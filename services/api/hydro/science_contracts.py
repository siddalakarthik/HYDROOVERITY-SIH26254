"""Bounded M06 replay contracts, separate from deferred M02 execution jobs."""

import copy
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import JsonValue

from .science_data import Case, Strict


class Provenance(Strict):
    source_category: Literal["SIMULATION"]
    label: Literal["SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED"]


class Scenario(Strict):
    code: str
    name: str
    module: Literal["HYDRO-WATCH", "GUARD-5", "HYDRO-EAR", "HYDRO-VERIFY"]


class Catalogue(Provenance):
    catalogue_hash: str
    items: list[Scenario]


class Replay(Provenance):
    id: UUID
    created_at: datetime
    status: Literal["IMPORTED"]
    scenario_code: str
    name: str
    module: str
    content_hash: str
    catalogue_hash: str
    configuration_hash: str
    algorithm_source_hash: str
    algorithm_version: Literal["M05-2"]
    limitations: list[str]


class Snapshot(Provenance):
    algorithm_version: Literal["M05-2"]
    configuration_hash: str
    algorithm_source_hash: str
    reference_summary_hash: str
    # Exact historical content is digest-pinned; not writable client JSON.
    historical_benchmark: dict[str, JsonValue]
    case: Case


class Detail(Replay):
    snapshot: Snapshot


class ReplayList(Provenance):
    items: list[Replay]
    next_offset: int | None


class Frame(Provenance):
    sequence: int
    time_s: float
    module: str
    # Explicit server-side projection from the strictly validated Case model.
    values: dict[str, JsonValue]


class Frames(Replay):
    items: list[Frame]
    total_frames: int
    next_offset: int | None


RESPONSES = {
    "m06_catalogue": Catalogue,
    "m06_import": Replay,
    "m06_list": ReplayList,
    "m06_detail": Detail,
    "m06_export": Detail,
    "m06_replay": Frames,
    "m06_stream": Frames,
}

BASE = "/orgs/{organization_id}/scientific-replays"
OPERATIONS = [
    {
        "id": "m06_" + name,
        "path": BASE + suffix,
        "method": method,
        "roles": ["ENGINEER"],
        "permission": "simulations." + ("write" if method == "post" else "read"),
        "group": "M06",
    }
    for name, suffix, method in (
        ("catalogue", "/catalogue", "get"),
        ("import", "", "post"),
        ("list", "", "get"),
        ("detail", "/{run_id}", "get"),
        ("replay", "/{run_id}/frames", "get"),
        ("export", "/{run_id}/export", "get"),
        ("stream", "/{run_id}/events", "get"),
    )
]


def extend_openapi(result):
    result = copy.deepcopy(result)
    for model in dict.fromkeys(RESPONSES.values()):
        schema = model.model_json_schema(ref_template="#/components/schemas/M06{model}")
        definitions = schema.pop("$defs", {})
        result["components"]["schemas"].update({"M06" + k: v for k, v in definitions.items()})
        result["components"]["schemas"]["M06" + model.__name__] = schema
    for op in OPERATIONS:
        params = [
            {
                "name": "organization_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if "{run_id}" in op["path"]:
            params.append(
                {
                    "name": "run_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
        if op["id"] in {"m06_replay", "m06_stream", "m06_list"}:
            is_list = op["id"] == "m06_list"
            params.extend(
                [
                    {
                        "name": "offset",
                        "in": "query",
                        "schema": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100000 if is_list else 8192,
                            "default": 0,
                        },
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100 if is_list else 200,
                            "default": 25 if is_list else 100,
                        },
                    },
                ]
            )
        spec = {
            "operationId": op["id"],
            "summary": "SIMULATION ONLY — " + op["id"],
            "x-roles": op["roles"],
            "x-required-permission": op["permission"],
            "x-implementation-status": "IMPLEMENTED_M06",
            "security": [{"sessionCookie": []}],
            "parameters": params,
            "responses": {
                "200": {
                    "description": "Authorized observation-only replay",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/M06" + RESPONSES[op["id"]].__name__
                            }
                        }
                    },
                }
            },
        }
        if op["id"] == "m06_stream":
            spec["responses"]["200"]["content"] = {
                "text/event-stream": {"schema": {"type": "string"}}
            }
            spec["description"] = (
                "Bounded SSE batch: provenance, observation events, then checkpoint. Resume with next_offset; every batch reauthorizes current membership. Not a live sensor feed."
            )
        if op["method"] == "post":
            spec["parameters"].append(
                {
                    "name": "Idempotency-Key",
                    "in": "header",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            )
            spec["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["scenario_code"],
                            "properties": {
                                "scenario_code": {"type": "string", "minLength": 3, "maxLength": 80}
                            },
                        }
                    }
                },
            }
        result["paths"].setdefault(op["path"], {})[op["method"]] = spec
    return result
