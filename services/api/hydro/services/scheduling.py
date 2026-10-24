"""Scheduling governance. All writes are authenticated PostgreSQL transactions."""

import hashlib
import json
import re
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from starlette.responses import Response

from ..auth import Auth
from ..db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from ..errors import require
from ..events import record
from ..repository import insert as legacy_insert
from ..scheduling_contracts import DESIGN, validator
from ..security import now
from ..tenant import Tenant

TABLES = {
    "dispatch_technician_profiles",
    "dispatch_shifts",
    "dispatch_allocations",
    "dispatch_policy",
    "appointment_windows",
    "appointment_requests",
    "appointments",
}
JSON_FIELDS = {
    "skill_codes",
    "service_area_codes",
    "allowed_duration_minutes",
    "category_codes",
    "reviewed_expectations",
}


def write(c, table, identifier=None, **values):
    assert table in TABLES and all(re.fullmatch(r"[a-z_]+", k) for k in values)
    expressions = {k: f"CAST(:{k} AS jsonb)" if k in JSON_FIELDS else f":{k}" for k in values}
    params = {k: json.dumps(v) if k in JSON_FIELDS else v for k, v in values.items()}
    if identifier is None:
        sql = f"INSERT INTO {table} ({','.join(values)}) VALUES ({','.join(expressions.values())}) RETURNING *"
    else:
        sql = (
            f"UPDATE {table} SET "
            + ",".join(k + "=" + v for k, v in expressions.items())
            + ",version=version+1,updated_at=now() WHERE id=:identifier RETURNING *"
        )
        params["identifier"] = identifier
    return one(c, sql, **params)


def instant(value):
    try:
        result = (
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            if isinstance(value, str)
            else value
        )
        require(
            isinstance(result, datetime) and result.tzinfo is not None,
            422,
            "INVALID_TIME",
            "Use a timestamp with an explicit UTC offset",
        )
        return result
    except (TypeError, ValueError):
        require(False, 422, "INVALID_TIME", "Use a valid timestamp with an explicit UTC offset")


def interval(value):
    start, end = instant(value["start_at"]), instant(value["end_at"])
    require(
        start < end and end - start <= timedelta(hours=24),
        422,
        "INVALID_INTERVAL",
        "A finite positive interval of at most 24 hours is required",
    )
    return start, end


def version(actual, expected):
    require(
        actual == expected,
        412,
        "VERSION_CONFLICT",
        "Scheduling state changed; refresh before retrying",
    )


class Scheduler:
    def __init__(self, scope):
        self.s, self.c, self.o = scope, scope.c, scope.organization_id
        self.result = None

    def row(self, table, identifier):
        assert table in TABLES
        row = one(
            self.c,
            f"SELECT * FROM {table} WHERE organization_id=:o AND id=:i",
            o=self.o,
            i=identifier,
        )
        require(row, 404, "NOT_FOUND", "Resource unavailable")
        return row

    def profile(self, member):
        row = one(
            self.c,
            "SELECT * FROM dispatch_technician_profiles WHERE organization_id=:o AND membership_id=:m",
            o=self.o,
            m=member,
        )
        require(row, 404, "NOT_FOUND", "Scheduling profile unavailable")
        return row

    def policy(self):
        return one(self.c, "SELECT * FROM dispatch_policy WHERE organization_id=:o", o=self.o)

    def bump(self, profile):
        return write(
            self.c,
            "dispatch_technician_profiles",
            profile["id"],
            calendar_version=profile["calendar_version"] + 1,
        )

    def eligible(self, profile):
        member = self.s.row("organization_memberships", profile["membership_id"])
        role = one(
            self.c,
            "SELECT a.id FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL AND r.code='TECHNICIAN' FOR SHARE OF a",
            m=member["id"],
        )
        require(
            profile["active"] and member["status"] == "ACTIVE" and role,
            409,
            "TECHNICIAN_UNAVAILABLE",
            "Current active technician enrollment is required",
        )

    def projection(self, table, row):
        if table == "dispatch_policy":
            keys = DESIGN["components"]["schemas"]["M07DispatchPolicy"]["required"]
            return {k: row[k] for k in keys}
        if table == "dispatch_technician_profiles":
            return {
                "membership_id": row["membership_id"],
                "display_name": "Technician " + str(row["membership_id"])[:8],
                "enrollment_state": "ENROLLED",
                "active": row["active"],
                "skill_codes": row["skill_codes"],
                "service_area_codes": row["service_area_codes"],
                "max_daily_minutes": row["max_daily_minutes"],
                "profile_version": row["version"],
                "calendar_version": row["calendar_version"],
                "scheduling_health": "UNCONFIGURED"
                if not self.policy()["configured"]
                else "REVIEW_REQUIRED",
            }
        profile = self.row("dispatch_technician_profiles", row["profile_id"])
        result = {
            "id": row["id"],
            "technician_membership_id": profile["membership_id"],
            "version": row["version"],
            "calendar_version": profile["calendar_version"],
        }
        if table == "dispatch_shifts":
            return {
                **result,
                "interval": {"start_at": row["starts_at"], "end_at": row["ends_at"]},
                "status": row["status"],
            }
        return {
            **result,
            "interval": {
                "start_at": row["occupied_range"].lower,
                "end_at": row["occupied_range"].upper,
            },
            "kind": row["kind"],
            "work_order_id": row["work_order_id"],
        }

    def save(self, table, row, reason):
        self.result = row
        record(
            self.c,
            self.o,
            self.s.member_id,
            self.s.op["id"],
            table,
            row["id"],
            self.s.auth.request.state.request_id,
            self.s.op["permission"],
            reason,
        )
        return self.projection(table, row)

    def run(self, body, parent, key):
        s, c, b, op = self.s, self.c, body, self.s.op["id"]
        if op == "m07_n38":
            return self.projection("dispatch_policy", self.policy())
        if op == "m07_n25":
            require(
                not s.auth.request.query_params,
                422,
                "INVALID_FILTER",
                "Roster filters are not yet activated",
            )
            rows = query(
                c,
                "SELECT * FROM dispatch_technician_profiles WHERE organization_id=:o ORDER BY id LIMIT 101",
                o=self.o,
            )
            require(len(rows) <= 100, 409, "NARROW_QUERY", "Roster requires pagination")
            return {
                "items": [self.projection("dispatch_technician_profiles", r) for r in rows],
                "next_cursor": None,
                "as_of": now(),
            }
        if op == "m07_n26":
            member = s.row("organization_memberships", b["membership_id"], True)
            version(member["version"], b["expected_membership_version"])
            subject = one(c, "SELECT hydro_dispatch_enroll(:m,:r) AS id", m=member["id"], r=key)[
                "id"
            ]
            row = write(
                c,
                "dispatch_technician_profiles",
                organization_id=self.o,
                membership_id=member["id"],
                subject_id=subject,
                **{k: b[k] for k in ("skill_codes", "service_area_codes", "max_daily_minutes")},
            )
            return self.save("dispatch_technician_profiles", row, b["reason"])
        if op == "m07_n27":
            require(
                b["max_daily_minutes"] >= parent["max_daily_minutes"]
                or not one(
                    c,
                    "SELECT hydro_dispatch_has_commitments(:m) AS busy",
                    m=parent["membership_id"],
                )["busy"],
                409,
                "REPLAN_REQUIRED",
                "Replan active visits before lowering technician capacity",
            )
            row = write(
                c,
                "dispatch_technician_profiles",
                parent["id"],
                **{
                    k: b[k]
                    for k in ("skill_codes", "service_area_codes", "max_daily_minutes", "active")
                },
                calendar_version=parent["calendar_version"] + 1,
                reviewed_at=now(),
            )
            return self.save("dispatch_technician_profiles", row, b["reason"])
        if op == "m07_n39":
            row = write(c, "dispatch_policy", parent["id"], configured=True, **b)
            return self.save("dispatch_policy", row, b["reason"])
        profile = (
            parent
            if op in {"m07_n29", "m07_n31"}
            else self.row("dispatch_technician_profiles", parent["profile_id"])
        )
        version(profile["calendar_version"], b["expected_calendar_version"])
        if op in {"m07_n29", "m07_n31", "m07_n33"}:
            self.eligible(profile)
        if op in {"m07_n29", "m07_n30"}:
            start, end = interval(b["interval"])
            if op == "m07_n30":
                invalid = one(
                    c,
                    "SELECT id FROM dispatch_allocations WHERE profile_id=:p AND active AND occupied_range && tstzrange(:oldstart,:oldend,'[)') AND (:withdraw OR NOT occupied_range <@ tstzrange(:start,:end,'[)')) LIMIT 1",
                    p=profile["id"],
                    oldstart=parent["starts_at"],
                    oldend=parent["ends_at"],
                    withdraw=b["status"] == "WITHDRAWN",
                    start=start,
                    end=end,
                )
                require(
                    not invalid,
                    409,
                    "ALLOCATION_CONFLICT",
                    "Replan active allocations before changing the shift",
                )
            row = write(
                c,
                "dispatch_shifts",
                parent["id"] if op == "m07_n30" else None,
                organization_id=self.o,
                profile_id=profile["id"],
                starts_at=start,
                ends_at=end,
                status=b.get("status", "ACTIVE"),
                reason=b["reason"],
            )
            self.bump(profile)
            return self.save("dispatch_shifts", row, b["reason"])
        require(op in {"m07_n31", "m07_n32", "m07_n33"}, 404, "NOT_FOUND", "Operation unavailable")
        work_id = b.get("work_order_id") if op == "m07_n31" else parent["work_order_id"]
        if work_id:
            work = s.work(work_id, True)
            version(work["version"], b["expected_work_version"])
            require(
                work["assignee_id"] == profile["membership_id"]
                and work["status"] not in {"COMPLETED", "CANCELLED"},
                409,
                "ASSIGNMENT_CHANGED",
                "Current assigned work is required",
            )
        else:
            require(
                b.get("expected_work_version") is None,
                422,
                "INVALID_BODY",
                "No work version is applicable",
            )
        if op != "m07_n31":
            require(
                parent["active"] and parent["kind"] != "APPOINTMENT",
                409,
                "INVALID_STATE",
                "An active non-appointment block is required",
            )
            row = write(c, "dispatch_allocations", parent["id"], active=False, released_at=now())
        if op != "m07_n32":
            from psycopg.types.range import Range

            start, end = interval(b["interval"])
            kind = b["kind"] if op == "m07_n31" else parent["kind"]
            if kind == "WORK_BLOCK":
                require(
                    self.policy()["configured"],
                    409,
                    "SCHEDULING_DISABLED",
                    "Configure authorized capacity before planning work blocks",
                )
                self.capacity(profile, start, end)
                require(
                    one(
                        c,
                        "SELECT id FROM dispatch_shifts WHERE profile_id=:p AND status='ACTIVE' AND starts_at<=:s AND ends_at>=:e",
                        p=profile["id"],
                        s=start,
                        e=end,
                    ),
                    409,
                    "OUTSIDE_SHIFT",
                    "Work must fit an authorized shift",
                )
            row = write(
                c,
                "dispatch_allocations",
                organization_id=self.o,
                profile_id=profile["id"],
                subject_id=profile["subject_id"],
                work_order_id=work_id,
                kind=kind,
                occupied_range=Range(start, end, "[)"),
                reason=b.get("internal_reason", b.get("reason")),
            )
        self.bump(profile)
        return self.save("dispatch_allocations", row, b.get("internal_reason", b.get("reason")))


def dispatch(app, request, op, value, params):
    response = Response()
    spec = DESIGN["paths"][op["path"]][op["method"]]
    status = min(int(k) for k in spec["responses"] if str(k).startswith("2"))
    with app.state.engine.begin() as c:
        require(
            principal_is_safe(c),
            503,
            "UNSAFE_DATABASE_PRINCIPAL",
            "Runtime database identity is not safe",
        )
        require(
            one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
            503,
            "MIGRATION_REQUIRED",
            "Database migration required",
        )
        auth = Auth(c, request, response, app)
        auth.identify()
        auth.authenticated()
        if op["method"] != "get":
            auth.csrf()
        for name, raw in params.items():
            try:
                params[name] = str(UUID(raw))
            except ValueError:
                require(False, 422, "INVALID_IDENTIFIER", "Invalid resource identifier")
        execute(
            c,
            "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
            key="hydro-dispatch:" + params["organization_id"],
        )
        s = Tenant(auth, op, params)
        from .bookings import Bookings

        service = Bookings(s)
        schema = (
            spec.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
            .get("$ref")
        )
        require(
            not list(validator(schema.rsplit("/", 1)[1]).iter_errors(value))
            if schema
            else value is None,
            422,
            "INVALID_BODY",
            "Body does not match operation contract",
        )
        b = value or {}
        auth.app.state.limits.hit("m07b-operation", str(s.member_id), 100, 60)
        parent = None
        if op["id"] in {"m07_n26", "m07_n27", "m07_n39"}:
            require(
                auth.session["reauthenticated_at"]
                and (now() - auth.session["reauthenticated_at"]).total_seconds() <= 600,
                403,
                "REAUTHENTICATE",
                "Authenticate again before governance changes",
            )
        if op["id"] in {"m07_n27", "m07_n29", "m07_n31", "m07_n35"}:
            parent = service.profile(params.get("membership_id") or b["technician_membership_id"])
        elif op["id"] == "m07_n30":
            parent = service.row("dispatch_shifts", params["shift_id"])
        elif op["id"] in {"m07_n32", "m07_n33"}:
            parent = service.row("dispatch_allocations", params["block_id"])
        elif op["id"] == "m07_n39":
            parent = service.policy()
        elif "request_id" in params:
            parent = service.case(params["request_id"])
        elif "appointment_request_id" in params:
            parent = service.row("appointment_requests", params["appointment_request_id"])
            service.case(parent["request_id"])
        elif "appointment_id" in params:
            parent = service.appointment(params["appointment_id"])
        elif "window_id" in params:
            parent = service.row("appointment_windows", params["window_id"])
        elif "membership_id" in params:
            parent = service.profile(params["membership_id"])
        if op["method"] == "get":
            result = service.run(b, parent, None)
        else:
            try:
                key = UUID(request.headers.get("idempotency-key", ""))
            except ValueError:
                require(False, 400, "IDEMPOTENCY_REQUIRED", "A UUID Idempotency-Key is required")
            fingerprint = hashlib.sha256(
                json.dumps({"body": b, "path": params}, sort_keys=True).encode()
            ).hexdigest()
            execute(c, "SELECT hydro_expire_receipts()")
            prior = one(
                c,
                "SELECT * FROM idempotency_records WHERE organization_id=:o AND actor_scope=:a AND method=:m AND route_template=:r AND operation_key=:k",
                o=s.organization_id,
                a=str(s.member_id),
                m=op["method"],
                r=op["path"],
                k=key,
            )
            table = service.result_table(op["id"])
            if prior:
                require(
                    prior["request_hash"] == fingerprint,
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    "Key was used with different content",
                )
                result = service.replay(
                    table, service.row(table, prior["result_resource_id"]), prior, b
                )
            else:
                if spec.get("x-version-target"):
                    s.version(parent)
                result = service.run(b, parent, key)
                legacy_insert(
                    c,
                    "idempotency_records",
                    organization_id=s.organization_id,
                    actor_scope=str(s.member_id),
                    operation_key=key,
                    method=op["method"],
                    route_template=op["path"],
                    request_hash=fingerprint,
                    result_resource_id=service.result["id"],
                    result_status=status,
                    expires_at=now() + timedelta(days=7),
                )
        wire = jsonable_encoder(
            result,
            custom_encoder={
                datetime: lambda d: d.astimezone(UTC).isoformat().replace("+00:00", "Z")
            },
        )
        response_schema = spec["responses"][str(status)]["content"]["application/json"]["schema"][
            "$ref"
        ].rsplit("/", 1)[1]
        if spec.get("x-role-projections"):
            role = (
                "SUPERVISOR"
                if "SUPERVISOR" in s.roles
                else "TECHNICIAN"
                if "TECHNICIAN" in s.roles and op["id"] in {"m07_n22", "m07_n24", "m07_n28"}
                else "CITIZEN"
            )
            response_schema = spec["x-role-projections"][role]
        require(
            not list(validator(response_schema).iter_errors(wire)),
            500,
            "RESPONSE_CONTRACT",
            "Server projection failed contract validation",
        )
        if "version" in result or "profile_version" in result:
            response.headers["ETag"] = (
                '"' + str(result.get("version", result.get("profile_version"))) + '"'
            )
    return wire, status, response
