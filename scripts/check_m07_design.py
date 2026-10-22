"""Validate proposed contracts and frozen compatibility, never runtime enforcement."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
METHODS = {"get", "post", "patch", "put", "delete", "head", "options", "trace"}
BASE = "fe69ccdb10ab515f73bbceaaa4652ce440859c85"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load():
    return tuple(read(p) for p in ["docs/architecture/m07/openapi-proposed.json", "data/schemas/m07-database-design.json", "data/schemas/m07-api-inventory.json", "data/schemas/m07-reconciliation-matrix.json", "design/ui-ux/m07-route-catalog.json", "data/schemas/m07-state-machines.json"])


def properties(spec, value, seen=None):
    seen = set() if seen is None else seen
    names = set()
    if isinstance(value, dict):
        names |= set(value.get("properties", {}))
        reference = value.get("$ref", "")
        if reference.startswith("#/components/schemas/") and reference not in seen:
            seen.add(reference)
            names |= properties(spec, spec["components"]["schemas"].get(reference.rsplit("/",1)[1], {}), seen)
        for k, item in value.items():
            if k != "$ref": names |= properties(spec, item, seen)
    elif isinstance(value, list):
        for item in value: names |= properties(spec, item, seen)
    return names


def validate(spec, db, inventory, matrix, routes, states):
    errors = []
    def require(condition, message):
        if not condition: errors.append(message)
    original = read("docs/architecture/openapi-design.json")
    old_inventory = read("data/schemas/m02-api-inventory.json")["operations"]
    deployed = read("data/schemas/m03-implementation-matrix.json")
    implemented = {op["id"] for op in deployed["operations"] if op["status"] == "CODE_TESTED"}
    entries = inventory["operations"]
    index = {op["id"]:op for op in entries}
    flat = {op["operationId"]:(method,path,op) for path,methods in spec["paths"].items() for method,op in methods.items() if method in METHODS}
    require(len(flat) == len(index) == len(entries) == 161, "Composed operation count/unique IDs drift")
    require(set(flat) == set(index), "Inventory operation set mismatch")
    require(spec.get("x-review-baseline") == matrix.get("baseline") == BASE, "Verified main baseline drift")
    new_ids = {f"m07_n{i:02d}" for i in range(1,45)}
    require(new_ids <= set(flat), "44 proposal IDs missing")
    require({op["id"] for op in matrix["operations"] if op["runtime_registered"]} == implemented, "Runtime registration claim drift")
    require(len(implemented) == 58 and len(deployed["operations"]) == 117, "Frozen M03 operation counts changed")
    require(matrix["counts"] == {"baseline_operations":117,"proposed_new_operations":44,"existing_deferred_selected":11,"composed_operations":161,"runtime_implemented_operations":58,"runtime_deferred_operations":59,"remaining_outside_m07":48,"baseline_design_tables":57,"proposed_new_tables":17,"composed_design_tables":74,"runtime_migrated_tables":30}, "Reconciliation counts drift")
    for old in old_inventory:
        if old["id"] in implemented:
            require(flat[old["id"]][2] == original["paths"][old["path"]][old["method"]], "Implemented operation contract changed: " + old["id"])
    for name,value in original["components"]["schemas"].items():
        require(spec["components"]["schemas"].get(name) == value, "Legacy reachable schema changed: " + name)
    selected = {op["id"] for op in old_inventory if op["group"] in {"Feedback","Uploads","Notifications"}}
    require(set(matrix["selected_deferred_ids"]) == selected and len(selected) == 11, "Eleven deferred operation selection drift")
    for oid in new_ids | selected:
        method,path,op = flat[oid]
        entry = index[oid]
        require(op.get("x-implementation-status") == entry.get("status") == "PROPOSED_NOT_IMPLEMENTED", "Proposed/implemented status drift: " + oid)
        require(op.get("security") == [{"sessionCookie":[]}], "Session security missing: " + oid)
        guards = set(op.get("x-authorization-guards", []))
        require("TENANT" in guards and "PUBLIC" not in op["x-roles"], "Tenant/anonymous access drift: " + oid)
        if "CITIZEN" in op["x-roles"]:
            require("CITIZEN_OWNED" in guards, "Citizen ownership missing: " + oid)
        if "TECHNICIAN" in op["x-roles"]:
            require(("TECHNICIAN_SELF" if oid == "m07_n28" else "TECHNICIAN_ASSIGNED") in guards, "Technician scope missing: " + oid)
        params = op.get("parameters", [])
        path_params = {p["name"] for p in params if p["in"] == "path" and p.get("required") is True}
        require(path_params == set(re.findall(r"{(.*?)}",path)), "Path parameters drift: " + oid)
        require(len(params) == len({(p["in"],p["name"]) for p in params}), "Duplicate parameter: " + oid)
        require({p["name"] for p in params if p["in"] == "query"} - {"limit","cursor"} == set(entry["filters"]), "Query filter inventory drift: " + oid)
        headers = {p["name"]:p for p in params if p["in"] == "header"}
        if method != "get":
            require(headers.get("X-CSRF-Token",{}).get("required") is True, "CSRF missing: " + oid)
            if oid == "m07_n05":
                require("Idempotency-Key" not in headers and op.get("x-retry-policy") == "READ_ONLY_POST" and op.get("x-idempotency-header") == "REJECT_400", "Lookup receipt/secret policy drift")
            else:
                require(headers.get("Idempotency-Key",{}).get("required") is True, "Business idempotency missing: " + oid)
        if op.get("x-version-target"):
            require(headers.get("If-Match",{}).get("required") is True, "Version precondition missing: " + oid)
        require(op["x-roles"] == entry["roles"] and op["x-required-permission"] == entry["permission"] and method == entry["method"] and path == entry["path"], "Permission/inventory drift: " + oid)
        if entry.get("request") and entry["request"] != "BINARY":
            require(op.get("requestBody",{}).get("required") is True and op["requestBody"]["content"]["application/json"]["schema"] == {"$ref":"#/components/schemas/"+entry["request"]}, "Request schema drift: " + oid)
        if entry.get("response") != "BINARY":
            require(any(v.get("content",{}).get("application/json",{}).get("schema") == {"$ref":"#/components/schemas/"+entry["response"]} for k,v in op["responses"].items() if k.startswith("2")), "Response schema drift: " + oid)
    for oid in ["m07_n26","m07_n27","m07_n39"]:
        require({"RECENT_REAUTH","GOVERNANCE_REASON"} <= set(flat[oid][2]["x-authorization-guards"]), "Governance reauth drift")
    require(flat["m07_n24"][2].get("x-action-roles",{}).get("ADMIN_CORRECTION") == ["SUPERVISOR"], "Technician administrative correction grant")
    require(flat["m07_n08"][2].get("x-action-roles",{}).get("CLOSE") == ["SUPERVISOR"], "Resident self-close grant")
    forbidden = {"incident_id","work_order_id","owner_membership_id","assignee_membership_id","internal_reason","technician_membership_id","profile_id","subject_id","ciphertext","resident_email","storage_key","actual_labels","truth_generation_seed"}
    for oid in new_ids:
        op = flat[oid][2]
        citizen = op.get("x-role-projections",{}).get("CITIZEN")
        if citizen:
            require(not (properties(spec, {"$ref":"#/components/schemas/"+citizen}) & forbidden), "Citizen projection leaks internal data: " + oid)
    components = spec["components"]["schemas"]
    def walk(node):
        if isinstance(node,dict):
            reference = node.get("$ref")
            if reference:
                current = spec
                try:
                    require(reference.startswith("#/"), "External reference is not approved")
                    for key in reference[2:].split("/"):
                        current = current[key.replace("~1","/").replace("~0","~")]
                except (KeyError,TypeError):
                    require(False,"Broken local schema reference: " + reference)
            for value in node.values(): walk(value)
        elif isinstance(node,list):
            for value in node: walk(value)
    walk(spec)
    for name,schema in components.items():
        if name.startswith("M07") and schema.get("type") == "object":
            require(schema.get("additionalProperties") is False, "Proposed object accepts arbitrary fields: " + name)
    for name in ["M07Feedback","M07Notification","M07Attachment"]:
        require("version" in components[name].get("required",[]), "Mutable DTO version absent: " + name)
    upload = components["M07UploadStart"]["properties"]
    require(upload["media_type"].get("enum") == ["image/jpeg","image/png","image/webp"], "Image-only policy drift")
    require("SERVICE_TEST" not in upload["purpose"]["enum"] and upload["target_id"].get("type") == "string", "Unapproved service-test/draft upload")
    require(upload["size_bytes"].get("maximum") == 5242880, "Upload byte limit drift")
    for name in ["M07NotificationPreferences","M07NotificationPreferencesWrite"]:
        channels = components[name]["properties"]["channels"]["properties"]
        require(all(channels[k].get("const") is False for k in ["email","sms","push"]), "External channel enabled")
    require(components["M07VerificationSummary"]["enum"] == ["NOT_APPLICABLE","PENDING_REVIEW","NOT_VERIFIABLE"], "Scientific verification gate drift")
    for number in [23,25,26,27,28,29,30,31,32,33,38,39]:
        require(not any(g.startswith("D5_") for g in flat[f"m07_n{number:02d}"][2]["x-authorization-guards"]), "Scheduling configuration/cancellation bootstrap deadlock")
    tables = {t["name"]:t for t in db["tables"]}
    require(len(tables) == len(db["tables"]) == 74 and len(db["x-m07-new-tables"]) == 17, "Database table count drift")
    for t in tables.values():
        columns = {c["name"] for c in t["columns"]}
        require(len(columns) == len(t["columns"]), "Duplicate DB column: " + t["name"])
        for fk in t["foreign_keys"]:
            target = tables.get(fk["target"])
            require(target is not None and fk["column"] in columns, "Broken DB FK: " + t["name"])
            if target:
                require(fk["same_tenant"] == (t["scope"] == target["scope"] == "tenant" and fk["column"] != "organization_id"), "Composite tenant FK drift: " + t["name"])
    for name,values in db["enums"].items():
        require(components[name]["enum"] == values, "Database/wire enum drift: " + name)
    allocation = tables["dispatch_allocations"]
    expected_constraint = {"kind":"EXCLUDE_GIST","keys":[["organization_id","="],["subject_id","="],["occupied_range","&&"]],"where":"active","extension":"btree_gist"}
    require(expected_constraint in allocation["constraints"], "Allocation exclusion constraint drift")
    require("user_id" in tables["dispatch_calendar_subjects"]["unique"] and tables["dispatch_calendar_subjects"]["scope"] == "global", "Exclusive enrollment uniqueness drift")
    require("SUBJECT_EXCLUSIVE_ORG_MATCHES_PROFILE_ORG" in tables["dispatch_technician_profiles"]["invariants"], "Exclusive enrollment tenant binding missing")
    require("subject_id WHERE status=CHECKED_IN" in tables["appointments"]["unique"], "Active visit uniqueness drift")
    require(all(tables[n]["retention"] == "M07_POLICY_REVIEW_REQUIRED" for n in db["x-m07-new-tables"]), "Unapproved live retention policy")
    require(states["policy_gates"] == {"availability_defaults":None,"live_retention_policy":None,"customer_sla":None,"external_channels":False,"pdf_documents":False,"offline":False,"max_total_delivery_attempts":3,"retry_delays_seconds":None,"encryption":"OWNER_REVIEW_REQUIRED","image_pipeline":"SCANNER_PROCESSING_STORAGE_LICENSE_OWNER_REVIEW_REQUIRED"}, "D5-D10 policy gate drift")
    require("OLD_APPOINTMENT_STAYS_UNTIL_ATOMIC_REPLACEMENT" in states["invariants"], "Atomic reschedule invariant missing")
    require("CANCELLED" not in states["appointment"]["CHECKED_IN"], "Checked-in cancellation fiction")
    for domain,schema in [("service","M07ServiceStatus"),("appointment_request","M07AppointmentRequestStatus"),("appointment","M07AppointmentStatus")]:
        require(set(states[domain]) == set(components[schema]["enum"]), "State enum coverage drift: " + domain)
        require(all(set(v) <= set(states[domain]) for v in states[domain].values()), "Unknown state edge")
    require(len(routes["pages"]) == 51 and len({p["route"] for p in routes["pages"]}) == 51, "Proposed route count/unique path drift")
    for page in routes["pages"]:
        require(set(page["operations"] + page.get("x-m07-proposed-operations",[])) <= set(flat), "Route references absent API: " + page["id"])
        if int(page["id"].split("-")[1]) > 46:
            require(page.get("status") == "PROPOSED_NOT_ROUTED" and "ONLINE_ONLY" in page["offline"], "Future route advertised active")
    return errors


def frozen_files():
    errors = []
    lock = read("data/schemas/m07-baseline-lock.json")
    if lock["baseline"] != BASE: errors.append("Frozen baseline revision changed")
    for name,digest in lock["sha256"].items():
        if not (ROOT/name).is_file() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            errors.append("Frozen runtime/scientific/hardware contract changed: " + name)
    for source in read("data/schemas/m07-planning-source-manifest.json")["sources"]:
        if hashlib.sha256((ROOT/source["path"]).read_bytes()).hexdigest() != source["sha256"]:
            errors.append("Owner planning source changed: " + source["path"])
    return errors


def main():
    errors = frozen_files() + validate(*load())
    for error in errors: print("FAIL:",error)
    print(f"M07 design: 161 composed operations (58 unchanged runtime; 44 new + 11 deferred selected); 74 designed / 30 migrated tables; 51 proposed / 46 current routes; {len(errors)} error(s).")
    print("Contract/design checks only. No SQL migration, scheduling, upload, notification or security enforcement is claimed.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
