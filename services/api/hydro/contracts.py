"""M02 wire conformance. No unimplemented catalogue routes are registered."""
import json
from functools import lru_cache

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
from referencing import Registry, Resource

from . import inputs
from .config import ROOT
from .errors import require

DESIGN=json.loads((ROOT/"docs/architecture/openapi-design.json").read_text())
INVENTORY=json.loads((ROOT/"data/schemas/m02-api-inventory.json").read_text())["operations"]
GROUPS={"Authentication","Current user","Water zones","Incidents","Work orders",
        "Repairs","Verification","Complaints","Evidence"}


def implemented(op):
    path=op["path"]
    return (op["group"] in GROUPS or
            (op["group"]=="Pipeline assets" and any(x in path for x in ("/junctions","/pipes"))) or
            path in {"/public/utilities/{slug}","/public/project-status"} or
            (op["group"]=="Organization" and op["method"]=="get") or
            (op["group"]=="Administration" and any(x in path for x in
             ("/memberships","/invitations","/audit-logs"))))


OPERATIONS=[op for op in INVENTORY if implemented(op)]
REGISTRY=Registry().with_resource("urn:hydro:design",Resource.from_contents(DESIGN,
                         default_specification=__import__('referencing.jsonschema',fromlist=['DRAFT202012']).DRAFT202012))


@lru_cache
def validator(name):
    return Draft202012Validator({"$ref":"urn:hydro:design#/components/schemas/"+name},
                               registry=REGISTRY,format_checker=FormatChecker())


def body(name, value):
    require(not list(validator(name).iter_errors(value)),422,"INVALID_BODY","Body does not match the operation contract")
    try:
        return getattr(inputs,name).model_validate_json(json.dumps(value,allow_nan=False)).model_dump(mode="json")
    except (ValidationError,ValueError,TypeError):
        require(False,422,"INVALID_BODY","Body does not match the operation contract")


def runtime_openapi():
    result={k:v for k,v in DESIGN.items() if k!="paths"}
    result["info"]={**DESIGN["info"],"title":"HYDROOVERITY implemented M03 API"}
    result["paths"]={}
    for op in OPERATIONS:
        result["paths"].setdefault(op["path"],{})[op["method"]]=DESIGN["paths"][op["path"]][op["method"]]
    return result
