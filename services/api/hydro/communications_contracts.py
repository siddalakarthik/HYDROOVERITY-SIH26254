"""Explicit M07-C activation overlay; media and privacy gates remain closed."""

import copy
import json
from functools import lru_cache

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .config import ROOT

DESIGN = json.loads(
    (ROOT / "docs/architecture/m07/openapi-proposed.json").read_text(encoding="utf-8")
)
SCHEMAS = DESIGN["components"]["schemas"]
# Additive private-development preference; existing opt-ins are never expanded.
for schema_name in ("M07NotificationPreferences", "M07NotificationPreferencesWrite"):
    categories = SCHEMAS[schema_name]["properties"]["event_categories"]
    categories["items"]["enum"].append("COMPLAINT_PROGRESS")
    categories["maxItems"] = 5
SCHEMAS["M07Notification"]["properties"].update(
    {
        "event_category": {
            "type": "string",
            "enum": [
                "SERVICE_PROGRESS",
                "APPOINTMENT",
                "WORK_ASSIGNMENT",
                "SERVICE_FEEDBACK",
                "COMPLAINT_PROGRESS",
            ],
        },
        "resource_path": {"type": "string", "maxLength": 300, "pattern": "^/"},
    }
)
SCHEMAS["M07Notification"]["required"] += ["event_category", "resource_path"]
SCHEMAS["M07Feedback"]["properties"]["description"] = {"type": "string", "maxLength": 2000}
SCHEMAS["M07Feedback"]["required"].append("description")
OPERATIONS = []
for path, methods in DESIGN["paths"].items():
    for method, spec in methods.items():
        if (
            spec.get("operationId") in {"m07_n40", "m07_n41", "m07_n42"}
            or path.endswith("/feedback")
            or "/feedback/{feedback_id}/review" in path
            or path.endswith("/notifications")
            or "/notifications/{notification_id}/read" in path
        ):
            OPERATIONS.append(
                {
                    "id": spec["operationId"],
                    "path": path,
                    "method": method,
                    "group": "M07-C",
                    "roles": spec["x-roles"],
                    "permission": spec["x-required-permission"],
                }
            )
            spec["x-implementation-status"] = "IMPLEMENTED_M07_C"

REGISTRY = Registry().with_resource(
    "urn:hydro:m07c", Resource.from_contents(DESIGN, default_specification=DRAFT202012)
)


@lru_cache
def validator(name):
    return Draft202012Validator(
        {"$ref": "urn:hydro:m07c#/components/schemas/" + name},
        registry=REGISTRY,
        format_checker=FormatChecker(),
    )


def extend_openapi(result):
    result = copy.deepcopy(result)
    for op in OPERATIONS:
        result["paths"].setdefault(op["path"], {})[op["method"]] = copy.deepcopy(
            DESIGN["paths"][op["path"]][op["method"]]
        )
    pending = [result["paths"]]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            ref = node.get("$ref", "")
            if ref.startswith("#/components/"):
                _, _, kind, name = ref.split("/")
                bucket = result["components"].setdefault(kind, {})
                if name not in bucket:
                    bucket[name] = copy.deepcopy(DESIGN["components"][kind][name])
                    pending.append(bucket[name])
            pending.extend(v for k, v in node.items() if k != "$ref")
        elif isinstance(node, list):
            pending.extend(node)
    result["info"]["title"] = "HYDROOVERITY implemented API through M07-C"
    return result
