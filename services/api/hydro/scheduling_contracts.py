"""Explicit incremental activation of approved M07-B operations."""

import copy
from functools import lru_cache

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .service_contracts import DESIGN as CANDIDATE

DESIGN = copy.deepcopy(CANDIDATE)
# An eligible but unenrolled member has no approved skills/areas yet.
# The candidate's unconditional minItems=1 contradicted its ELIGIBLE projection.
for field in ("skill_codes", "service_area_codes"):
    DESIGN["components"]["schemas"]["M07DispatchTechnician"]["properties"][field]["minItems"] = 0
DESIGN["components"]["schemas"]["M07DispatchTechnician"]["allOf"] = [
    {
        "if": {
            "properties": {"enrollment_state": {"const": "ENROLLED"}},
            "required": ["enrollment_state"],
        },
        "then": {
            "properties": {"skill_codes": {"minItems": 1}, "service_area_codes": {"minItems": 1}}
        },
    }
]
ACTIVE = {f"m07_n{i:02}" for i in range(14, 40)}
OPERATIONS = [
    {
        "id": s["operationId"],
        "path": p,
        "method": m,
        "group": "M07-B",
        "roles": s["x-roles"],
        "permission": s["x-required-permission"],
    }
    for p, methods in DESIGN["paths"].items()
    for m, s in methods.items()
    if s.get("operationId") in ACTIVE
]
REGISTRY = Registry().with_resource(
    "urn:hydro:m07b", Resource.from_contents(DESIGN, default_specification=DRAFT202012)
)


@lru_cache
def validator(name):
    return Draft202012Validator(
        {"$ref": "urn:hydro:m07b#/components/schemas/" + name},
        registry=REGISTRY,
        format_checker=FormatChecker(),
    )


def extend_openapi(result):
    result = copy.deepcopy(result)
    for op in OPERATIONS:
        spec = copy.deepcopy(DESIGN["paths"][op["path"]][op["method"]])
        spec["x-implementation-status"] = "IMPLEMENTED_M07_B"
        spec["summary"] = spec["summary"].replace("— proposed only", "— M07-B")
        result["paths"].setdefault(op["path"], {})[op["method"]] = spec
    pending = [result["paths"], result["components"]]
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
    return result
