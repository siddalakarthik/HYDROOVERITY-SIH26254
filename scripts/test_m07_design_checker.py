"""Adversarial contract tests, not operational M07 acceptance tests."""
import copy
import unittest
from check_m07_design import load, validate


class M07DesignMutations(unittest.TestCase):
    def test_valid_contract(self):
        self.assertEqual(validate(*load()), [])

    def test_rejects_invalid_contracts(self):
        baseline = load()
        def op(d, number):
            return next(o for methods in d[0]["paths"].values() for o in methods.values() if o.get("operationId") == f"m07_n{number:02d}")
        def table(d, name):
            return next(t for t in d[1]["tables"] if t["name"] == name)
        mutations = [
            ("false implementation claim",lambda d:op(d,1).update({"x-implementation-status":"CODE_TESTED"}),"status drift"),
            ("anonymous service",lambda d:op(d,1).update({"security":[]}),"Session security"),
            ("citizen ownership removed",lambda d:op(d,3)["x-authorization-guards"].remove("CITIZEN_OWNED"),"Citizen ownership"),
            ("technician assignment removed",lambda d:op(d,24)["x-authorization-guards"].remove("TECHNICIAN_ASSIGNED"),"Technician scope"),
            ("self calendar broadened",lambda d:op(d,28)["x-authorization-guards"].remove("TECHNICIAN_SELF"),"Technician scope"),
            ("CSRF optional",lambda d:next(p for p in op(d,1)["parameters"] if p["name"]=="X-CSRF-Token").update({"required":False}),"CSRF missing"),
            ("idempotency optional",lambda d:next(p for p in op(d,1)["parameters"] if p["name"]=="Idempotency-Key").update({"required":False}),"Business idempotency"),
            ("lookup caches business receipt",lambda d:op(d,5).update({"x-retry-policy":"TENANT_7_DAY"}),"Lookup receipt"),
            ("missing booking version",lambda d:next(p for p in op(d,18)["parameters"] if p["name"]=="If-Match").update({"required":False}),"Version precondition"),
            ("governance reauth removed",lambda d:op(d,26)["x-authorization-guards"].remove("RECENT_REAUTH"),"Governance reauth"),
            ("resident self-closes",lambda d:op(d,8)["x-action-roles"].update({"CLOSE":["CITIZEN"]}),"self-close"),
            ("tech impersonates correction",lambda d:op(d,24)["x-action-roles"].update({"ADMIN_CORRECTION":["TECHNICIAN"]}),"administrative correction"),
            ("citizen internal DTO",lambda d:op(d,3)["x-role-projections"].update({"CITIZEN":"M07ServiceCaseStaff"}),"Citizen projection leaks"),
            ("citizen nested leak",lambda d:d[0]["components"]["schemas"]["M07ResidentWindow"]["properties"].update({"technician_membership_id":{"type":"string"}}),"Citizen projection leaks"),
            ("PDF enabled",lambda d:d[0]["components"]["schemas"]["M07UploadStart"]["properties"]["media_type"]["enum"].append("application/pdf"),"Image-only"),
            ("unbounded upload",lambda d:d[0]["components"]["schemas"]["M07UploadStart"]["properties"]["size_bytes"].update({"maximum":999999999}),"Upload byte"),
            ("email enabled",lambda d:d[0]["components"]["schemas"]["M07NotificationPreferencesWrite"]["properties"]["channels"]["properties"]["email"].update({"const":True}),"External channel"),
            ("verification fabricated",lambda d:d[0]["components"]["schemas"]["M07VerificationSummary"]["enum"].append("VERIFICATION_PASSED"),"Scientific verification"),
            ("exclusion removed",lambda d:table(d,"dispatch_allocations")["constraints"].clear(),"Allocation exclusion"),
            ("exclusive enrollment removed",lambda d:table(d,"dispatch_calendar_subjects")["unique"].clear(),"Exclusive enrollment"),
            ("exclusive tenant binding removed",lambda d:table(d,"dispatch_technician_profiles")["invariants"].remove("SUBJECT_EXCLUSIVE_ORG_MATCHES_PROFILE_ORG"),"tenant binding"),
            ("FK tenant check removed",lambda d:next(f for f in table(d,"appointments")["foreign_keys"] if f["same_tenant"]).update({"same_tenant":False}),"Composite tenant FK"),
            ("two simultaneous checkins",lambda d:table(d,"appointments")["unique"].remove("subject_id WHERE status=CHECKED_IN"),"Active visit uniqueness"),
            ("retention approved by accident",lambda d:table(d,"service_requests").update({"retention":"30 days approved"}),"Unapproved live retention"),
            ("fourth notification attempt",lambda d:d[5]["policy_gates"].update({"max_total_delivery_attempts":4}),"policy gate"),
            ("defaults fabricated",lambda d:d[5]["policy_gates"].update({"availability_defaults":{"shift":"09:00"}}),"policy gate"),
            ("offline enabled",lambda d:d[5]["policy_gates"].update({"offline":True}),"policy gate"),
            ("atomic reschedule removed",lambda d:d[5]["invariants"].remove("OLD_APPOINTMENT_STAYS_UNTIL_ATOMIC_REPLACEMENT"),"Atomic reschedule"),
            ("checked-in cancelled fiction",lambda d:d[5]["appointment"]["CHECKED_IN"].append("CANCELLED"),"cancellation fiction"),
            ("configuration requires config",lambda d:op(d,39)["x-authorization-guards"].append("D5_CONFIGURED_CALENDAR"),"bootstrap deadlock"),
            ("future page advertised live",lambda d:d[4]["pages"][-1].update({"status":"ACTIVE_FUNCTIONAL"}),"Future route"),
            ("existing runtime reclassified",lambda d:next(o for o in d[3]["operations"] if not o["runtime_registered"]).update({"runtime_registered":True}),"Runtime registration"),
            ("legacy schema changed",lambda d:d[0]["components"]["schemas"]["WorkOrderWrite"]["properties"].update({"new_field":{"type":"string"}}),"Legacy reachable schema"),
            ("missing local schema",lambda d:d[0]["components"]["schemas"]["M07Followup"]["properties"].update({"bad":{"$ref":"#/components/schemas/Missing"}}),"Broken local schema"),
        ]
        for name,mutate,diagnostic in mutations:
            with self.subTest(name=name):
                d = copy.deepcopy(baseline)
                mutate(d)
                self.assertTrue(any(diagnostic in e for e in validate(*d)),name)
        print(f"Executed {len(mutations)} rejected M07 design mutations.")


if __name__ == "__main__":
    unittest.main()
