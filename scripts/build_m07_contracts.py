"""Compose review-only M07 contracts; never imported by the running application.

No SQL, network, identity, scheduling or upload implementation is performed here.
The deployed M02 catalogue and all M03/M04 source/generated contracts stay frozen.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "fe69ccdb10ab515f73bbceaaa4652ce440859c85"
O = "/orgs/{organization_id}"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def ref(name):
    return {"$ref": "#/components/schemas/" + name}


def text(maximum=2000, minimum=0):
    return {"type": "string", "minLength": minimum, "maxLength": maximum}


def integer(maximum=2147483647, minimum=1):
    return {"type": "integer", "minimum": minimum, "maximum": maximum}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def arr(item, maximum=100):
    return {"type": "array", "items": item, "maxItems": maximum, "uniqueItems": True}


def obj(properties, optional=()):
    return {"type": "object", "additionalProperties": False, "properties": properties,
            "required": [k for k in properties if k not in optional]}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def schemas():
    u = {"type": "string", "format": "uuid"}
    dt = {"type": "string", "format": "date-time", "pattern": r"(?:Z|[+-]\d{2}:\d{2})$"}
    b = {"type": "boolean"}
    v = integer()
    un, vn, dn = nullable(u), nullable(v), nullable(dt)
    s = {}
    def add(name, properties, optional=()):
        s["M07" + name] = obj(properties, optional)
    def r(name):
        return ref("M07" + name)
    def page(item):
        return obj({"items": arr(item), "next_cursor": nullable(text(500, 1)), "as_of": dt})
    s["M07ServiceCategory"] = enum("VISIBLE_LEAK", "LOW_PRESSURE", "SERVICE_INTERRUPTION")
    s["M07ServiceStatus"] = enum("SUBMITTED", "UNDER_REVIEW", "AWAITING_RESIDENT", "ACCEPTED", "SERVICE_IN_PROGRESS", "SERVICE_REVIEW_PENDING", "SERVICE_CLOSED", "DECLINED", "WITHDRAWN", "CANCELLED")
    s["M07AppointmentRequestStatus"] = enum("PENDING", "ALTERNATIVE_OFFERED", "CONFIRMED", "DECLINED", "WITHDRAWN", "EXPIRED")
    s["M07AppointmentStatus"] = enum("CONFIRMED", "CHECKED_IN", "VISIT_FINISHED", "NO_ACCESS", "ABORTED", "NO_SHOW", "CANCELLED", "SUPERSEDED")
    s["M07TaskPurpose"] = enum("REPAIR", "INVESTIGATION")
    s["M07ServiceOutcome"] = enum("ADVICE_PROVIDED", "VISIT_COMPLETED", "REPAIR_REPORTED", "REFERRED", "NO_ACTION_WITH_REASON")
    s["M07VerificationSummary"] = enum("NOT_APPLICABLE", "PENDING_REVIEW", "NOT_VERIFIABLE")
    add("Interval", {"start_at": dt, "end_at": dt})
    add("Reason", {"reason_code": text(40, 1), "reason": text(1000, 5)})
    add("ReferenceLookup", {"tracking_reference": {**text(40, 6), "pattern": "^HYS-[0-9A-HJKMNP-TV-Z]{26}$"}})
    add("ReferenceResult", {"id": u, "tracking_reference": text(40, 6)})
    add("ServiceCreate", {"category": r("ServiceCategory"), "description": text(2000, 10), "coarse_area": text(200, 2), "origin_complaint_id": un, "expected_complaint_version": vn, "follow_up_of_id": un, "service_privacy_acknowledged": {"const": True, "type": "boolean"}})
    add("Followup", {"operation_id": u, "message": text(2000, 1)})
    add("Triage", {"target": enum("UNDER_REVIEW", "AWAITING_RESIDENT", "ACCEPTED", "DECLINED"), "public_message": text(1000, 5), "internal_reason": text(2000, 5)})
    add("PublicUpdateWrite", {"event_kind": enum("INFORMATION", "PROGRESS", "CORRECTION"), "message": text(2000, 5), "supersedes_update_id": un})
    add("PublicUpdate", {"id": u, "sequence": v, "event_kind": enum("INFORMATION", "PROGRESS", "CORRECTION", "SERVICE", "APPOINTMENT", "VISIT"), "message": text(2000), "occurred_at": dt, "published_at": dt, "appointment_id": un, "supersedes_id": un})
    add("InternalEvent", {"id": u, "sequence": v, "event_kind": text(40, 1), "actor_membership_id": un, "received_at": dt, "observed_at": dn, "internal_reason": text(2000), "resource_type": enum("SERVICE", "APPOINTMENT", "WORK", "FEEDBACK", "ATTACHMENT"), "resource_id": un, "previous_version": vn, "resulting_version": vn, "supersedes_id": un})
    s["M07TimelinePage"] = {"oneOf": [page(r("PublicUpdate")), page(r("InternalEvent"))]}
    # The audience constant disambiguates empty public/internal pages.
    for choice, audience in zip(s["M07TimelinePage"]["oneOf"], ["PUBLIC", "INTERNAL"]):
        choice["properties"]["audience"] = {"const": audience, "type": "string"}
        choice["required"].append("audience")
    add("PreferencesWrite", {"expected_preferences_version": vn, "intervals": arr(r("Interval"), 5), "access_needs": text(500)})
    add("Preferences", {"version": v, "intervals": arr(r("Interval"), 5), "access_needs": text(500), "updated_at": dt})
    add("VisitAccessWrite", {"expected_access_version": vn, "site_text": text(500, 1), "safe_access_instructions": text(500), "technician_disclosure_consent": {"const": True, "type": "boolean"}})
    add("VisitAccess", {"version": vn, "site_text": nullable(text(500)), "safe_access_instructions": nullable(text(500)), "consented_at": dn, "updated_at": dn})
    child = obj({"work_order_id": u, "version": v})
    dispositions = arr(obj({"appointment_id": u, "expected_version": v, "action": enum("CANCEL", "KEEP_FOR_SHARED_WORK")}), 20)
    transitions = []
    for action in ["WITHDRAW", "REQUEST_CANCELLATION", "CANCEL", "START_SERVICE", "REQUEST_REVIEW", "RETURN_TO_WORK", "CLOSE"]:
        props = {"action": {"const": action, "type": "string"}, "reason_code": text(40, 1), "public_message": text(1000, 5)}
        if action not in {"WITHDRAW", "REQUEST_CANCELLATION"}:
            props["internal_reason"] = text(2000, 5)
        if action in {"CANCEL", "CLOSE"}:
            props["expected_work_versions"] = arr(child, 20)
            props["child_dispositions"] = dispositions
        if action == "CLOSE":
            props["service_outcome"] = r("ServiceOutcome")
        transitions.append(obj(props))
    s["M07ServiceTransition"] = {"oneOf": transitions}
    add("WorkLinkWrite", {"work_order_id": u, "expected_work_version": v, "purpose": r("TaskPurpose"), "internal_reason": text(2000, 5)})
    add("WorkLink", {"id": u, "service_request_id": u, "work_order_id": u, "purpose": r("TaskPurpose"), "created_at": dt, "version": v})
    arrival = {"arrival_start": dt, "arrival_end": dt, "expected_service_minutes": integer(480), "timezone": {"type": "string", "const": "Asia/Kolkata"}}
    add("ResidentWindow", {"id": u, "version": v, **arrival, "policy_version": v, "as_of": dt, "confirmation_required": {"type": "boolean", "const": True}})
    staff_window = {**s["M07ResidentWindow"]["properties"], "technician_membership_id": u, "calendar_version": v, "category_codes": arr(r("ServiceCategory"), 3), "service_area_codes": arr(text(40, 1), 20), "before_buffer_minutes": integer(240, 0), "after_buffer_minutes": integer(240, 0), "state": enum("PUBLISHED", "WITHDRAWN"), "occupied_interval": r("Interval")}
    add("StaffWindow", staff_window)
    ap = {"id": u, "service_request_id": u, "status": r("AppointmentStatus"), **arrival, "public_visit_message": nullable(text(1000)), "cancellation_pending": b, "replaces_id": un, "version": v, "created_at": dt, "updated_at": dt, "allowed_actions": arr(text(40, 1), 10)}
    add("AppointmentCitizen", ap)
    add("AppointmentStaff", {**ap, "request_id": u, "window_id": u, "work_order_id": u, "assignee_membership_id": u, "assignment_version": v, "occupied_interval": r("Interval"), "calendar_version": v, "policy_version": v, "dispatch_health": enum("READY", "REVIEW_REQUIRED", "UNPLANNED_WORK"), "internal_reason": text(2000)})
    add("AppointmentTechnician", {"id": u, "status": r("AppointmentStatus"), **arrival, "work_order_id": u, "assignment_version": v, "work_version": v, "version": v, "safe_access_instructions": text(500), "safe_task_instructions": text(4000), "brief_expires_at": dt, "allowed_actions": arr(text(40, 1), 10)})
    s["M07AppointmentRead"] = {"anyOf": [r("AppointmentCitizen"), r("AppointmentStaff"), r("AppointmentTechnician")]}
    add("AppointmentRequestCreate", {"kind": enum("INITIAL", "RESCHEDULE"), "window_id": u, "expected_window_version": v, "expected_preferences_version": vn, "replaces_appointment_id": un, "expected_appointment_version": vn, "message": text(500)})
    req = {"id": u, "service_request_id": u, "kind": enum("INITIAL", "RESCHEDULE"), "status": r("AppointmentRequestStatus"), "requested_window": r("ResidentWindow"), "alternative_window": nullable(r("ResidentWindow")), "proposal_revision": vn, "offer_expires_at": dn, "replaces_appointment_id": un, "confirmed_appointment_id": un, "public_message": nullable(text(1000)), "created_at": dt, "updated_at": dt, "version": v}
    add("AppointmentRequestCitizen", req)
    expectations = {"service_version": v, "work_order_id": u, "work_version": v, "assignment_version": v, "window_version": v, "calendar_version": v, "policy_version": v, "replaced_appointment_version": vn}
    add("BookingExpectations", expectations)
    add("AppointmentRequestStaff", {**req, "expectations": r("BookingExpectations"), "internal_reason": text(2000)})
    s["M07AppointmentRequestRead"] = {"anyOf": [r("AppointmentRequestCitizen"), r("AppointmentRequestStaff")]}
    decisions = []
    for action in ["CONFIRM_REQUESTED", "OFFER_ALTERNATIVE", "DECLINE"]:
        props = {"decision": {"const": action, "type": "string"}, "public_message": text(1000, 5), "internal_reason": text(2000, 5)}
        if action != "DECLINE":
            props["expectations"] = r("BookingExpectations")
        if action == "OFFER_ALTERNATIVE":
            props.update({"alternative_window_id": u, "expected_window_version": v, "offer_expires_at": dt})
        if action == "DECLINE":
            props["reason_code"] = text(40, 1)
        decisions.append(obj(props))
    s["M07AppointmentDecision"] = {"oneOf": decisions}
    add("AlternativeAccept", {"proposal_revision": v, "expected_window_version": v, "expected_service_version": v, "expected_replaced_appointment_version": vn})
    add("AppointmentDecisionReceipt", {"receipt": ref("Receipt"), "request": r("AppointmentRequestRead"), "appointment": nullable(r("AppointmentRead")), "replaced_appointment": nullable(r("AppointmentRead"))})
    cancel = {"reason_code": text(40, 1), "public_reason": text(1000, 5), "expected_service_version": v}
    s["M07AppointmentCancel"] = {"oneOf": [obj({"caller_action": {"type": "string", "const": "RESIDENT"}, **cancel}), obj({"caller_action": {"type": "string", "const": "SUPERVISOR"}, **cancel, "internal_reason": text(2000, 5), "expected_work_version": v, "expected_assignment_version": v, "disposition": enum("CANCEL", "ACCEPT_PENDING_CANCEL", "DECLINE_PENDING_CANCEL")})]}
    add("AppointmentCommandReceipt", {"receipt": ref("Receipt"), "appointment": r("AppointmentRead"), "current_service_version": v})
    add("VisitEventWrite", {"operation_id": u, "event_type": enum("CHECK_IN", "VISIT_FINISHED", "NO_ACCESS", "ABORTED", "OVERRUN_REPORTED", "ADMIN_CORRECTION"), "observed_at": dt, "assignment_version": v, "expected_work_version": v, "note": text(2000, 1), "supersedes_event_id": un})
    add("VisitEventReceipt", {"receipt": ref("Receipt"), "appointment": r("AppointmentRead")})
    case = {"id": u, "tracking_reference": text(40, 6), "category": r("ServiceCategory"), "description": text(2000, 10), "coarse_area": text(200, 2), "status": r("ServiceStatus"), "cancellation_pending": b, "service_outcome": nullable(r("ServiceOutcome")), "verification_summary": r("VerificationSummary"), "created_at": dt, "updated_at": dt, "accepted_at": dn, "version": v, "own_origin_complaint_id": un, "own_follow_up_of_id": un, "preferences": nullable(r("Preferences")), "latest_public_update": nullable(r("PublicUpdate")), "current_appointment": nullable(r("AppointmentCitizen")), "allowed_actions": arr(text(40, 1), 20)}
    add("ServiceCaseCitizen", case)
    add("ServiceCaseStaff", {**case, "owner_membership_id": u, "work_links": arr(r("WorkLink"), 20), "dispatch_health": enum("UNCONFIGURED", "UNPLANNED_WORK", "READY", "REVIEW_REQUIRED"), "internal_event_summary": text(2000)})
    s["M07ServiceCaseRead"] = {"anyOf": [r("ServiceCaseCitizen"), r("ServiceCaseStaff")]}
    profile = {"membership_id": u, "display_name": text(100, 1), "enrollment_state": enum("ELIGIBLE", "ENROLLED", "UNAVAILABLE"), "active": b, "skill_codes": arr(text(40, 1), 20), "service_area_codes": arr(text(40, 1), 20), "max_daily_minutes": nullable(integer(960)), "profile_version": vn, "calendar_version": vn, "scheduling_health": enum("READY", "UNPLANNED_WORK", "REVIEW_REQUIRED", "UNCONFIGURED")}
    add("DispatchTechnician", profile)
    enroll = {"membership_id": u, "expected_membership_version": v, "skill_codes": profile["skill_codes"], "service_area_codes": profile["service_area_codes"], "max_daily_minutes": integer(960), "exclusive_dispatch_acknowledged": {"type": "boolean", "const": True}, "reason": text(2000, 5)}
    add("TechnicianEnroll", enroll)
    add("TechnicianProfilePatch", {k: enroll[k] for k in ["skill_codes", "service_area_codes", "max_daily_minutes", "reason"]} | {"active": b})
    add("ShiftWrite", {"technician_membership_id": u, "expected_calendar_version": v, "interval": r("Interval"), "reason": text(2000, 5)})
    add("ShiftChange", {"interval": r("Interval"), "status": enum("ACTIVE", "WITHDRAWN"), "expected_calendar_version": v, "reason": text(2000, 5)})
    add("Shift", {"id": u, "technician_membership_id": u, "interval": r("Interval"), "status": enum("ACTIVE", "WITHDRAWN"), "version": v, "calendar_version": v})
    block = {"technician_membership_id": u, "expected_calendar_version": v, "kind": enum("UNAVAILABLE", "WORK_BLOCK"), "interval": r("Interval"), "work_order_id": un, "expected_work_version": vn, "reason_code": text(40, 1), "internal_reason": text(2000, 5)}
    add("DispatchBlockWrite", block)
    add("DispatchBlock", {"id": u, "technician_membership_id": u, "kind": block["kind"], "interval": r("Interval"), "work_order_id": un, "version": v, "calendar_version": v})
    # Leave reasons never enter technician-self calendar DTOs.
    add("BlockRelease", {"expected_calendar_version": v, "expected_work_version": vn, "reason": text(2000, 5)})
    add("BlockReplace", {**s["M07BlockRelease"]["properties"], "interval": r("Interval")})
    add("WindowPublish", {"technician_membership_id": u, "expected_calendar_version": v, "expected_policy_version": v, "arrival_start": dt, "arrival_end": dt, "expected_service_minutes": integer(480), "before_buffer_minutes": integer(240, 0), "after_buffer_minutes": integer(240, 0), "category_codes": arr(r("ServiceCategory"), 3), "service_area_codes": arr(text(40, 1), 20), "reason": text(2000, 5)})
    add("WindowWithdraw", {"expected_calendar_version": v, "reason": text(2000, 5)})
    policy = {"horizon_days": integer(60), "minimum_lead_minutes": integer(10080, 0), "free_cancel_before_minutes": integer(10080, 0), "max_arrival_width_minutes": integer(480), "request_expiry_hours": integer(168), "offer_expiry_hours": integer(72), "max_daily_minutes": integer(960), "minimum_before_buffer_minutes": integer(240, 0), "minimum_after_buffer_minutes": integer(240, 0)}
    add("DispatchPolicy", {"version": v, "booking_enabled": b, "configured": b, **{k: nullable(value) for k, value in policy.items()}, "allowed_duration_minutes": arr(integer(480), 20), "updated_at": dt})
    add("DispatchPolicyWrite", {"booking_enabled": b, **policy, "allowed_duration_minutes": arr(integer(480), 20), "reason": text(2000, 5)})
    add("CalendarSnapshot", {"profile_version": v, "calendar_version": v, "as_of": dt, "timezone": {"type": "string", "const": "Asia/Kolkata"}, "shifts": page(r("Shift")), "blocks": page(r("DispatchBlock")), "appointments": page(r("AppointmentRead"))})
    add("WorkloadRow", {"technician_membership_id": u, "confirmed_appointments": integer(minimum=0), "planned_occupied_minutes": integer(minimum=0), "unplanned_work_count": integer(minimum=0), "overdue_work_count": integer(minimum=0), "available_shift_minutes": integer(minimum=0), "known_load_ratio": nullable({"type": "number", "minimum": 0, "maximum": 1}), "scheduling_health": profile["scheduling_health"]})
    add("WorkloadSnapshot", {"as_of": dt, "from": dt, "to": dt, "timezone": {"type": "string", "const": "Asia/Kolkata"}, "items": arr(r("WorkloadRow")), "next_cursor": nullable(text(500, 1))})
    channels = obj({"in_app": b, "email": {"type": "boolean", "const": False}, "sms": {"type": "boolean", "const": False}, "push": {"type": "boolean", "const": False}})
    quiet = nullable(obj({"start_local": {"type": "string", "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"}, "end_local": {"type": "string", "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"}, "timezone": {"type": "string", "const": "Asia/Kolkata"}}))
    prefs = {"channels": channels, "event_categories": arr(enum("SERVICE_PROGRESS", "APPOINTMENT", "WORK_ASSIGNMENT", "SERVICE_FEEDBACK"), 4), "quiet_hours": quiet}
    add("NotificationPreferencesWrite", prefs)
    add("NotificationPreferences", {"version": v, **prefs, "email_available": {"type": "boolean", "const": False}})
    add("DeliveryAttempt", {"notification_id": u, "event_kind": text(40, 1), "channel": {"type": "string", "const": "IN_APP"}, "state": enum("QUEUED", "SENDING", "DELIVERED", "RETRY_WAIT", "FAILED", "SUPPRESSED"), "attempt_number": integer(3, 0), "attempted_at": dn, "next_attempt_at": dn, "safe_error_code": nullable(text(40, 1))})
    add("FindingsWrite", {"operation_id": u, "assignment_version": v, "observed_at": dt, "findings": text(4000, 10), "no_repair_reason": text(2000, 5), "attachment_ids": arr(u, 10), "supersedes_id": un})
    add("Findings", {"id": u, "work_order_id": u, "recorded_by_membership_id": u, "observed_at": dt, "received_at": dt, "findings": text(4000, 10), "no_repair_reason": text(2000, 5), "attachment_ids": arr(u, 10), "supersedes_id": un, "provenance": {"type": "string", "const": "MANUAL"}})
    add("FindingsReceipt", {"receipt": ref("Receipt"), "resource": r("Findings"), "work_version": v})
    for item in ["ServiceCaseRead", "ResidentWindow", "StaffWindow", "AppointmentRequestRead", "AppointmentRead", "DispatchTechnician", "DeliveryAttempt", "Findings"]:
        s["M07Page_" + item] = page(r(item))
    s["M07Page_ResidentWindow"]["properties"].update({"availability_state":enum("AVAILABLE","NO_PUBLISHED_WINDOWS","UNCONFIGURED","DISABLED","SERVICE_REVIEW_REQUIRED"),"message":text(200)})
    s["M07Page_ResidentWindow"]["required"] += ["availability_state","message"]
    s["M07Page_ResidentWindow"]["allOf"] = [{"if":{"properties":{"availability_state":{"enum":["UNCONFIGURED","DISABLED","SERVICE_REVIEW_REQUIRED"]}},"required":["availability_state"]},"then":{"properties":{"items":{"maxItems":0}}}}]
    s["M07PublicTimelinePage"] = copy.deepcopy(s["M07TimelinePage"]["oneOf"][0])
    s["M07InternalTimelinePage"] = copy.deepcopy(s["M07TimelinePage"]["oneOf"][1])
    for role, appointment, request in [("Citizen","AppointmentCitizen","AppointmentRequestCitizen"),("Staff","AppointmentStaff","AppointmentRequestStaff")]:
        s["M07Page_ServiceCase" + role] = page(r("ServiceCase" + role))
        s["M07Page_AppointmentRequest" + role] = page(r(request))
        s["M07Page_Appointment" + role] = page(r(appointment))
        add(role + "DecisionReceipt", {"receipt":ref("Receipt"),"request":r(request),"appointment":nullable(r(appointment)),"replaced_appointment":nullable(r(appointment))})
        add(role + "AppointmentCommandReceipt", {"receipt":ref("Receipt"),"appointment":r(appointment),"current_service_version":v})
    for role, appointment in [("Technician","AppointmentTechnician"),("Staff","AppointmentStaff")]:
        add(role + "VisitEventReceipt", {"receipt":ref("Receipt"),"appointment":r(appointment)})
        value = copy.deepcopy(s["M07CalendarSnapshot"])
        value["properties"]["appointments"] = page(r(appointment))
        s["M07" + role + "CalendarSnapshot"] = value
    # Conditional shapes prevent self-contradictory retry/parent references.
    s["M07ServiceCreate"]["allOf"] = [{"if":{"properties":{"origin_complaint_id":{"type":"string"}},"required":["origin_complaint_id"]},"then":{"properties":{"expected_complaint_version":v,"follow_up_of_id":{"type":"null"}}},"else":{"properties":{"expected_complaint_version":{"type":"null"}}}}]
    s["M07AppointmentRequestCreate"]["allOf"] = [{"if":{"properties":{"kind":{"const":"INITIAL"}},"required":["kind"]},"then":{"properties":{"replaces_appointment_id":{"type":"null"},"expected_appointment_version":{"type":"null"}}},"else":{"properties":{"replaces_appointment_id":u,"expected_appointment_version":v}}}]
    s["M07DispatchBlockWrite"]["allOf"] = [{"if":{"properties":{"kind":{"const":"WORK_BLOCK"}},"required":["kind"]},"then":{"properties":{"work_order_id":u,"expected_work_version":v}},"else":{"properties":{"work_order_id":{"type":"null"},"expected_work_version":{"type":"null"}}}}]
    for name in ["M07TechnicianEnroll","M07WindowPublish"]:
        for key in ["skill_codes","service_area_codes","category_codes"]:
            if key in s[name]["properties"]:
                s[name]["properties"][key]["minItems"] = 1
    s["M07DispatchPolicyWrite"]["properties"]["allowed_duration_minutes"]["minItems"] = 1
    return s


# Stable IDs refer to the owner-reviewed proposal. Groups intentionally never
# enter hydro.contracts.implemented's legacy domain allow-list.
ROWS = [
    (1,"post","/service-requests","CITIZEN","ServiceCreate","ServiceCaseCitizen","service_requests",False,None),
    (2,"get","/service-requests","CITIZEN,SUPERVISOR",None,"Page_ServiceCaseRead","service_requests",False,None),
    (3,"get","/service-requests/{request_id}","CITIZEN,SUPERVISOR",None,"ServiceCaseRead","service_requests",False,None),
    (4,"get","/service-requests/{request_id}/timeline","CITIZEN,SUPERVISOR",None,"TimelinePage","service_public_updates",False,None),
    (5,"post","/service-request-lookups","CITIZEN,SUPERVISOR","ReferenceLookup","ReferenceResult","service_requests",False,None),
    (6,"post","/service-requests/{request_id}/follow-ups","CITIZEN","Followup","Receipt","service_request_events",True,"SERVICE"),
    (7,"post","/service-requests/{request_id}/triage","SUPERVISOR","Triage","ServiceCaseStaff","service_requests",True,"SERVICE"),
    (8,"post","/service-requests/{request_id}/transitions","CITIZEN,SUPERVISOR","ServiceTransition","ServiceCaseRead","service_requests",True,"SERVICE"),
    (9,"post","/service-requests/{request_id}/public-updates","SUPERVISOR","PublicUpdateWrite","PublicUpdate","service_public_updates",True,"SERVICE"),
    (10,"put","/service-requests/{request_id}/visit-preferences","CITIZEN","PreferencesWrite","Preferences","service_visit_preferences",True,"SERVICE"),
    (11,"get","/service-requests/{request_id}/visit-access","CITIZEN,SUPERVISOR",None,"VisitAccess","service_visit_access",False,None),
    (12,"put","/service-requests/{request_id}/visit-access","CITIZEN","VisitAccessWrite","VisitAccess","service_visit_access",True,"SERVICE"),
    (13,"post","/service-requests/{request_id}/work-order-links","SUPERVISOR","WorkLinkWrite","WorkLink","service_work_order_links",True,"SERVICE"),
    (14,"get","/service-requests/{request_id}/appointment-windows","CITIZEN,SUPERVISOR",None,"Page_ResidentWindow","appointment_windows",False,None),
    (15,"post","/service-requests/{request_id}/appointment-requests","CITIZEN","AppointmentRequestCreate","AppointmentRequestCitizen","appointment_requests",True,"SERVICE"),
    (16,"get","/service-requests/{request_id}/appointment-requests","CITIZEN,SUPERVISOR",None,"Page_AppointmentRequestRead","appointment_requests",False,None),
    (17,"get","/appointment-requests/{appointment_request_id}","CITIZEN,SUPERVISOR",None,"AppointmentRequestRead","appointment_requests",False,None),
    (18,"post","/appointment-requests/{appointment_request_id}/decisions","SUPERVISOR","AppointmentDecision","AppointmentDecisionReceipt","appointments",True,"APPOINTMENT_REQUEST"),
    (19,"post","/appointment-requests/{appointment_request_id}/accept-alternative","CITIZEN","AlternativeAccept","AppointmentDecisionReceipt","appointments",True,"APPOINTMENT_REQUEST"),
    (20,"post","/appointment-requests/{appointment_request_id}/withdrawals","CITIZEN","Reason","AppointmentRequestCitizen","appointment_requests",True,"APPOINTMENT_REQUEST"),
    (21,"get","/service-requests/{request_id}/appointments","CITIZEN,SUPERVISOR",None,"Page_AppointmentRead","appointments",False,None),
    (22,"get","/appointments/{appointment_id}","CITIZEN,SUPERVISOR,TECHNICIAN",None,"AppointmentRead","appointments",False,None),
    (23,"post","/appointments/{appointment_id}/cancellations","CITIZEN,SUPERVISOR","AppointmentCancel","AppointmentCommandReceipt","appointments",True,"APPOINTMENT"),
    (24,"post","/appointments/{appointment_id}/visit-events","TECHNICIAN,SUPERVISOR","VisitEventWrite","VisitEventReceipt","appointment_events",True,"APPOINTMENT"),
    (25,"get","/dispatch/technicians","SUPERVISOR,ADMIN",None,"Page_DispatchTechnician","dispatch_technician_profiles",False,None),
    (26,"post","/dispatch/technicians","ADMIN","TechnicianEnroll","DispatchTechnician","dispatch_technician_profiles",False,None),
    (27,"patch","/dispatch/technicians/{membership_id}","ADMIN","TechnicianProfilePatch","DispatchTechnician","dispatch_technician_profiles",True,"PROFILE"),
    (28,"get","/dispatch/technicians/{membership_id}/calendar","SUPERVISOR,TECHNICIAN",None,"CalendarSnapshot","dispatch_allocations",False,None),
    (29,"post","/dispatch/shifts","SUPERVISOR","ShiftWrite","Shift","dispatch_shifts",True,"PROFILE"),
    (30,"patch","/dispatch/shifts/{shift_id}","SUPERVISOR","ShiftChange","Shift","dispatch_shifts",True,"SHIFT"),
    (31,"post","/dispatch/blocks","SUPERVISOR","DispatchBlockWrite","DispatchBlock","dispatch_allocations",True,"PROFILE"),
    (32,"post","/dispatch/blocks/{block_id}/release","SUPERVISOR","BlockRelease","DispatchBlock","dispatch_allocations",True,"BLOCK"),
    (33,"post","/dispatch/blocks/{block_id}/replacements","SUPERVISOR","BlockReplace","DispatchBlock","dispatch_allocations",True,"BLOCK"),
    (34,"get","/dispatch/appointment-windows","SUPERVISOR",None,"Page_StaffWindow","appointment_windows",False,None),
    (35,"post","/dispatch/appointment-windows","SUPERVISOR","WindowPublish","StaffWindow","appointment_windows",True,"PROFILE"),
    (36,"post","/dispatch/appointment-windows/{window_id}/withdrawals","SUPERVISOR","WindowWithdraw","StaffWindow","appointment_windows",True,"WINDOW"),
    (37,"get","/dispatch/workload","SUPERVISOR",None,"WorkloadSnapshot","dispatch_allocations",False,None),
    (38,"get","/dispatch/policy","SUPERVISOR,ADMIN",None,"DispatchPolicy","dispatch_policy",False,None),
    (39,"put","/dispatch/policy","ADMIN","DispatchPolicyWrite","DispatchPolicy","dispatch_policy",True,"POLICY"),
    (40,"get","/notification-preferences","ALL",None,"NotificationPreferences","notification_preferences",False,None),
    (41,"put","/notification-preferences","ALL","NotificationPreferencesWrite","NotificationPreferences","notification_preferences",True,"PREFERENCES"),
    (42,"get","/service-requests/{request_id}/delivery-audit","SUPERVISOR",None,"Page_DeliveryAttempt","notification_delivery_attempts",False,None),
    (43,"post","/work-orders/{work_order_id}/findings","TECHNICIAN","FindingsWrite","FindingsReceipt","investigation_findings",True,"WORK_ORDER"),
    (44,"get","/work-orders/{work_order_id}/findings","SUPERVISOR,ENGINEER,TECHNICIAN",None,"Page_Findings","investigation_findings",False,None),
]


def operation(row):
    n, method, suffix, roles, request, response, table, match, target = row
    phase = "M07-A" if n <= 13 or n >= 43 else "M07-B" if n <= 39 else "M07-C"
    permission = ("service_requests" if n <= 13 else "dispatch" if n <= 39 else "notification_preferences" if n <= 41 else "service_requests" if n == 42 else "investigation_findings") + (".read" if method == "get" or n == 5 else ".write")
    params = [{"name": name, "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}} for name in re.findall(r"{(.*?)}", O + suffix)]
    if method != "get":
        params.append({"name": "X-CSRF-Token", "in": "header", "required": True, "schema": text(200, 1)})
        if n != 5:
            params.append({"name": "Idempotency-Key", "in": "header", "required": True, "schema": {"type": "string", "format": "uuid"}})
        if match:
            params.append({"name": "If-Match", "in": "header", "required": True, "schema": {"type": "string", "pattern": '^"[1-9][0-9]*"$'}, "description": "Current " + target + " resource version; body contains any additional parent/calendar versions."})
    filters = []
    if response.startswith("Page_") or n in {4, 28, 37}:
        params += [{"name": "limit", "in": "query", "schema": integer(100)}, {"name": "cursor", "in": "query", "schema": text(500, 1)}]
    for name in (["from", "to"] if n in {14, 28, 34, 37} else []):
        params.append({"name": name, "in": "query", "required": True, "schema": {"type": "string", "format": "date-time"}})
        filters.append(name)
    if n == 4:
        params.append({"name": "audience", "in": "query", "schema": enum("PUBLIC", "INTERNAL"), "description": "Default PUBLIC. INTERNAL is SUPERVISOR-only; denied to citizen even when owned."})
        filters.append("audience")
    optional_filters = {2:{"status":ref("M07ServiceStatus"),"category":ref("M07ServiceCategory"),"from":{"type":"string","format":"date-time"},"to":{"type":"string","format":"date-time"}},25:{"status":enum("ELIGIBLE","ENROLLED","UNAVAILABLE"),"skill":text(40,1),"area":text(40,1)},34:{"state":enum("PUBLISHED","WITHDRAWN"),"category":ref("M07ServiceCategory"),"area":text(40,1)}}
    for name,schema in optional_filters.get(n,{}).items():
        params.append({"name":name,"in":"query","schema":schema})
        filters.append(name)
    guards = ["TENANT", "CURRENT_MEMBERSHIP", "CURRENT_PARENT_ACL"]
    if "CITIZEN" in roles:
        guards += ["CITIZEN_OWNED", "CITIZEN_SAFE_DTO"]
    if "TECHNICIAN" in roles:
        guards.append("TECHNICIAN_SELF" if n == 28 else "TECHNICIAN_ASSIGNED")
    if n in {26, 27, 39}:
        guards += ["RECENT_REAUTH", "GOVERNANCE_REASON"]
    if n in {40, 41}:
        guards.append("RECIPIENT_SELF")
    if n in {15,18,19,35}:
        guards.append("D5_CAPACITY_PROMISE_ONLY")
    if n in {18, 19, 23, 24, 29, 30, 31, 32, 33, 35}:
        guards += ["SORTED_LOCK_ORDER", "ATOMIC_ALLOCATION_CONSTRAINTS"]
    status = "201" if method == "post" and n in {1, 6, 9, 13, 15, 24, 26, 29, 31, 33, 35, 43} else "200"
    response_name = response if response == "Receipt" else "M07" + response
    op = {"operationId": f"m07_n{n:02d}", "summary": f"N{n:02d} {method.upper()} {suffix} — proposed only", "tags": ["M07 " + phase], "security": [{"sessionCookie": []}], "parameters": params, "x-roles": roles.split(","), "x-required-permission": permission, "x-scope": "Current tenant plus per-action own/assigned/self/role checks; see M07 permission contract", "x-authorization-guards": guards, "x-retry-policy": "READ_ONLY_POST" if n == 5 else "READ_ONLY" if method == "get" else "TENANT_7_DAY", "x-response-cache": "NO_STORE", "x-implementation-status": "PROPOSED_NOT_IMPLEMENTED", "x-m07-phase": phase, "x-version-target": target, "x-database-effect": ("Authorized projection only" if method == "get" or n == 5 else "Atomic state/history/audit/outbox; no external side effect before commit"), "responses": {status: {"description": "Proposed authorized result, not an implemented endpoint", "headers": {"Cache-Control": {"required": True, "schema": {"type": "string", "const": "no-store"}}}, "content": {"application/json": {"schema": ref(response_name)}}}, **{str(code): {"$ref": "#/components/responses/Error" + str(code)} for code in [400, 401, 403, 404, 409, 412, 413, 422, 428, 429, 503]}}}
    if request:
        op["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref("M07" + request)}}}
    if n == 5:
        op["x-idempotency-header"] = "REJECT_400"
    if n == 8:
        op["x-action-roles"] = {"WITHDRAW":["CITIZEN"],"REQUEST_CANCELLATION":["CITIZEN"],**{action:["SUPERVISOR"] for action in ["CANCEL","START_SERVICE","REQUEST_REVIEW","RETURN_TO_WORK","CLOSE"]}}
    if n == 24:
        op["x-action-roles"] = {**{action:["TECHNICIAN"] for action in ["CHECK_IN","VISIT_FINISHED","NO_ACCESS","ABORTED","OVERRUN_REPORTED"]},"ADMIN_CORRECTION":["SUPERVISOR"]}
    if n == 14:
        op["x-unconfigured-behavior"] = "EMPTY_WINDOWS_WITH_VISIBLE_UNCONFIGURED_REASON; preferences and cancellation remain usable"
    if n == 18:
        op["x-action-gates"] = {"CONFIRM_REQUESTED":"D5_CONFIGURED_CALENDAR","OFFER_ALTERNATIVE":"D5_CONFIGURED_CALENDAR","DECLINE":"CURRENT_AUTHORIZATION_ONLY"}
    projections = {
        2:{"CITIZEN":"M07Page_ServiceCaseCitizen","SUPERVISOR":"M07Page_ServiceCaseStaff"},
        3:{"CITIZEN":"M07ServiceCaseCitizen","SUPERVISOR":"M07ServiceCaseStaff"},
        4:{"CITIZEN":"M07PublicTimelinePage","SUPERVISOR":"M07InternalTimelinePage or M07PublicTimelinePage by audience"},
        8:{"CITIZEN":"M07ServiceCaseCitizen","SUPERVISOR":"M07ServiceCaseStaff"},
        16:{"CITIZEN":"M07Page_AppointmentRequestCitizen","SUPERVISOR":"M07Page_AppointmentRequestStaff"},
        17:{"CITIZEN":"M07AppointmentRequestCitizen","SUPERVISOR":"M07AppointmentRequestStaff"},
        18:{"SUPERVISOR":"M07StaffDecisionReceipt"},
        19:{"CITIZEN":"M07CitizenDecisionReceipt"},
        21:{"CITIZEN":"M07Page_AppointmentCitizen","SUPERVISOR":"M07Page_AppointmentStaff"},
        22:{"CITIZEN":"M07AppointmentCitizen","SUPERVISOR":"M07AppointmentStaff","TECHNICIAN":"M07AppointmentTechnician"},
        23:{"CITIZEN":"M07CitizenAppointmentCommandReceipt","SUPERVISOR":"M07StaffAppointmentCommandReceipt"},
        24:{"TECHNICIAN":"M07TechnicianVisitEventReceipt","SUPERVISOR":"M07StaffVisitEventReceipt"},
        28:{"TECHNICIAN":"M07TechnicianCalendarSnapshot","SUPERVISOR":"M07StaffCalendarSnapshot"}}
    if n in projections:
        op["x-role-projections"] = projections[n]
        # Role variants are explicit wire alternatives; the server chooses by
        # current authorization, never a request-body role or fields selector.
        variants = sorted({name for value in projections[n].values() for name in value.split() if name.startswith("M07")})
        wrapper = "M07N" + str(n).zfill(2) + "Response"
        op["x-response-variants"] = variants
        op["responses"][status]["content"]["application/json"]["schema"] = ref(wrapper)
    if method == "get" and n in {3, 11, 17, 22, 38, 40}:
        op["responses"][status]["headers"]["ETag"] = {"required": n != 11, "schema": text(100, 1), "description": "Resource version; unsupplied visit access omits child ETag and uses the service precondition plus null expected_access_version for first write."}
    entry = {"id": op["operationId"], "group": "M07 " + phase, "method": method, "path": O + suffix, "request": "M07" + request if request else None, "response": response_name, "roles": op["x-roles"], "scope": op["x-scope"], "effects": op["x-database-effect"], "table": table, "permission": permission, "list": False, "filters": filters, "restricted": False, "retry_policy": op["x-retry-policy"], "authorization_guards": guards, "status": "PROPOSED_NOT_IMPLEMENTED", "proposal_id": f"N{n:02d}", "phase": phase}
    return op, entry


def outputs():
    spec = read("docs/architecture/openapi-design.json")
    inventory = read("data/schemas/m02-api-inventory.json")
    spec["info"] = {"title": "HYDROOVERITY Operations API — M07 REVIEW CANDIDATE", "version": "0.2.0", "description": "Contract revision only, not a product rename. Baseline 117 operations plus 44 proposed operations. Running M03 still reads frozen M02 and implements 58. Nothing here is registered by the application."}
    spec["x-review-baseline"] = BASE
    spec["x-release-gates"] = {"scheduling": "DISABLED_UNTIL_AUTHORIZED_CONFIGURATION", "images": "DISABLED_UNTIL_SCANNER_PROCESSING_STORAGE_LICENSE_REVIEW", "external_delivery": "DISABLED", "offline": "DEFERRED", "documents": "DEFERRED", "retention_and_erasure": "OWNER_OPERATOR_REVIEW_REQUIRED", "scientific_verification": "NOT_VERIFIABLE_ONLY"}
    spec["components"]["schemas"].update(schemas())
    new = []
    for row in ROWS:
        op, entry = operation(row)
        if op.get("x-response-variants"):
            name = "M07N" + str(row[0]).zfill(2) + "Response"
            spec["components"]["schemas"][name] = {"anyOf":[ref(v) for v in op["x-response-variants"]]}
            entry["response"] = name
        spec["paths"].setdefault(entry["path"], {})[entry["method"]] = op
        new.append(entry)
    selected = reconcile_deferred(spec, inventory)
    # Reviewed future schema deltas are separate, not wired into the current
    # 58 paths. The actual runtime catalogue/source must stay byte-unchanged.
    future_work = copy.deepcopy(spec["components"]["schemas"]["WorkOrderWrite"])
    future_work["properties"]["task_purpose"] = ref("M07TaskPurpose")
    spec["components"]["schemas"]["M07FutureWorkOrderWrite"] = future_work
    from m07_model_design import database, states
    db = database(read("data/schemas/m02-database-design.json"))
    for name in ["ServiceCategory", "ServiceStatus", "AppointmentRequestStatus", "AppointmentStatus", "TaskPurpose"]:
        db["enums"]["M07" + name] = spec["components"]["schemas"]["M07" + name]["enum"]
    inv = {"status": "M07_PROPOSED_COMPOSED_CATALOGUE_NOT_RUNTIME", "baseline": BASE, "operations": inventory["operations"] + new}
    baseline = read("data/schemas/m03-implementation-matrix.json")
    implemented = {op["id"] for op in baseline["operations"] if op["status"] == "CODE_TESTED"}
    selected_ids = {op["id"] for op in selected}
    matrix = {"status":"CONTRACT_REVIEW_ONLY", "baseline":BASE,
              "counts":{"baseline_operations":117,"proposed_new_operations":44,"existing_deferred_selected":11,"composed_operations":len(inv["operations"]),"runtime_implemented_operations":58,"runtime_deferred_operations":59,"remaining_outside_m07":48,"baseline_design_tables":57,"proposed_new_tables":len(db["x-m07-new-tables"]),"composed_design_tables":len(db["tables"]),"runtime_migrated_tables":30},
              "operations":[{"id":op["id"],"method":op["method"],"path":op["path"],"classification":"BASELINE_CODE_TESTED_UNCHANGED" if op["id"] in implemented else "M07_EXISTING_DEFERRED_PROPOSED" if op["id"] in selected_ids else "M07_NEW_PROPOSED" if op in new else "OUTSIDE_M07_DEFERRED", "runtime_registered":op["id"] in implemented} for op in inv["operations"]],
              "future_runtime_deltas":[{"operation":"POST "+O+"/work-orders","candidate_schema":"M07FutureWorkOrderWrite","effect":"optional task_purpose; omitted stays REPAIR; INVESTIGATION requires findings; NOT applied to current operation or runtime"},{"operation":"existing assignment/transitions/actions/repairs","effect":"future scheduling, clean-image and purpose-specific submission guards; no current runtime behavior change"},{"operation":"existing WorkerBrief","effect":"retain 15-minute online scope; any future appointment/access enrichment requires coordinated API/frontend approval; no offline lease"}],
              "baseline_files": baseline_hashes(), "selected_deferred_ids":sorted(selected_ids)}
    routes = route_catalogue(new, selected)
    return {"docs/architecture/m07/openapi-proposed.json": spec,
            "data/schemas/m07-api-inventory.json": inv,
            "data/schemas/m07-database-design.json":db,
            "data/schemas/m07-state-machines.json":states(),
            "data/schemas/m07-reconciliation-matrix.json":matrix,
            "design/ui-ux/m07-route-catalog.json":routes}


def baseline_hashes():
    return read("data/schemas/m07-baseline-lock.json")["sha256"]


def reconcile_deferred(spec, inventory):
    all_schemas = spec["components"]["schemas"]
    selected = []
    for entry in inventory["operations"]:
        if entry["group"] not in {"Feedback", "Uploads", "Notifications"}:
            continue
        op = spec["paths"][entry["path"]][entry["method"]]
        selected.append(entry)
        entry.update({"status":"PROPOSED_NOT_IMPLEMENTED","phase":"M07-C"})
        op.update({"x-implementation-status":"PROPOSED_NOT_IMPLEMENTED","x-m07-phase":"M07-C","x-response-cache":"NO_STORE"})
        # Clone every DTO/page reachable from selected operations so legacy
        # M02 components used by existing runtime routes are never altered.
        def clone(name):
            target = "M07" + name
            if target in all_schemas:
                return target
            original = copy.deepcopy(all_schemas[name])
            all_schemas[target] = original
            def walk(node):
                if isinstance(node,dict):
                    if node.get("$ref","").startswith("#/components/schemas/"):
                        old = node["$ref"].rsplit("/",1)[1]
                        if old not in {"Receipt","Error"}:
                            node["$ref"] = "#/components/schemas/" + clone(old)
                    for value in node.values():
                        walk(value)
                elif isinstance(node,list):
                    for value in node: walk(value)
            walk(original)
            return target
        if entry["request"] and entry["request"] != "BINARY":
            name = clone(entry["request"])
            entry["request"] = name
            op["requestBody"]["content"]["application/json"]["schema"] = ref(name)
        if entry["response"] != "BINARY":
            original = ("Page_" if entry["list"] else "") + entry["response"]
            name = clone(original) if original != "Receipt" else "Receipt"
            for code,value in op["responses"].items():
                if code.startswith("2"):
                    value["content"]["application/json"]["schema"] = ref(name)
            entry["response"],entry["list"] = name,False
        if entry["method"] == "get":
            for code,value in op["responses"].items():
                if code.startswith("2") and "application/json" in value.get("content",{}):
                    value.setdefault("headers",{})["ETag"] = {"schema":text(100,1),"description":"Mutable entity version when applicable; list items expose their own versions"}
        if entry["path"].endswith(("/read","/review")) or entry["method"] == "delete":
            if not any(p["name"] == "If-Match" for p in op["parameters"]):
                op["parameters"].append({"name":"If-Match","in":"header","required":True,"schema":{"type":"string","pattern":'^"[1-9][0-9]*"$'}})
        entry["authorization_guards"] = op["x-authorization-guards"]
        if entry["group"] == "Uploads":
            op["x-authorization-guards"] += ["CURRENT_PARENT_ACL","CLEAN_DERIVATIVE_ONLY","IMAGE_REVIEW_GATE"]
            op["x-max-body-bytes"] = 5242880 if entry["request"] == "BINARY" else 16384
        if entry["path"].endswith("/complete"):
            success = next(k for k in op["responses"] if k.startswith("2"))
            value = op["responses"].pop(success)
            value["description"] = "Persisted completion receipt; quarantined until scan/processing succeeds, never fake CLEAN"
            op["responses"]["202"] = value
        if entry["path"].endswith("/feedback") and entry["method"] == "get":
            op["parameters"].append({"name":"service_request_id","in":"query","schema":{"type":"string","format":"uuid"}})
            entry["filters"].append("service_request_id")
    assert len(selected) == 11, "Unexpected deferred-group inventory; review exact selection"
    for name in ["M07Feedback","M07Notification","M07Attachment"]:
        all_schemas[name]["properties"]["version"] = integer()
        all_schemas[name]["required"].append("version")
    all_schemas["M07FeedbackWrite"]["properties"].update({"service_request_id":nullable({"type":"string","format":"uuid"}),"service_rating":nullable(integer(5))})
    all_schemas["M07Feedback"]["properties"].update({"service_request_id":nullable({"type":"string","format":"uuid"}),"service_rating":nullable(integer(5))})
    upload = all_schemas["M07UploadStart"]["properties"]
    upload["purpose"] = enum("COMPLAINT","WORK_ORDER","REPAIR","FEEDBACK","SERVICE_REQUEST")
    upload["media_type"] = enum("image/jpeg","image/png","image/webp")
    upload["target_id"] = {"type":"string","format":"uuid"}
    assert upload["size_bytes"]["maximum"] == 5242880
    return selected


def route_catalogue(new, selected):
    routes = read("design/ui-ux/m02-route-catalog.json")
    routes["status"] = "M07_PROPOSED_ROUTES_NOT_RUNTIME"
    ids = {entry["proposal_id"]:entry["id"] for entry in new}
    for page in routes["pages"]:
        extra = []
        if page["id"] == "PAGE-37": extra = [ids[f"N{i:02d}"] for i in range(14,40)]
        if page["id"] == "PAGE-34": extra = [ids[k] for k in ["N22","N24","N43","N44"]]
        if page["id"] == "PAGE-43": extra = [ids[k] for k in ["N40","N41"]]
        if page["id"] == "PAGE-45": extra = [ids[k] for k in ["N26","N27","N38","N39"]]
        if extra:
            page["x-m07-proposed-operations"] = extra
            page["x-m07-status"] = "PROPOSED_NOT_ROUTED"
    for number,path,roles,keys,objective in [
        (47,"/citizen/{org}/service-requests","CITIZEN",[1,2,5],"Read own service receipts and authenticated reference lookup"),
        (48,"/citizen/{org}/service-requests/new","CITIZEN",[1],"Submit service review, no automatic acceptance or incident"),
        (49,"/citizen/{org}/service-requests/{id}","CITIZEN",[3,4,6,8,10,11,12,14,15,16,17,19,20,21,22,23],"Own timeline, access preferences and explicit appointment decisions"),
        (50,"/app/{org}/service-requests","SUPERVISOR",[2,5],"Triage tenant service queue"),
        (51,"/app/{org}/service-requests/{id}","SUPERVISOR",[3,4,7,8,9,11,13,16,17,18,21,22,23,42],"Review safe/internal context and manage service commitments")]:
        routes["pages"].append({"id":f"PAGE-{number}","route":path,"roles":roles,"objective":objective,"data":objective,"operations":[ids[f"N{i:02d}"] for i in keys],"offline":"ONLINE_ONLY; no persistent private drafts or queued writes","status":"PROPOSED_NOT_ROUTED"})
    return routes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, data in outputs().items():
        p = ROOT / path
        if args.check:
            assert read(path) == data, "Generated M07 contract drift: " + path
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            # One reviewable line per JSON top-level field is not necessary;
            # compact JSON keeps the composed spec below the existing 1 MiB gate.
            p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print("PASS: reproducible M07 review contracts; runtime artifacts not modified")


if __name__ == "__main__":
    main()
