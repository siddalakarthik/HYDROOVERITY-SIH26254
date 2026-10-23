"""M02 wire conformance. No unimplemented catalogue routes are registered."""

import json
from functools import lru_cache

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
from referencing import Registry, Resource

from . import inputs
from .config import ROOT
from .errors import require

DESIGN = json.loads((ROOT / "docs/architecture/openapi-design.json").read_text())
INVENTORY = json.loads((ROOT / "data/schemas/m02-api-inventory.json").read_text())["operations"]
GROUPS = {
    "Authentication",
    "Current user",
    "Incidents",
    "Work orders",
    "Repairs",
    "Verification",
    "Complaints",
    "Evidence",
}


def implemented(op):
    path = op["path"]
    return (
        op["group"] in GROUPS
        or (op["group"] == "Water zones" and "/zones" in path)
        or (op["group"] == "Pipeline assets" and any(x in path for x in ("/junctions", "/pipes")))
        or path in {"/public/utilities/{slug}", "/public/project-status"}
        or (op["group"] == "Organization" and op["method"] == "get")
        or (
            op["group"] == "Administration"
            and any(x in path for x in ("/memberships", "/invitations", "/audit-logs"))
        )
    )


OPERATIONS = [op for op in INVENTORY if implemented(op)]
REGISTRY = Registry().with_resource(
    "urn:hydro:design",
    Resource.from_contents(
        DESIGN,
        default_specification=__import__(
            "referencing.jsonschema", fromlist=["DRAFT202012"]
        ).DRAFT202012,
    ),
)


@lru_cache
def validator(name):
    return Draft202012Validator(
        {"$ref": "urn:hydro:design#/components/schemas/" + name},
        registry=REGISTRY,
        format_checker=FormatChecker(),
    )


def body(name, value):
    check = validator(name)
    if name == "WorkOrderWrite" and isinstance(value, dict) and "task_purpose" in value:
        from .service_contracts import validator as service_validator

        check = service_validator("M07FutureWorkOrderWrite")
    require(
        not list(check.iter_errors(value)),
        422,
        "INVALID_BODY",
        "Body does not match the operation contract",
    )
    try:
        return (
            getattr(inputs, name)
            .model_validate_json(json.dumps(value, allow_nan=False))
            .model_dump(mode="json", exclude_unset=name == "WorkOrderWrite")
        )
    except (ValidationError, ValueError, TypeError):
        require(False, 422, "INVALID_BODY", "Body does not match the operation contract")


def runtime_openapi():
    result = {k: v for k, v in DESIGN.items() if k != "paths"}
    result["info"] = {**DESIGN["info"], "title": "HYDROOVERITY implemented M03 API"}
    result["paths"] = {}
    for op in OPERATIONS:
        result["paths"].setdefault(op["path"], {})[op["method"]] = DESIGN["paths"][op["path"]][
            op["method"]
        ]
    # Unreachable future scientific/evaluation schemas are not advertised by
    # the implementation document. Canonical design remains complete.
    pending = [result["paths"]]
    found = set()
    components = {}
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            reference = value.get("$ref", "")
            if reference.startswith("#/components/") and reference not in found:
                found.add(reference)
                _, _, kind, name = reference.split("/")
                target = DESIGN["components"][kind][name]
                components.setdefault(kind, {})[name] = target
                pending.append(target)
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    components["securitySchemes"] = {
        "sessionCookie": DESIGN["components"]["securitySchemes"]["sessionCookie"]
    }
    result["components"] = components
    from .service_contracts import extend_openapi

    return extend_openapi(result)
