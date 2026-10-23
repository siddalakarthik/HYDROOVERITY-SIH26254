"""Explicit M07-A activation; the full proposed catalogue never registers routes."""

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
ACTIVE = {f"m07_n{i:02}" for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 43, 44]}
DISABLED = {"m07_n10", "m07_n11", "m07_n12"}
OPERATIONS = []
for path, methods in DESIGN["paths"].items():
    for method, spec in methods.items():
        if spec.get("operationId") not in ACTIVE | DISABLED:
            continue
        OPERATIONS.append(
            {
                "id": spec["operationId"],
                "path": path,
                "method": method,
                "group": "M07-A",
                "roles": spec["x-roles"],
                "permission": spec["x-required-permission"],
            }
        )
REGISTRY = Registry().with_resource(
    "urn:hydro:m07", Resource.from_contents(DESIGN, default_specification=DRAFT202012)
)


@lru_cache
def validator(name):
    return Draft202012Validator(
        {"$ref": "urn:hydro:m07#/components/schemas/" + name},
        registry=REGISTRY,
        format_checker=FormatChecker(),
    )


def extend_openapi(result):
    result = copy.deepcopy(result)
    # Activate the explicitly staged optional input; existing response definitions stay unchanged.
    work = result["paths"]["/orgs/{organization_id}/work-orders"]["post"]
    work["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/M07FutureWorkOrderWrite"
    }
    result["components"]["schemas"].update(
        {
            k: v
            for k, v in DESIGN["components"]["schemas"].items()
            if k in {"M07FutureWorkOrderWrite", "M07TaskPurpose"}
        }
    )
    for op in OPERATIONS:
        if op["id"] not in ACTIVE:
            continue
        spec = copy.deepcopy(DESIGN["paths"][op["path"]][op["method"]])
        spec["x-implementation-status"] = "IMPLEMENTED_M07_A"
        spec["summary"] = spec["summary"].replace("— proposed only", "— M07-A")
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
    result["info"]["title"] = "HYDROOVERITY implemented M03 + M07-A API"
    return result
