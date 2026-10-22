"""Independent OpenAPI/JSON Schema checks in the pinned design-review environment."""
import copy
from importlib.metadata import version
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import OpenAPIV31SpecValidator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = json.loads((ROOT/"docs/architecture/m07/openapi-proposed.json").read_text(encoding="utf-8"))
    OpenAPIV31SpecValidator(spec).validate()
    for s in spec["components"]["schemas"].values():
        Draft202012Validator.check_schema(s)
    registry = Registry().with_resource("urn:hydro:m07",Resource.from_contents(spec,default_specification=DRAFT202012))
    def valid(name,value):
        return Draft202012Validator({"$ref":"urn:hydro:m07#/components/schemas/"+name},registry=registry,format_checker=FormatChecker()).is_valid(value)
    uid = "00000000-0000-4000-8000-000000000001"
    sample = {"category":"VISIBLE_LEAK","description":"SYNTHETIC schema test concern","coarse_area":"SYNTHETIC locality","origin_complaint_id":None,"expected_complaint_version":None,"follow_up_of_id":None,"service_privacy_acknowledged":True}
    checks = []
    def check(name,value,expected):
        assert valid(name,value) is expected,(name,expected)
        checks.append((name,expected))
    check("M07ServiceCreate",sample,True)
    bad = copy.deepcopy(sample);bad["owner_membership_id"] = uid;check("M07ServiceCreate",bad,False)
    bad = copy.deepcopy(sample);bad["category"] = "BILL_PAYMENT";check("M07ServiceCreate",bad,False)
    bad = copy.deepcopy(sample);bad["origin_complaint_id"] = uid;check("M07ServiceCreate",bad,False)
    bad["expected_complaint_version"] = 1;check("M07ServiceCreate",bad,True)
    req = {"kind":"INITIAL","window_id":uid,"expected_window_version":1,"expected_preferences_version":None,"replaces_appointment_id":None,"expected_appointment_version":None,"message":"SYNTHETIC schema fixture, not availability"}
    check("M07AppointmentRequestCreate",req,True)
    bad = copy.deepcopy(req);bad["kind"] = "RESCHEDULE";check("M07AppointmentRequestCreate",bad,False)
    bad.update({"replaces_appointment_id":uid,"expected_appointment_version":2});check("M07AppointmentRequestCreate",bad,True)
    photo = {"purpose":"SERVICE_REQUEST","target_id":uid,"media_type":"image/png","size_bytes":100,"sha256":"a"*64,"consent":True}
    check("M07UploadStart",photo,True)
    for key,value in [("media_type","application/pdf"),("size_bytes",5242881),("target_id",None),("consent",False)]:
        bad = copy.deepcopy(photo);bad[key] = value;check("M07UploadStart",bad,False)
    channels = {"channels":{"in_app":True,"email":False,"sms":False,"push":False},"event_categories":["APPOINTMENT"],"quiet_hours":None}
    check("M07NotificationPreferencesWrite",channels,True)
    bad = copy.deepcopy(channels);bad["channels"]["email"] = True;check("M07NotificationPreferencesWrite",bad,False)
    check("M07Interval",{"start_at":"2026-10-22T05:00:00Z","end_at":"2026-10-22T06:00:00Z"},True)
    check("M07Interval",{"start_at":"2026-10-22T05:00:00","end_at":"2026-10-22T06:00:00"},False)
    check("M07VerificationSummary","NOT_VERIFIABLE",True)
    check("M07VerificationSummary","VERIFICATION_PASSED",False)
    for package in ["openapi-spec-validator","openapi-schema-validator","jsonschema","referencing"]:
        print(package+"=="+version(package))
    print(f"PASS: M07 OpenAPI 3.1, {len(spec['components']['schemas'])} metaschemas and {len(checks)} positive/negative schema examples.")
    print("Schema examples are synthetic contract checks; no DB concurrency, scanner, physical or service operation was executed.")


if __name__ == "__main__":
    main()
