"""One durable event queue, explicit utility principal, safe in-app delivery only."""

import json
from datetime import timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from .db import context, execute, one, principal_is_safe, query
from .errors import require
from .security import now

TEMPLATES = {
    "COMPLAINT_PROGRESS": "A report update is available. Open your report timeline for the current status.",
    "SERVICE_PROGRESS": "A service progress update is available. Open your service timeline for the current status.",
    "APPOINTMENT": "An appointment update is available. Open your service record for the current visit status.",
    "WORK_ASSIGNMENT": "Your assigned work has an update. Check your current task and agenda before taking action.",
    "SERVICE_FEEDBACK": "A feedback response is available. Open your feedback history to read it.",
}
SOURCE_TABLES = {
    "citizen_complaints",
    "complaint_status_events",
    "service_requests",
    "service_public_updates",
    "appointments",
    "appointment_requests",
    "work_orders",
    "feedback_items",
}


def enqueue(c, organization, event, table, identifier, action):
    """Capture minimal recipients/versions atomically with the business state, not text."""
    if table not in SOURCE_TABLES:
        return
    if table == "feedback_items" and not action.endswith("_review"):
        return
    source = one(
        c, f"SELECT * FROM {table} WHERE organization_id=:o AND id=:i", o=organization, i=identifier
    )
    if not source:
        return
    if table == "complaint_status_events":
        source = one(
            c,
            "SELECT * FROM citizen_complaints WHERE organization_id=:o AND id=:i",
            o=organization,
            i=source["complaint_id"],
        )
        if not source:
            return
        table = "citizen_complaints"
    if table == "service_public_updates":
        source = one(
            c,
            "SELECT * FROM service_requests WHERE organization_id=:o AND id=:i",
            o=organization,
            i=source["request_id"],
        )
        table = "service_requests"
    if table == "appointment_requests" and source.get("confirmed_appointment_id"):
        source = one(
            c,
            "SELECT * FROM appointments WHERE id=:i AND organization_id=:o",
            i=source["confirmed_appointment_id"],
            o=organization,
        )
        table = "appointments"
    targets = []
    if table == "citizen_complaints":
        targets.append((source["reporter_id"], None, "COMPLAINT_PROGRESS"))
    elif table == "service_requests":
        targets.append((source["owner_membership_id"], source["id"], "SERVICE_PROGRESS"))
    elif table in {"appointments", "appointment_requests"}:
        case = one(
            c,
            "SELECT owner_membership_id FROM service_requests WHERE id=:i",
            i=source["request_id"],
        )
        targets.append(
            (case["owner_membership_id"] if case else None, source["request_id"], "APPOINTMENT")
        )
        if table == "appointments" and source.get("assignee_id"):
            targets.append((source["assignee_id"], source["request_id"], "WORK_ASSIGNMENT"))
    elif table == "work_orders" and source.get("assignee_id"):
        targets.append((source["assignee_id"], None, "WORK_ASSIGNMENT"))
    elif table == "feedback_items":
        targets.append(
            (source["owner_membership_id"], source["service_request_id"], "SERVICE_FEEDBACK")
        )
    if not targets:
        return
    safe = [
        {
            "recipient_id": str(member) if member else None,
            "service_request_id": str(case) if case else None,
            "resource_type": table,
            "resource_id": str(source["id"]),
            "resource_version": source["version"],
            "event_category": category,
        }
        for member, case, category in targets
    ]
    execute(
        c,
        "INSERT INTO background_jobs(organization_id,domain_event_id,kind,targets) VALUES(:o,:e,'NOTIFICATION_FANOUT',CAST(:targets AS jsonb))",
        o=organization,
        e=event,
        targets=json.dumps(safe),
    )


def inbox_access_sql():
    # Correlated RLS-filtered parent reads; assignment is rechecked even for delivered inbox rows.
    return """EXISTS(SELECT 1 FROM role_assignments ra JOIN role_permissions rp ON rp.role_id=ra.role_id JOIN permissions p ON p.id=rp.permission_id WHERE ra.membership_id=notifications.recipient_id AND ra.revoked_at IS NULL AND p.code=CASE notifications.resource_type WHEN 'citizen_complaints' THEN 'complaints.read' WHEN 'service_requests' THEN 'service_requests.read' WHEN 'feedback_items' THEN 'feedback.read' WHEN 'work_orders' THEN 'work_orders.read' ELSE 'dispatch.read' END) AND (
      (resource_type='citizen_complaints' AND EXISTS(SELECT 1 FROM citizen_complaints c WHERE c.id=notifications.resource_id AND c.reporter_id=notifications.recipient_id)) OR
      (resource_type='service_requests' AND EXISTS(SELECT 1 FROM service_requests s WHERE s.id=notifications.resource_id AND s.owner_membership_id=notifications.recipient_id)) OR
      (resource_type='feedback_items' AND EXISTS(SELECT 1 FROM feedback_items f WHERE f.id=notifications.resource_id AND f.owner_membership_id=notifications.recipient_id)) OR
      (resource_type='work_orders' AND hydro_m07_role(ARRAY['TECHNICIAN']) AND EXISTS(SELECT 1 FROM work_orders w WHERE w.id=notifications.resource_id AND w.assignee_id=notifications.recipient_id)) OR
      (resource_type='appointment_requests' AND EXISTS(SELECT 1 FROM appointment_requests a JOIN service_requests s ON s.id=a.request_id WHERE a.id=notifications.resource_id AND s.owner_membership_id=notifications.recipient_id)) OR
      (resource_type='appointments' AND EXISTS(SELECT 1 FROM appointments a WHERE a.id=notifications.resource_id AND (
        EXISTS(SELECT 1 FROM service_requests s WHERE s.id=a.request_id AND s.owner_membership_id=notifications.recipient_id) OR
        (hydro_m07_role(ARRAY['TECHNICIAN']) AND a.assignee_id=notifications.recipient_id AND EXISTS(SELECT 1 FROM work_orders w WHERE w.id=a.work_order_id AND w.assignee_id=a.assignee_id AND w.assignment_version=a.assignment_version)))))
    )"""


def authorized_target(c, target, member, exact_version=False):
    table = target["resource_type"]
    if table not in SOURCE_TABLES - {"service_public_updates", "complaint_status_events"}:
        return False
    permission = {
        "citizen_complaints": "complaints.read",
        "service_requests": "service_requests.read",
        "feedback_items": "feedback.read",
        "work_orders": "work_orders.read",
        "appointments": "dispatch.read",
        "appointment_requests": "dispatch.read",
    }[table]
    allowed = one(
        c,
        "SELECT EXISTS(SELECT 1 FROM role_assignments a JOIN role_permissions rp ON rp.role_id=a.role_id JOIN permissions p ON p.id=rp.permission_id WHERE a.membership_id=:m AND a.revoked_at IS NULL AND p.code=:p) AS ok",
        m=member,
        p=permission,
    )["ok"]
    if not allowed:
        return False
    resource = one(c, f"SELECT * FROM {table} WHERE id=:i", i=target["resource_id"])
    if not resource or (exact_version and resource["version"] != target["resource_version"]):
        return False
    if table == "citizen_complaints":
        return str(resource["reporter_id"]) == str(member)
    if table in {"service_requests", "feedback_items"}:
        return str(resource["owner_membership_id"]) == str(member)
    if table in {"appointment_requests", "appointments"}:
        case = one(
            c,
            "SELECT owner_membership_id FROM service_requests WHERE id=:i",
            i=resource["request_id"],
        )
        if case and str(case["owner_membership_id"]) == str(member):
            return True
        if table == "appointment_requests":
            return False
        work = one(c, "SELECT * FROM work_orders WHERE id=:i", i=resource["work_order_id"])
        return bool(
            work
            and str(resource["assignee_id"]) == str(member)
            and work["assignee_id"] == resource["assignee_id"]
            and work["assignment_version"] == resource["assignment_version"]
            and one(c, "SELECT hydro_m07_role(ARRAY['TECHNICIAN']) AS ok")["ok"]
        )
    return (
        str(resource["assignee_id"]) == str(member)
        and one(c, "SELECT hydro_m07_role(ARRAY['TECHNICIAN']) AS ok")["ok"]
    )


def quiet_until(preferences, instant):
    quiet = preferences.get("quiet_hours")
    if not quiet:
        return None
    local = instant.astimezone(ZoneInfo("Asia/Kolkata"))
    start, end = quiet["start_local"], quiet["end_local"]
    current = local.strftime("%H:%M")
    active = start <= current < end if start < end else current >= start or current < end
    if not active:
        return None
    hour, minute = map(int, end.split(":"))
    deadline = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if deadline <= local:
        deadline += timedelta(days=1)
    return deadline


def worker_scope(c, user, organization):
    require(principal_is_safe(c), 503, "UNSAFE_DATABASE_PRINCIPAL", "Unsafe worker identity")
    context(c, user, organization)
    execute(
        c,
        "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
        key="hydro-dispatch:" + str(organization),
    )
    member = one(
        c,
        "SELECT m.id FROM organization_memberships m JOIN organizations o ON o.id=m.organization_id JOIN users u ON u.id=m.user_id AND u.deactivated_at IS NULL WHERE m.user_id=:u AND m.organization_id=:o AND m.status='ACTIVE' AND o.status='ACTIVE' FOR SHARE OF m",
        u=user,
        o=organization,
    )
    require(
        member and one(c, "SELECT hydro_m07_role(ARRAY['SUPERVISOR']) AS ok")["ok"],
        403,
        "WORKER_SCOPE_REQUIRED",
        "Worker requires a currently authorized utility supervisor",
    )
    # Hold current role grants through the transaction, as API authorization does.
    query(
        c,
        "SELECT a.id FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL AND r.code='SUPERVISOR' FOR SHARE OF a",
        m=member["id"],
    )


def resource_path(target):
    # Existing frontend route names are resolved by the client from these API-relative links.
    table = target["resource_type"]
    return (
        "/"
        + {
            "citizen_complaints": "complaints",
            "service_requests": "service-requests",
            "feedback_items": "feedback",
            "work_orders": "work-orders",
            "appointments": "appointments",
            "appointment_requests": "appointment-requests",
        }[table]
        + "/"
        + str(target["resource_id"])
    )


def intent(c, job, target, organization):
    if target["recipient_id"] is None:
        case = one(
            c,
            "SELECT owner_membership_id FROM service_requests WHERE organization_id=:o AND id=:i",
            o=organization,
            i=target["service_request_id"],
        )
        require(case, 409, "PARENT_UNAVAILABLE", "Notification parent unavailable")
        target["recipient_id"] = str(case["owner_membership_id"])
    return one(
        c,
        "INSERT INTO notifications(organization_id,recipient_id,domain_event_id,service_request_id,template_version,channel,event_category,resource_type,resource_id,resource_version,message,resource_path) VALUES(:o,:m,:e,:s,'M07C-1','IN_APP',:category,:table,:resource,:version,:message,:path) ON CONFLICT(organization_id,recipient_id,domain_event_id,template_version,channel) DO UPDATE SET template_version=EXCLUDED.template_version RETURNING *",
        o=organization,
        m=target["recipient_id"],
        e=job["domain_event_id"],
        s=target["service_request_id"],
        category=target["event_category"],
        table=target["resource_type"],
        resource=target["resource_id"],
        version=target["resource_version"],
        message=TEMPLATES[target["event_category"]],
        path=resource_path(target),
    )


def deliver(c, job, user, organization):
    deferred = []
    for target in job["targets"]:
        notification = intent(c, job, target, organization)
        if notification["state"] in {"DELIVERED", "SUPPRESSED", "FAILED"}:
            continue
        member = one(
            c,
            "SELECT * FROM organization_memberships WHERE id=:m AND organization_id=:o FOR SHARE",
            m=target["recipient_id"],
            o=organization,
        )
        permitted, preferences = False, None
        if member and member["status"] == "ACTIVE":
            context(c, member["user_id"], organization)
            permissions = query(
                c,
                "SELECT p.code FROM role_assignments a JOIN role_permissions rp ON rp.role_id=a.role_id JOIN permissions p ON p.id=rp.permission_id WHERE a.membership_id=:m AND a.revoked_at IS NULL FOR SHARE OF a",
                m=member["id"],
            )
            active_user = one(
                c,
                "SELECT id FROM users WHERE id=:u AND deactivated_at IS NULL",
                u=member["user_id"],
            )
            permitted = (
                bool(active_user)
                and any(p["code"] == "notifications.read" for p in permissions)
                and authorized_target(c, target, member["id"], True)
            )
            preferences = one(
                c,
                "SELECT * FROM notification_preferences WHERE membership_id=:m FOR SHARE",
                m=member["id"],
            )
            context(c, user, organization)
        enabled = (
            preferences
            and preferences["in_app"]
            and target["event_category"] in preferences["event_categories"]
        )
        quiet = quiet_until(preferences, now()) if permitted and enabled else None
        if quiet:
            execute(
                c,
                "UPDATE notifications SET state='RETRY_WAIT',next_attempt_at=:time,safe_error_code='QUIET_HOURS' WHERE id=:i",
                time=quiet,
                i=notification["id"],
            )
            deferred.append(quiet)
            continue
        if not permitted or not enabled:
            execute(
                c,
                "UPDATE notifications SET state='SUPPRESSED',safe_error_code=:code,next_attempt_at=NULL WHERE id=:i",
                code="RECIPIENT_UNAVAILABLE" if not permitted else "PREFERENCES_DISABLED",
                i=notification["id"],
            )
            continue
        attempt = notification["attempt_number"] + 1
        require(attempt <= 3, 409, "ATTEMPTS_EXHAUSTED", "Delivery attempts exhausted")
        execute(
            c,
            "UPDATE notifications SET state='DELIVERED',delivered_at=now(),attempted_at=now(),attempt_number=:n,next_attempt_at=NULL,safe_error_code=NULL,updated_at=now() WHERE id=:i",
            i=notification["id"],
            n=attempt,
        )
        execute(
            c,
            "INSERT INTO notification_delivery_attempts(organization_id,notification_id,attempt_number,state) VALUES(:o,:i,:n,'DELIVERED')",
            o=organization,
            i=notification["id"],
            n=attempt,
        )
    return min(deferred) if deferred else None


def failed_attempt(c, job, code, next_time=None):
    for n in query(
        c,
        "SELECT * FROM notifications WHERE domain_event_id=:e AND state NOT IN ('DELIVERED','SUPPRESSED','FAILED') FOR UPDATE",
        e=job["domain_event_id"],
    ):
        attempt = n["attempt_number"] + 1
        if attempt > 3:
            continue
        execute(
            c,
            "UPDATE notifications SET state=:state,attempt_number=:attempt,attempted_at=now(),next_attempt_at=:next,safe_error_code=:code WHERE id=:i",
            i=n["id"],
            state="RETRY_WAIT" if next_time else "FAILED",
            attempt=attempt,
            next=next_time,
            code=code,
        )
        execute(
            c,
            "INSERT INTO notification_delivery_attempts(organization_id,notification_id,attempt_number,state,safe_error_code) VALUES(:o,:i,:a,:state,:code)",
            o=n["organization_id"],
            i=n["id"],
            a=attempt,
            state="RETRY_WAIT" if next_time else "FAILED",
            code=code,
        )


def run_once(engine, user, organization, retry_delays=None, retry_policy_reference=None):
    """Process at most one event. Explicit reviewed retry configuration has two delays.

    Claim commits separately; token fencing and row locking prevent duplicate completion.
    The lease is a technical recovery bound, not an invented delivery retry policy.
    """
    user, organization = UUID(str(user)), UUID(str(organization))
    require(
        retry_delays is None
        or (
            retry_policy_reference
            and len(retry_delays) == 2
            and all(type(n) is int and 0 < n <= 86400 for n in retry_delays)
        ),
        422,
        "RETRY_POLICY_REQUIRED",
        "Two reviewed retry delays and a policy reference are required",
    )
    with engine.begin() as c:
        worker_scope(c, user, organization)
        job = one(
            c,
            "SELECT * FROM background_jobs WHERE organization_id=:o AND ((state='QUEUED' AND (next_attempt_at IS NULL OR next_attempt_at<=now())) OR (state='RUNNING' AND lease_until<now())) ORDER BY created_at,id FOR UPDATE SKIP LOCKED LIMIT 1",
            o=organization,
        )
        if not job:
            return "IDLE"
        if job["state"] == "RUNNING":
            if retry_delays is None or job["attempts"] >= 3:
                execute(
                    c,
                    "UPDATE background_jobs SET state='FAILED',lease_token=NULL,lease_until=NULL,safe_error_code=:code WHERE id=:i",
                    i=job["id"],
                    code="RETRY_POLICY_UNCONFIGURED"
                    if retry_delays is None
                    else "ATTEMPTS_EXHAUSTED",
                )
            else:
                execute(
                    c,
                    "UPDATE background_jobs SET state='QUEUED',lease_token=NULL,lease_until=NULL,next_attempt_at=:time,safe_error_code='LEASE_EXPIRED' WHERE id=:i",
                    i=job["id"],
                    time=now() + timedelta(seconds=retry_delays[job["attempts"] - 1]),
                )
            recovered = one(c, "SELECT * FROM background_jobs WHERE id=:i", i=job["id"])
            failed_attempt(
                c,
                job,
                recovered["safe_error_code"],
                recovered["next_attempt_at"] if recovered["state"] == "QUEUED" else None,
            )
            return "RECOVERED"
        for target in job["targets"]:
            intent(c, job, target, organization)
        token = uuid4()
        execute(
            c,
            "UPDATE background_jobs SET state='RUNNING',lease_token=:token,lease_until=now()+interval '60 seconds',attempts=attempts+1,updated_at=now() WHERE id=:i",
            i=job["id"],
            token=token,
        )
    try:
        with engine.begin() as c:
            worker_scope(c, user, organization)
            current = one(
                c,
                "SELECT * FROM background_jobs WHERE id=:i AND state='RUNNING' AND lease_token=:token AND lease_until>now() FOR UPDATE",
                i=job["id"],
                token=token,
            )
            if not current:
                return "LEASE_LOST"
            deferred = deliver(c, current, user, organization)
            execute(
                c,
                "UPDATE background_jobs SET state=:state,lease_token=NULL,lease_until=NULL,next_attempt_at=:next,attempts=attempts-:postponed,safe_error_code=NULL,updated_at=now() WHERE id=:i",
                i=current["id"],
                state="QUEUED" if deferred else "SUCCEEDED",
                next=deferred,
                postponed=1 if deferred else 0,
            )
            return "DEFERRED" if deferred else "SUCCEEDED"
    except Exception:
        # Failed delivery transaction rolls back atomically; never claim delivery.
        # If the database itself is unavailable, the durable expired lease handles recovery.
        with engine.begin() as c:
            worker_scope(c, user, organization)
            current = one(
                c,
                "SELECT * FROM background_jobs WHERE id=:i AND state='RUNNING' AND lease_token=:token FOR UPDATE",
                i=job["id"],
                token=token,
            )
            if current:
                retry = retry_delays is not None and current["attempts"] < 3
                execute(
                    c,
                    "UPDATE background_jobs SET state=:state,lease_token=NULL,lease_until=NULL,next_attempt_at=:next,safe_error_code=:code WHERE id=:i",
                    i=current["id"],
                    state="QUEUED" if retry else "FAILED",
                    next=now() + timedelta(seconds=retry_delays[current["attempts"] - 1])
                    if retry
                    else None,
                    code="DELIVERY_FAILED"
                    if retry
                    else "RETRY_POLICY_UNCONFIGURED"
                    if retry_delays is None
                    else "ATTEMPTS_EXHAUSTED",
                )
                failed = one(c, "SELECT * FROM background_jobs WHERE id=:i", i=job["id"])
                failed_attempt(
                    c,
                    current,
                    failed["safe_error_code"],
                    failed["next_attempt_at"] if retry else None,
                )
        return "FAILED"
