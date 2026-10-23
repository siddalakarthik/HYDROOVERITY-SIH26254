"""Authorized synchronous snapshot ingestion and deterministic observation replay."""

import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from ..auth import Auth
from ..db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from ..errors import require
from ..science_contracts import RESPONSES
from ..science_data import LABEL, digest, load_catalogue
from ..tenant import Tenant


def catalogue(app):
    settings = app.state.settings
    require(
        settings.science_catalogue_path and settings.science_catalogue_sha256,
        503,
        "SCIENCE_CATALOGUE_REQUIRED",
        "A verified observation catalogue has not been configured",
    )
    try:
        return load_catalogue(settings.science_catalogue_path, settings.science_catalogue_sha256)
    except (ValueError, OSError, KeyError, TypeError):
        require(
            False,
            503,
            "SCIENCE_CATALOGUE_INVALID",
            "The observation catalogue failed integrity validation",
        )


def view(row):
    snapshot = row["snapshot"]
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "source_category": "SIMULATION",
        "label": LABEL,
        "status": "IMPORTED",
        "scenario_code": row["scenario_code"],
        "name": snapshot["case"]["name"],
        "module": snapshot["case"]["data"]["module"],
        "content_hash": row["content_hash"],
        "catalogue_hash": row["catalogue_hash"],
        "configuration_hash": snapshot["configuration_hash"],
        "algorithm_source_hash": snapshot["algorithm_source_hash"],
        "algorithm_version": "M05-2",
        "limitations": snapshot["case"]["data"]["limitations"],
    }


def frames(data):
    if data["module"] == "HYDRO-VERIFY":
        data = data["watch"]
    for i, time_s in enumerate(data["time_s"]):
        if data["module"] == "HYDRO-WATCH":
            values = {
                key: data[key][i]
                for key in (
                    "pressure_bar",
                    "inlet_lpm",
                    "customer_outlet_lpm",
                    "pump_on",
                    "storage_known",
                    "solver_valid",
                    "state",
                    "qualified_outcome",
                    "fixed_alarm",
                    "watch_alarm",
                    "residual_lpm",
                )
            }
        elif data["module"] == "GUARD-5":
            values = {"wet": data["wet"][i], "health": data["health"], "channels": data["channels"]}
        else:
            values = {
                "paired_samples": [row[i] for row in data["waveforms"]],
                "shared_clock": data["shared_clock"],
                "preview_stride": data["preview_stride"],
            }
        yield {
            "sequence": i,
            "time_s": time_s,
            "module": data["module"],
            "source_category": "SIMULATION",
            "label": LABEL,
            "values": values,
        }


def page_number(request, name, default, maximum):
    raw = request.query_params.get(name, str(default))
    require(
        raw.isascii() and raw.isdecimal() and len(raw) <= 6,
        422,
        "INVALID_FILTER",
        "Replay pagination must be bounded nonnegative integers",
    )
    value = int(raw)
    require(
        value <= maximum and (name != "limit" or value > 0),
        422,
        "INVALID_FILTER",
        "Replay pagination is outside its bounds",
    )
    return value


def dispatch(app, request, op, value, params):
    response = Response()
    with app.state.engine.begin() as c:
        require(principal_is_safe(c), 503, "UNSAFE_DATABASE_PRINCIPAL", "Unsafe runtime identity")
        require(
            one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
            503,
            "MIGRATION_REQUIRED",
            "Database migration is required",
        )
        auth = Auth(c, request, response, app)
        auth.identify()
        auth.authenticated()
        for name, raw in params.items():
            try:
                params[name] = str(UUID(raw))
            except ValueError:
                require(False, 422, "INVALID_IDENTIFIER", "Invalid identifier")
        scope = Tenant(auth, op, params)
        app.state.limits.hit("science", str(scope.member_id), 120, 60)
        identity = op["id"]
        if op["method"] == "post":
            auth.csrf()
            require(
                isinstance(value, dict)
                and set(value) == {"scenario_code"}
                and isinstance(value["scenario_code"], str)
                and 3 <= len(value["scenario_code"]) <= 80,
                422,
                "INVALID_BODY",
                "Select one supported scenario code",
            )
            try:
                key = UUID(request.headers.get("idempotency-key", ""))
            except ValueError:
                require(False, 400, "IDEMPOTENCY_REQUIRED", "A UUID Idempotency-Key is required")
            execute(
                c,
                "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
                key="m06:" + str(scope.organization_id) + str(scope.member_id) + str(key),
            )
            row = one(
                c,
                "SELECT * FROM scientific_replays WHERE organization_id=:o AND creator_id=:a AND operation_key=:k",
                o=scope.organization_id,
                a=scope.member_id,
                k=key,
            )
            if row:
                require(
                    row["scenario_code"] == value["scenario_code"],
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    "Key already used for a different scenario",
                )
            else:
                source = catalogue(app)
                case = next(
                    (v for v in source["cases"] if v["code"] == value["scenario_code"]), None
                )
                require(case, 422, "UNKNOWN_SCENARIO", "Select a supported scenario")
                snapshot = {
                    k: source[k]
                    for k in (
                        "source_category",
                        "label",
                        "algorithm_version",
                        "configuration_hash",
                        "algorithm_source_hash",
                        "reference_summary_hash",
                        "historical_benchmark",
                    )
                }
                snapshot["case"] = case
                row = one(
                    c,
                    """INSERT INTO scientific_replays
                    (organization_id,creator_id,operation_key,scenario_code,catalogue_hash,content_hash,snapshot)
                    VALUES(:o,:a,:k,:s,:h,:d,CAST(:payload AS jsonb)) RETURNING *""",
                    o=scope.organization_id,
                    a=scope.member_id,
                    k=key,
                    s=case["code"],
                    h=digest(source),
                    d=digest(snapshot),
                    payload=json.dumps(snapshot, allow_nan=False),
                )
                execute(
                    c,
                    """INSERT INTO audit_logs(organization_id,actor_id,action,resource_type,
                    resource_id,request_id,safe_metadata,occurred_at)
                    VALUES(:o,:a,'SIMULATION_IMPORTED','scientific_replays',:i,:q,'{}',now())""",
                    o=scope.organization_id,
                    a=scope.member_id,
                    i=row["id"],
                    q=request.state.request_id,
                )
                execute(
                    c,
                    """INSERT INTO domain_events(organization_id,event_type,resource_type,
                    resource_id,workspace_mode,minimum_permission,occurred_at,safe_summary)
                    VALUES(:o,'SIMULATION_IMPORTED','scientific_replays',:i,'SIMULATION','simulations.read',now(),'{}')""",
                    o=scope.organization_id,
                    i=row["id"],
                )
            result = view(row)
        else:
            require(value is None, 422, "UNEXPECTED_BODY", "No request body is accepted")
            if identity == "m06_catalogue":
                source = catalogue(app)
                result = {
                    "source_category": "SIMULATION",
                    "label": LABEL,
                    "catalogue_hash": digest(source),
                    "items": [
                        {"code": v["code"], "name": v["name"], "module": v["data"]["module"]}
                        for v in source["cases"]
                    ],
                }
            elif identity == "m06_list":
                limit = page_number(request, "limit", 25, 100)
                offset = page_number(request, "offset", 0, 100000)
                rows = query(
                    c,
                    "SELECT * FROM scientific_replays WHERE organization_id=:o ORDER BY created_at DESC,id DESC LIMIT :n OFFSET :skip",
                    o=scope.organization_id,
                    n=limit + 1,
                    skip=offset,
                )
                result = {
                    "source_category": "SIMULATION",
                    "label": LABEL,
                    "items": [view(v) for v in rows[:limit]],
                    "next_offset": offset + limit if len(rows) > limit else None,
                }
            else:
                row = one(
                    c,
                    "SELECT * FROM scientific_replays WHERE organization_id=:o AND id=:i",
                    o=scope.organization_id,
                    i=params["run_id"],
                )
                require(row, 404, "NOT_FOUND", "Resource unavailable")
                require(
                    digest(row["snapshot"]) == row["content_hash"],
                    503,
                    "SCIENCE_INTEGRITY_FAILURE",
                    "Persisted observations failed integrity validation",
                )
                result = {**view(row), "snapshot": row["snapshot"]}
                if identity in {"m06_replay", "m06_stream"}:
                    offset = page_number(request, "offset", 0, 8192)
                    limit = page_number(request, "limit", 100, 200)
                    observations = list(frames(row["snapshot"]["case"]["data"]))
                    require(
                        offset <= len(observations),
                        422,
                        "INVALID_CURSOR",
                        "Replay offset exceeds recording",
                    )
                    end = min(offset + limit, len(observations))
                    result = {
                        **view(row),
                        "items": observations[offset:end],
                        "total_frames": len(observations),
                        "next_offset": end if end < len(observations) else None,
                    }
        wire = jsonable_encoder(
            result,
            custom_encoder={
                datetime: lambda d: d.astimezone(UTC).isoformat().replace("+00:00", "Z")
            },
        )
        RESPONSES[identity].model_validate_json(json.dumps(wire))
    return wire, 200, response
