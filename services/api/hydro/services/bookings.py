"""Atomic bookings, safe role projections, and explicit capacity eligibility."""

import json
from datetime import timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

from psycopg.types.range import Range

from ..db import execute, one, query
from ..errors import Problem, require
from ..repository import change as legacy_change
from ..repository import insert as legacy_insert
from ..security import now
from ..tenant import receipt
from .scheduling import Scheduler, instant, version, write
from .service_requests import TERMINAL, Foundation
from .service_requests import change as case_change

LIVE = {"CONFIRMED", "CHECKED_IN"}
FINAL_WORK = {"COMPLETED", "CANCELLED"}


class Bookings(Scheduler):
    def staff(self):
        return "SUPERVISOR" in self.s.roles

    def case(self, identifier):
        row = one(
            self.c,
            "SELECT * FROM service_requests WHERE organization_id=:o AND id=:i FOR UPDATE",
            o=self.o,
            i=identifier,
        )
        require(
            row and (self.staff() or row["owner_membership_id"] == self.s.member_id),
            404,
            "NOT_FOUND",
            "Service unavailable",
        )
        execute(self.c, "SELECT set_config('hydro.dispatch_service',:i,true)", i=str(row["id"]))
        return row

    def appointment(self, identifier):
        row = self.row("appointments", identifier)
        if self.staff():
            return row
        if "TECHNICIAN" in self.s.roles and self.s.op["id"] in {"m07_n22", "m07_n24"}:
            work = self.s.work(row["work_order_id"], True, assigned=True)
            require(
                row["assignee_id"] == self.s.member_id
                and row["assignment_version"] == work["assignment_version"],
                409,
                "ASSIGNMENT_CHANGED",
                "Visit assignment changed; refresh your agenda",
            )
        else:
            self.case(row["request_id"])
        return row

    def result_table(self, op):
        n = int(op.rsplit("n", 1)[1])
        if n in {15, 18, 19, 20}:
            return "appointment_requests"
        if n in {23, 24}:
            return "appointments"
        if n in {35, 36}:
            return "appointment_windows"
        if n in {26, 27}:
            return "dispatch_technician_profiles"
        if n in {29, 30}:
            return "dispatch_shifts"
        return "dispatch_policy" if n == 39 else "dispatch_allocations"

    def replay(self, table, row, prior, body):
        op = self.s.op["id"]
        if table == "appointment_requests":
            self.case(row["request_id"])
            return (
                self.decision_receipt(row)
                if op in {"m07_n18", "m07_n19"}
                else self.projection(table, row)
            )
        if table == "appointments":
            self.appointment(row["id"])
            if op == "m07_n24":
                event = one(
                    self.c,
                    "SELECT * FROM appointment_events WHERE appointment_id=:a AND actor_id=:m AND operation_id=:k",
                    a=row["id"],
                    m=self.s.member_id,
                    k=body["operation_id"],
                )
                return {"receipt": receipt(event), "appointment": self.projection(table, row)}
            return self.command_receipt(row)
        return self.projection(table, row)

    def page(self, rows, project):
        # Keyset cursor is scoped to actor, role, query and current calendar revision.
        from ..dispatch import global_page

        request = self.s.auth.request
        original = request.state.global_scope if hasattr(request.state, "global_scope") else None
        request.state.global_scope = json.dumps(
            [
                str(self.o),
                str(self.s.member_id),
                sorted(self.s.roles),
                self.s.op["path"],
                self.s.params,
                {k: v for k, v in request.query_params.items() if k not in {"cursor", "limit"}},
            ],
            sort_keys=True,
            default=str,
        )
        # global_page permits limit/cursor only; filters were already applied server-side.
        from starlette.requests import Request

        filtered = [
            (k, v) for k, v in request.query_params.multi_items() if k in {"limit", "cursor"}
        ]
        from urllib.parse import urlencode

        page_request = Request({**request.scope, "query_string": urlencode(filtered).encode()})
        result = global_page(rows, page_request)
        result["items"] = [project(r) for r in result["items"]]
        request.state.global_scope = original
        return result

    def unplanned(self, profile, exclude=None):
        return one(
            self.c,
            "SELECT count(*) AS n FROM work_orders w WHERE w.organization_id=:o AND w.assignee_id=:m AND w.status NOT IN ('COMPLETED','CANCELLED') AND (CAST(:exclude AS uuid) IS NULL OR w.id<>CAST(:exclude AS uuid)) AND NOT EXISTS(SELECT 1 FROM dispatch_allocations a WHERE a.work_order_id=w.id AND a.active)",
            o=self.o,
            m=profile["membership_id"],
            exclude=str(exclude) if exclude else None,
        )["n"]

    def health(self, profile):
        if not self.policy()["configured"]:
            return "UNCONFIGURED"
        try:
            self.eligible(profile)
        except Problem:
            return "REVIEW_REQUIRED"
        impacted = one(
            self.c,
            "SELECT a.id FROM appointments a JOIN service_work_order_links l ON l.request_id=a.request_id AND l.work_order_id=a.work_order_id WHERE a.assignee_id=:m AND a.status IN ('CONFIRMED','CHECKED_IN') AND (l.dispatch_service_area_code NOT IN (SELECT jsonb_array_elements_text(CAST(:areas AS jsonb))) OR NOT l.dispatch_required_skill_codes <@ CAST(:skills AS jsonb)) LIMIT 1",
            m=profile["membership_id"],
            areas=json.dumps(profile["service_area_codes"]),
            skills=json.dumps(profile["skill_codes"]),
        )
        if impacted:
            return "REVIEW_REQUIRED"
        return "UNPLANNED_WORK" if self.unplanned(profile) else "READY"

    def linked_work(self, case, window, requested=None):
        links = query(self.c, "SELECT * FROM hydro_dispatch_case_links(:r)", r=case["id"])
        profile = self.row("dispatch_technician_profiles", window["profile_id"])
        for link in links:
            if requested and str(link["work_order_id"]) != str(requested):
                continue
            if link["dispatch_service_area_code"] not in window["service_area_codes"]:
                continue
            skills = link["dispatch_required_skill_codes"]
            if not skills or not set(skills) <= set(profile["skill_codes"]):
                continue
            work = self.s.row("work_orders", link["work_order_id"], True)
            incident = self.s.row("incidents", work["incident_id"])
            if (
                work["status"] not in FINAL_WORK
                and work["workspace_mode"] == incident["workspace_mode"] == "OPERATIONAL"
                and incident["status"]
                in {"ACCEPTED", "IN_PROGRESS", "REOPENED", "INVESTIGATION_REQUIRED"}
            ):
                return work
        require(
            False,
            409,
            "DISPATCH_REVIEW_REQUIRED",
            "A triaged operational work link with reviewed service area and skills is required",
        )

    def bounds(self, window):
        return (
            window["arrival_start"] - timedelta(minutes=window["before_buffer_minutes"]),
            window["arrival_end"]
            + timedelta(
                minutes=window["service_duration_minutes"] + window["after_buffer_minutes"]
            ),
        )

    def capacity(self, profile, start, end, exclude=None):
        require(
            one(
                self.c,
                "SELECT id FROM dispatch_shifts WHERE profile_id=:p AND status='ACTIVE' AND starts_at<=:s AND ends_at>=:e",
                p=profile["id"],
                s=start,
                e=end,
            ),
            409,
            "OUTSIDE_SHIFT",
            "The complete visit and buffers must fit an authorized shift",
        )
        require(
            not one(
                self.c,
                "SELECT id FROM dispatch_allocations WHERE profile_id=:p AND active AND occupied_range && tstzrange(:s,:e,'[)') AND (CAST(:exclude AS uuid) IS NULL OR appointment_id IS DISTINCT FROM CAST(:exclude AS uuid)) LIMIT 1",
                p=profile["id"],
                s=start,
                e=end,
                exclude=str(exclude) if exclude else None,
            ),
            409,
            "SCHEDULE_CONFLICT",
            "The requested interval is no longer available",
        )
        policy = self.policy()
        cap = min(profile["max_daily_minutes"], policy["max_daily_minutes"])
        local = ZoneInfo("Asia/Kolkata")
        day = start.astimezone(local).replace(hour=0, minute=0, second=0, microsecond=0)
        while day < end:
            nextday = day + timedelta(days=1)
            reserved = one(
                self.c,
                "SELECT coalesce(sum(extract(epoch FROM (least(upper(occupied_range),:e)-greatest(lower(occupied_range),:s)))/60),0) AS minutes FROM dispatch_allocations WHERE profile_id=:p AND active AND kind<>'UNAVAILABLE' AND occupied_range && tstzrange(:s,:e,'[)') AND (CAST(:exclude AS uuid) IS NULL OR appointment_id IS DISTINCT FROM CAST(:exclude AS uuid))",
                p=profile["id"],
                s=day,
                e=nextday,
                exclude=str(exclude) if exclude else None,
            )["minutes"]
            proposed = (min(end, nextday) - max(start, day)).total_seconds() / 60
            require(
                float(reserved) + proposed <= cap,
                409,
                "DAILY_CAP",
                "The interval exceeds the reviewed daily capacity",
            )
            day = nextday

    def available(self, window, case=None, exclude=None, work=None):
        policy = self.policy()
        require(
            policy["configured"] and policy["booking_enabled"],
            409,
            "SCHEDULING_DISABLED",
            "Scheduling is disabled until authorized utility policy and staff configuration are complete",
        )
        require(
            window["state"] == "PUBLISHED", 409, "WINDOW_WITHDRAWN", "Window is no longer published"
        )
        require(
            window["policy_version"] == policy["version"],
            409,
            "POLICY_CHANGED",
            "Utility policy changed; the window requires review",
        )
        require(
            now() + timedelta(minutes=policy["minimum_lead_minutes"])
            <= window["arrival_start"]
            <= now() + timedelta(days=policy["horizon_days"]),
            409,
            "WINDOW_EXPIRED",
            "Window is outside the configured lead time or horizon",
        )
        profile = self.row("dispatch_technician_profiles", window["profile_id"])
        self.eligible(profile)
        require(
            not one(
                self.c,
                "SELECT id FROM appointments WHERE assignee_id=:m AND status='CHECKED_IN' LIMIT 1",
                m=profile["membership_id"],
            ),
            409,
            "ACTIVE_VISIT_REVIEW",
            "An active checked-in visit requires completion or explicit replanning",
        )
        require(
            set(window["service_area_codes"]) <= set(profile["service_area_codes"]),
            409,
            "ELIGIBILITY_CHANGED",
            "Staff service areas changed",
        )
        if case:
            require(
                case["status"] not in TERMINAL
                and case["accepted_at"] is not None
                and not case["cancellation_pending"]
                and case["category"] in window["category_codes"],
                409,
                "SERVICE_NOT_ELIGIBLE",
                "Accepted active service with matching category is required",
            )
            work = self.linked_work(case, window, work)
        require(
            not self.unplanned(profile, work["id"] if isinstance(work, dict) else work),
            409,
            "UNPLANNED_WORK",
            "Existing assigned work requires a reviewed schedule",
        )
        start, end = self.bounds(window)
        self.capacity(profile, start, end, exclude)
        return profile, work

    def expectations(self, row, window=None):
        case = self.case(row["request_id"])
        window = window or self.row(
            "appointment_windows", row["alternative_window_id"] or row["selected_window_id"]
        )
        # History stays readable after work/incident closure or staff eligibility
        # changes. Projection exposes revisions, while reserve() repeats live gates.
        if row["confirmed_appointment_id"]:
            booked = self.row("appointments", row["confirmed_appointment_id"])
            work = self.s.row("work_orders", booked["work_order_id"])
        else:
            try:
                work = self.linked_work(case, window)
            except Problem:
                links = query(self.c, "SELECT * FROM hydro_dispatch_case_links(:r)", r=case["id"])
                require(links, 409, "DISPATCH_REVIEW_REQUIRED", "A reviewed work link is required")
                identifier = (row["reviewed_expectations"] or {}).get(
                    "work_order_id", links[0]["work_order_id"]
                )
                work = self.s.row("work_orders", identifier)
        profile = self.row("dispatch_technician_profiles", window["profile_id"])
        old = (
            self.row("appointments", row["replaces_appointment_id"])
            if row["replaces_appointment_id"]
            else None
        )
        return {
            "service_version": case["version"],
            "work_order_id": str(work["id"]),
            "work_version": work["version"],
            "assignment_version": work["assignment_version"],
            "window_version": window["version"],
            "calendar_version": profile["calendar_version"],
            "policy_version": self.policy()["version"],
            "replaced_appointment_version": old["version"] if old else None,
        }

    def projection(self, table, row, citizen=False):
        if table == "dispatch_technician_profiles":
            result = super().projection(table, row)
            identity = one(
                self.c,
                "SELECT display_name FROM hydro_dispatch_roster() WHERE id=:i",
                i=row["membership_id"],
            )
            result["display_name"] = identity["display_name"] if identity else "Assigned technician"
            result["scheduling_health"] = self.health(row)
            return result
        if table == "appointment_windows":
            result = {
                "id": row["id"],
                "version": row["version"],
                "arrival_start": row["arrival_start"],
                "arrival_end": row["arrival_end"],
                "expected_service_minutes": row["service_duration_minutes"],
                "timezone": "Asia/Kolkata",
                "policy_version": row["policy_version"],
                "as_of": now(),
                "confirmation_required": True,
            }
            if self.staff() and not citizen:
                p = self.row("dispatch_technician_profiles", row["profile_id"])
                start, end = self.bounds(row)
                result.update(
                    technician_membership_id=p["membership_id"],
                    calendar_version=p["calendar_version"],
                    category_codes=row["category_codes"],
                    service_area_codes=row["service_area_codes"],
                    before_buffer_minutes=row["before_buffer_minutes"],
                    after_buffer_minutes=row["after_buffer_minutes"],
                    state=row["state"],
                    occupied_interval={"start_at": start, "end_at": end},
                )
            return result
        if table == "appointment_requests":
            keys = "id kind status proposal_revision offer_expires_at replaces_appointment_id confirmed_appointment_id public_message created_at updated_at version".split()
            result = {k: row[k] for k in keys}
            expired = row["expires_at"] <= now() or (
                row["status"] == "ALTERNATIVE_OFFERED" and row["offer_expires_at"] <= now()
            )
            if row["status"] in {"PENDING", "ALTERNATIVE_OFFERED"} and expired:
                result["status"] = "EXPIRED"
            result.update(
                service_request_id=row["request_id"],
                requested_window=self.projection(
                    "appointment_windows",
                    self.row("appointment_windows", row["selected_window_id"]),
                    True,
                ),
                alternative_window=self.projection(
                    "appointment_windows",
                    self.row("appointment_windows", row["alternative_window_id"]),
                    True,
                )
                if row["alternative_window_id"]
                else None,
            )
            if self.staff() and not citizen:
                result.update(
                    expectations=self.expectations(row), internal_reason=row["internal_reason"]
                )
            return result
        if table == "appointments":
            if (
                not self.staff()
                and not citizen
                and "TECHNICIAN" in self.s.roles
                and self.s.op["id"] in {"m07_n22", "m07_n24", "m07_n28"}
            ):
                work = self.s.work(row["work_order_id"], assigned=True)
                return {
                    "id": row["id"],
                    "status": row["status"],
                    "arrival_start": row["arrival_start"],
                    "arrival_end": row["arrival_end"],
                    "expected_service_minutes": row["service_duration_minutes"],
                    "timezone": "Asia/Kolkata",
                    "work_order_id": work["id"],
                    "assignment_version": work["assignment_version"],
                    "work_version": work["version"],
                    "version": row["version"],
                    "safe_access_instructions": "Visit-access information remains disabled pending privacy review.",
                    "safe_task_instructions": "Review your currently assigned work brief; attendance does not verify a repair.",
                    "brief_expires_at": now() + timedelta(minutes=15),
                    "allowed_actions": ["CHECK_IN"]
                    if row["status"] == "CONFIRMED"
                    else ["VISIT_FINISHED", "NO_ACCESS", "ABORTED", "OVERRUN_REPORTED"]
                    if row["status"] == "CHECKED_IN"
                    else [],
                }
            result = {
                k: row[k]
                for k in "id status arrival_start arrival_end cancellation_pending replaces_id version created_at updated_at".split()
            }
            result.update(
                service_request_id=row["request_id"],
                expected_service_minutes=row["service_duration_minutes"],
                timezone="Asia/Kolkata",
                public_visit_message=row["public_visit_message"],
                allowed_actions=["CANCEL", "RESCHEDULE"] if row["status"] == "CONFIRMED" else [],
            )
            if self.staff() and not citizen:
                p = self.profile(row["assignee_id"])
                result.update(
                    request_id=row["appointment_request_id"],
                    window_id=row["window_id"],
                    work_order_id=row["work_order_id"],
                    assignee_membership_id=row["assignee_id"],
                    assignment_version=row["assignment_version"],
                    occupied_interval={
                        "start_at": row["occupied_range"].lower,
                        "end_at": row["occupied_range"].upper,
                    },
                    calendar_version=p["calendar_version"],
                    policy_version=row["policy_version"],
                    dispatch_health="READY" if self.health(p) == "READY" else "REVIEW_REQUIRED",
                    internal_reason=row["internal_reason"],
                )
            return result
        return super().projection(table, row)

    def history(self, case, kind, public, private):
        case = case_change(self.c, "service_requests", case["id"], status=case["status"])
        Foundation(self.s).history(case, kind, private, public)
        return case

    def decision_receipt(self, row):
        appointment = (
            self.row("appointments", row["confirmed_appointment_id"])
            if row["confirmed_appointment_id"]
            else None
        )
        old = (
            self.row("appointments", row["replaces_appointment_id"])
            if row["replaces_appointment_id"]
            else None
        )
        return {
            "receipt": receipt(row),
            "request": self.projection("appointment_requests", row),
            "appointment": self.projection("appointments", appointment) if appointment else None,
            "replaced_appointment": self.projection("appointments", old) if old else None,
        }

    def command_receipt(self, row):
        return {
            "receipt": receipt(row),
            "appointment": self.projection("appointments", row),
            "current_service_version": self.case(row["request_id"])["version"],
        }

    def reserve(self, row, window, expected, message, reason):
        case = self.case(row["request_id"])
        actual = self.expectations(row, window)
        require(
            actual == expected,
            412,
            "VERSION_CONFLICT",
            "The reviewed work, service, staff calendar or policy changed",
        )
        old = (
            self.row("appointments", row["replaces_appointment_id"])
            if row["replaces_appointment_id"]
            else None
        )
        require(
            not old or old["status"] == "CONFIRMED",
            409,
            "VISIT_STATE_CHANGED",
            "Only a confirmed visit may be replaced",
        )
        p, work = self.available(
            window, case, old["id"] if old else None, expected["work_order_id"]
        )
        require(
            not work["assignee_id"] or work["assignee_id"] == p["membership_id"] or old is not None,
            409,
            "ASSIGNMENT_REVIEW_REQUIRED",
            "Existing assignment must be reviewed before reassignment",
        )
        if old:
            write(
                self.c, "appointments", old["id"], status="SUPERSEDED", cancellation_pending=False
            )
            execute(
                self.c,
                "UPDATE dispatch_allocations SET active=false,released_at=now(),version=version+1,updated_at=now() WHERE appointment_id=:i AND active",
                i=old["id"],
            )
            oldprofile = self.profile(old["assignee_id"])
            if oldprofile["id"] != p["id"]:
                self.bump(oldprofile)
        else:
            require(
                not one(
                    self.c,
                    "SELECT id FROM appointments WHERE (request_id=:r OR work_order_id=:w) AND status IN ('CONFIRMED','CHECKED_IN')",
                    r=case["id"],
                    w=work["id"],
                ),
                409,
                "ACTIVE_APPOINTMENT",
                "An active appointment already exists",
            )
        work = legacy_change(
            self.c,
            "work_orders",
            work["id"],
            assignee_id=p["membership_id"],
            assignment_version=work["assignment_version"] + 1,
            status="ASSIGNED" if work["status"] in {"CREATED", "ASSIGNED"} else work["status"],
        )
        legacy_insert(
            self.c,
            "work_order_actions",
            organization_id=self.o,
            work_order_id=work["id"],
            actor_id=self.s.member_id,
            action_type="ASSIGNMENT",
            note="Appointment allocation: " + reason,
            materials=[],
            operation_id=uuid4(),
            observed_at=now(),
            received_at=now(),
            base_version=expected["work_version"],
        )
        start, end = self.bounds(window)
        appointment = write(
            self.c,
            "appointments",
            organization_id=self.o,
            request_id=case["id"],
            appointment_request_id=row["id"],
            window_id=window["id"],
            work_order_id=work["id"],
            assignee_id=p["membership_id"],
            subject_id=p["subject_id"],
            assignment_version=work["assignment_version"],
            arrival_start=window["arrival_start"],
            arrival_end=window["arrival_end"],
            service_duration_minutes=window["service_duration_minutes"],
            occupied_range=Range(start, end, "[)"),
            policy_version=window["policy_version"],
            status="CONFIRMED",
            replaces_id=old["id"] if old else None,
            public_visit_message=message,
            internal_reason=reason,
        )
        write(
            self.c,
            "dispatch_allocations",
            organization_id=self.o,
            profile_id=p["id"],
            subject_id=p["subject_id"],
            appointment_id=appointment["id"],
            work_order_id=work["id"],
            kind="APPOINTMENT",
            occupied_range=Range(start, end, "[)"),
            reason=reason,
        )
        self.bump(p)
        row = write(
            self.c,
            "appointment_requests",
            row["id"],
            status="CONFIRMED",
            confirmed_appointment_id=appointment["id"],
            public_message=message,
            internal_reason=reason,
        )
        self.history(case, "VISIT_CONFIRMED", message, reason)
        self.save("appointment_requests", row, reason)
        return self.decision_receipt(row)

    def run(self, b, parent, key):
        n = int(self.s.op["id"].rsplit("n", 1)[1])
        if n == 25:
            profiles = {
                r["membership_id"]: r
                for r in query(
                    self.c,
                    "SELECT * FROM dispatch_technician_profiles WHERE organization_id=:o",
                    o=self.o,
                )
            }
            rows = query(self.c, "SELECT * FROM hydro_dispatch_roster() ORDER BY id")
            filters = self.s.auth.request.query_params

            def project(r):
                p = profiles.get(r["id"])
                return (
                    self.projection("dispatch_technician_profiles", p)
                    if p
                    else {
                        "membership_id": r["id"],
                        "display_name": r["display_name"],
                        "enrollment_state": "ELIGIBLE"
                        if r["status"] == "ACTIVE" and r["enrollment_available"]
                        else "UNAVAILABLE",
                        "active": False,
                        "skill_codes": [],
                        "service_area_codes": [],
                        "max_daily_minutes": None,
                        "profile_version": None,
                        "calendar_version": None,
                        "scheduling_health": "UNCONFIGURED",
                    }
                )

            if filters.get("skill"):
                rows = [
                    r
                    for r in rows
                    if filters["skill"] in profiles.get(r["id"], {}).get("skill_codes", [])
                ]
            if filters.get("area"):
                rows = [
                    r
                    for r in rows
                    if filters["area"] in profiles.get(r["id"], {}).get("service_area_codes", [])
                ]
            if filters.get("status"):
                rows = [r for r in rows if project(r)["enrollment_state"] == filters["status"]]
            return self.page(rows, project)
        if n == 39:
            safety = set(b) - {"booking_enabled", "reason"}
            require(
                not one(
                    self.c,
                    "SELECT id FROM dispatch_technician_profiles WHERE calendar_version>1 LIMIT 1",
                )
                or all(parent[k] == b[k] for k in safety),
                409,
                "REPLAN_REQUIRED",
                "Safety policy changes after calendar use require reviewed governance controls. Booking can still be disabled with unchanged safety values.",
            )
        if n in {25, 26, 27, 29, 30, 31, 32, 33, 38, 39}:
            return super().run(b, parent, key)
        if n in {14, 34}:
            rows = query(
                self.c,
                "SELECT * FROM appointment_windows WHERE organization_id=:o ORDER BY arrival_start,id",
                o=self.o,
            )
            filters = self.s.auth.request.query_params
            good = []
            old = (
                one(
                    self.c,
                    "SELECT id FROM appointments WHERE request_id=:r AND status='CONFIRMED'",
                    r=parent["id"],
                )
                if n == 14
                else None
            )
            for row in rows:
                if filters.get("state") and row["state"] != filters["state"]:
                    continue
                if filters.get("category") and filters["category"] not in row["category_codes"]:
                    continue
                if filters.get("area") and filters["area"] not in row["service_area_codes"]:
                    continue
                if filters.get("from") and row["arrival_start"] < instant(filters["from"]):
                    continue
                if filters.get("to") and row["arrival_end"] > instant(filters["to"]):
                    continue
                if n == 14:
                    try:
                        self.available(row, parent, old["id"] if old else None)
                    except Problem:
                        continue
                good.append(row)
            result = self.page(good, lambda r: self.projection("appointment_windows", r, n == 14))
            if n == 14:
                policy = self.policy()
                state = (
                    "UNCONFIGURED"
                    if not policy["configured"]
                    else "DISABLED"
                    if not policy["booking_enabled"]
                    else "SERVICE_REVIEW_REQUIRED"
                    if parent["status"] in TERMINAL or parent["accepted_at"] is None
                    else "AVAILABLE"
                    if good
                    else "NO_PUBLISHED_WINDOWS"
                )
                result.update(
                    availability_state=state,
                    message="Only utility-reviewed windows are shown. A request does not confirm a visit."
                    if good
                    else "No eligible visit windows are currently published. Utility review and authorized configuration are required.",
                )
            return result
        if n in {16, 21}:
            table = "appointment_requests" if n == 16 else "appointments"
            rows = query(
                self.c,
                f"SELECT * FROM {table} WHERE request_id=:r ORDER BY created_at,id",
                r=parent["id"],
            )
            return self.page(rows, lambda r: self.projection(table, r))
        if n in {17, 22}:
            return self.projection("appointment_requests" if n == 17 else "appointments", parent)
        if n == 15:
            require(
                b["expected_preferences_version"] is None,
                409,
                "PREFERENCES_DISABLED",
                "Visit preferences remain disabled pending privacy review",
            )
            window = self.row("appointment_windows", b["window_id"])
            version(window["version"], b["expected_window_version"])
            old = (
                self.row("appointments", b["replaces_appointment_id"])
                if b["replaces_appointment_id"]
                else None
            )
            if old:
                require(
                    old["request_id"] == parent["id"] and old["status"] == "CONFIRMED",
                    409,
                    "VISIT_STATE_CHANGED",
                    "Current owned confirmed appointment required",
                )
                version(old["version"], b["expected_appointment_version"])
            else:
                require(
                    not one(
                        self.c,
                        "SELECT id FROM appointments WHERE request_id=:r AND status IN ('CONFIRMED','CHECKED_IN')",
                        r=parent["id"],
                    ),
                    409,
                    "ACTIVE_APPOINTMENT",
                    "Use rescheduling for the existing appointment",
                )
            self.available(window, parent, old["id"] if old else None)
            execute(
                self.c,
                "UPDATE appointment_requests SET status='EXPIRED',version=version+1,updated_at=now() WHERE request_id=:r AND status IN ('PENDING','ALTERNATIVE_OFFERED') AND (expires_at<=now() OR offer_expires_at<=now())",
                r=parent["id"],
            )
            row = write(
                self.c,
                "appointment_requests",
                organization_id=self.o,
                request_id=parent["id"],
                kind=b["kind"],
                selected_window_id=window["id"],
                replaces_appointment_id=b["replaces_appointment_id"],
                expires_at=now() + timedelta(hours=self.policy()["request_expiry_hours"]),
                status="PENDING",
                public_message=b["message"],
            )
            self.history(
                parent,
                "VISIT_REQUESTED",
                "A visit was requested. No appointment or capacity is confirmed.",
                "Resident requested a visit",
            )
            return self.save("appointment_requests", row, "Resident requested a visit")
        if n in {18, 19, 20}:
            case = self.case(parent["request_id"])
            require(
                parent["status"] in {"PENDING", "ALTERNATIVE_OFFERED"}
                and parent["expires_at"] > now(),
                409,
                "REQUEST_EXPIRED",
                "Request is no longer actionable",
            )
            if n == 20:
                row = write(
                    self.c,
                    "appointment_requests",
                    parent["id"],
                    status="WITHDRAWN",
                    public_message=b["reason"],
                )
                self.history(
                    case,
                    "VISIT_REQUEST_WITHDRAWN",
                    "The visit request was withdrawn. Any existing confirmed appointment is unchanged.",
                    b["reason"],
                )
                return self.save("appointment_requests", row, b["reason"])
            if n == 19:
                require(
                    parent["status"] == "ALTERNATIVE_OFFERED"
                    and parent["offer_expires_at"] > now(),
                    409,
                    "OFFER_EXPIRED",
                    "Alternative offer expired or changed",
                )
                version(parent["proposal_revision"], b["proposal_revision"])
                expected = parent["reviewed_expectations"]
                version(expected["service_version"], b["expected_service_version"])
                version(expected["window_version"], b["expected_window_version"])
                version(
                    expected["replaced_appointment_version"],
                    b["expected_replaced_appointment_version"],
                )
                return self.reserve(
                    parent,
                    self.row("appointment_windows", parent["alternative_window_id"]),
                    expected,
                    "Your accepted alternative visit is confirmed.",
                    "Resident accepted the reviewed alternative",
                )
            if b["decision"] == "DECLINE":
                row = write(
                    self.c,
                    "appointment_requests",
                    parent["id"],
                    status="DECLINED",
                    public_message=b["public_message"],
                    internal_reason=b["internal_reason"],
                )
                self.history(
                    case, "VISIT_REQUEST_DECLINED", b["public_message"], b["internal_reason"]
                )
                self.save("appointment_requests", row, b["internal_reason"])
                return self.decision_receipt(row)
            window = self.row(
                "appointment_windows",
                b.get("alternative_window_id") or parent["selected_window_id"],
            )
            if b["decision"] == "CONFIRM_REQUESTED":
                require(
                    parent["status"] == "PENDING",
                    409,
                    "RESIDENT_ACCEPTANCE_REQUIRED",
                    "Resident must accept an offered alternative",
                )
                return self.reserve(
                    parent, window, b["expectations"], b["public_message"], b["internal_reason"]
                )
            version(window["version"], b["expected_window_version"])
            require(
                self.expectations(parent, window) == b["expectations"],
                412,
                "VERSION_CONFLICT",
                "Reviewed booking expectations changed",
            )
            self.available(
                window, case, parent["replaces_appointment_id"], b["expectations"]["work_order_id"]
            )
            expiry = instant(b["offer_expires_at"])
            require(
                now()
                < expiry
                <= min(
                    parent["expires_at"],
                    now() + timedelta(hours=self.policy()["offer_expiry_hours"]),
                    window["arrival_start"],
                ),
                422,
                "INVALID_EXPIRY",
                "Offer expiry must fit configured policy and arrival",
            )
            updatedcase = self.history(
                case, "VISIT_ALTERNATIVE_OFFERED", b["public_message"], b["internal_reason"]
            )
            expected = {**b["expectations"], "service_version": updatedcase["version"]}
            row = write(
                self.c,
                "appointment_requests",
                parent["id"],
                status="ALTERNATIVE_OFFERED",
                alternative_window_id=window["id"],
                proposal_revision=(parent["proposal_revision"] or 0) + 1,
                reviewed_expectations=expected,
                offer_expires_at=expiry,
                public_message=b["public_message"],
                internal_reason=b["internal_reason"],
            )
            self.save("appointment_requests", row, b["internal_reason"])
            return self.decision_receipt(row)
        if n == 23:
            case = self.case(parent["request_id"])
            version(case["version"], b["expected_service_version"])
            require(
                parent["status"] == "CONFIRMED",
                409,
                "VISIT_STATE_CHANGED",
                "Only a confirmed visit can be cancelled; checked-in visits require a recorded outcome",
            )
            work = self.s.row("work_orders", parent["work_order_id"], True)
            staff = b["caller_action"] == "SUPERVISOR"
            require(
                staff == self.staff(), 403, "FORBIDDEN", "Cancellation action exceeds current role"
            )
            if staff:
                version(work["version"], b["expected_work_version"])
                version(work["assignment_version"], b["expected_assignment_version"])
                require(
                    b["disposition"] == "CANCEL" or parent["cancellation_pending"],
                    409,
                    "NO_PENDING_CANCEL",
                    "No cancellation request is pending",
                )
            cutoff = self.policy()["free_cancel_before_minutes"]
            cancel = (
                staff
                and b["disposition"] != "DECLINE_PENDING_CANCEL"
                or not staff
                and cutoff is not None
                and now() < parent["arrival_start"] - timedelta(minutes=cutoff)
            )
            row = write(
                self.c,
                "appointments",
                parent["id"],
                status="CANCELLED" if cancel else "CONFIRMED",
                cancellation_pending=not staff and not cancel,
                public_visit_message=b["public_reason"],
            )
            if cancel:
                execute(
                    self.c,
                    "UPDATE dispatch_allocations SET active=false,released_at=now(),version=version+1,updated_at=now() WHERE appointment_id=:a AND active",
                    a=row["id"],
                )
                self.bump(self.profile(row["assignee_id"]))
                execute(
                    self.c,
                    "UPDATE appointment_requests SET status='EXPIRED',version=version+1,updated_at=now() WHERE replaces_appointment_id=:a AND status IN ('PENDING','ALTERNATIVE_OFFERED')",
                    a=row["id"],
                )
            self.history(
                case,
                "VISIT_CANCELLED" if cancel else "VISIT_CANCELLATION_REVIEW",
                b["public_reason"],
                b.get("internal_reason", b["reason_code"]),
            )
            self.save("appointments", row, b.get("internal_reason", b["reason_code"]))
            return self.command_receipt(row)
        if n == 24:
            work = self.s.row("work_orders", parent["work_order_id"], True)
            version(work["version"], b["expected_work_version"])
            version(work["assignment_version"], b["assignment_version"])
            require(
                work["assignee_id"] == parent["assignee_id"]
                and work["assignment_version"] == parent["assignment_version"]
                and work["status"] not in FINAL_WORK,
                409,
                "ASSIGNMENT_CHANGED",
                "Current active work assignment required",
            )
            event = b["event_type"]
            require(
                (self.staff() and event == "ADMIN_CORRECTION")
                or (not self.staff() and event != "ADMIN_CORRECTION"),
                403,
                "FORBIDDEN",
                "Visit event exceeds current role",
            )
            observed = instant(b["observed_at"])
            previous = one(
                self.c,
                "SELECT max(observed_at) AS stamp FROM appointment_events WHERE appointment_id=:a",
                a=parent["id"],
            )["stamp"]
            require(
                parent["created_at"] <= observed <= now() + timedelta(minutes=5)
                and (previous is None or observed >= previous),
                422,
                "INVALID_TIME",
                "Visit event ordering is invalid",
            )
            if event == "ADMIN_CORRECTION":
                require(
                    b["supersedes_event_id"]
                    and one(
                        self.c,
                        "SELECT id FROM appointment_events WHERE appointment_id=:a AND id=:i",
                        a=parent["id"],
                        i=b["supersedes_event_id"],
                    ),
                    422,
                    "INVALID_CORRECTION",
                    "A same-visit prior event is required",
                )
                target = parent["status"]
            else:
                require(
                    b["supersedes_event_id"] is None,
                    422,
                    "INVALID_CORRECTION",
                    "Technician events cannot replace history",
                )
                require(
                    parent["status"] == ("CONFIRMED" if event == "CHECK_IN" else "CHECKED_IN"),
                    409,
                    "INVALID_TRANSITION",
                    "Visit state changed",
                )
                target = (
                    "CHECKED_IN"
                    if event == "CHECK_IN"
                    else parent["status"]
                    if event == "OVERRUN_REPORTED"
                    else event
                )
            event_id = uuid4()
            execute(
                self.c,
                "INSERT INTO appointment_events(id,organization_id,appointment_id,actor_id,operation_id,event_type,note,observed_at,assignment_version,supersedes_event_id) VALUES(:i,:o,:a,:m,:k,:t,:n,:at,:av,:sup)",
                i=event_id,
                o=self.o,
                a=parent["id"],
                m=self.s.member_id,
                k=b["operation_id"],
                t=event,
                n=b["note"],
                at=observed,
                av=work["assignment_version"],
                sup=b["supersedes_event_id"],
            )
            row = write(self.c, "appointments", parent["id"], status=target)
            if target not in LIVE:
                execute(
                    self.c,
                    "UPDATE dispatch_allocations SET active=false,released_at=now(),version=version+1,updated_at=now() WHERE appointment_id=:a AND active",
                    a=row["id"],
                )
            if self.staff():
                self.bump(self.profile(row["assignee_id"]))
            else:
                execute(self.c, "SELECT hydro_dispatch_visit_update(:a)", a=row["id"])
            self.save("appointments", row, b["note"])
            return {
                "receipt": {"id": event_id, "version": 1, "received_at": now()},
                "appointment": self.projection("appointments", row),
            }
        if n == 35:
            p = parent
            policy = self.policy()
            version(policy["version"], b["expected_policy_version"])
            version(p["calendar_version"], b["expected_calendar_version"])
            start, end = instant(b["arrival_start"]), instant(b["arrival_end"])
            require(
                policy["configured"] and policy["booking_enabled"],
                409,
                "SCHEDULING_DISABLED",
                "Authorized utility policy is required before publication",
            )
            require(
                start < end
                and (end - start).total_seconds() / 60 <= policy["max_arrival_width_minutes"]
                and b["expected_service_minutes"] in policy["allowed_duration_minutes"]
                and b["before_buffer_minutes"] >= policy["minimum_before_buffer_minutes"]
                and b["after_buffer_minutes"] >= policy["minimum_after_buffer_minutes"],
                422,
                "POLICY_CONFLICT",
                "Window does not satisfy the explicit policy",
            )
            require(
                set(b["service_area_codes"]) <= set(p["service_area_codes"]),
                422,
                "AREA_CONFLICT",
                "Window areas must match reviewed staff areas",
            )
            window = {
                **b,
                "profile_id": p["id"],
                "state": "PUBLISHED",
                "arrival_start": start,
                "arrival_end": end,
                "service_duration_minutes": b["expected_service_minutes"],
                "policy_version": policy["version"],
            }
            self.available(window)
            p = self.bump(p)
            row = write(
                self.c,
                "appointment_windows",
                organization_id=self.o,
                profile_id=p["id"],
                arrival_start=start,
                arrival_end=end,
                service_duration_minutes=b["expected_service_minutes"],
                before_buffer_minutes=b["before_buffer_minutes"],
                after_buffer_minutes=b["after_buffer_minutes"],
                category_codes=b["category_codes"],
                service_area_codes=b["service_area_codes"],
                policy_version=policy["version"],
                calendar_version=p["calendar_version"],
                state="PUBLISHED",
                reason=b["reason"],
            )
            return self.save("appointment_windows", row, b["reason"])
        if n == 36:
            p = self.row("dispatch_technician_profiles", parent["profile_id"])
            version(p["calendar_version"], b["expected_calendar_version"])
            row = write(self.c, "appointment_windows", parent["id"], state="WITHDRAWN")
            self.bump(p)
            return self.save("appointment_windows", row, b["reason"])
        if n in {28, 37}:
            return self.calendar(parent) if n == 28 else self.workload()
        require(False, 404, "NOT_FOUND", "Operation unavailable")

    def range_filter(self):
        p = self.s.auth.request.query_params
        try:
            start, end = instant(p["from"]), instant(p["to"])
        except (KeyError, ValueError):
            require(False, 422, "INVALID_RANGE", "An explicit from/to date range is required")
        require(
            start < end and end - start <= timedelta(days=60),
            422,
            "INVALID_RANGE",
            "Use a positive date range of at most 60 days",
        )
        return start, end

    def calendar(self, p):
        if not self.staff():
            require(
                p["membership_id"] == self.s.member_id, 404, "NOT_FOUND", "Calendar unavailable"
            )
        start, end = self.range_filter()
        shifts = query(
            self.c,
            "SELECT * FROM dispatch_shifts WHERE profile_id=:p AND starts_at<:e AND ends_at>:s ORDER BY starts_at,id",
            p=p["id"],
            s=start,
            e=end,
        )
        blocks = query(
            self.c,
            "SELECT * FROM dispatch_allocations WHERE profile_id=:p AND active AND kind<>'APPOINTMENT' AND occupied_range && tstzrange(:s,:e,'[)') ORDER BY id",
            p=p["id"],
            s=start,
            e=end,
        )
        visits = query(
            self.c,
            "SELECT * FROM appointments WHERE assignee_id=:m AND arrival_start<:e AND arrival_end>:s ORDER BY arrival_start,id",
            m=p["membership_id"],
            s=start,
            e=end,
        )
        require(
            max(len(shifts), len(blocks), len(visits)) <= 100,
            409,
            "NARROW_QUERY",
            "Narrow the date range to retrieve a complete calendar",
        )

        def page(rows, table):
            return {
                "items": [self.projection(table, r) for r in rows],
                "next_cursor": None,
                "as_of": now(),
            }

        return {
            "profile_version": p["version"],
            "calendar_version": p["calendar_version"],
            "as_of": now(),
            "timezone": "Asia/Kolkata",
            "shifts": page(shifts, "dispatch_shifts"),
            "blocks": page(blocks, "dispatch_allocations"),
            "appointments": page(visits, "appointments"),
        }

    def workload(self):
        start, end = self.range_filter()
        rows = query(
            self.c,
            "SELECT * FROM dispatch_technician_profiles WHERE organization_id=:o ORDER BY id",
            o=self.o,
        )

        def project(p):
            reserved = one(
                self.c,
                "SELECT coalesce(sum(extract(epoch FROM (least(upper(occupied_range),:e)-greatest(lower(occupied_range),:s)))/60) FILTER(WHERE kind<>'UNAVAILABLE'),0) AS planned,coalesce(sum(extract(epoch FROM (least(upper(occupied_range),:e)-greatest(lower(occupied_range),:s)))/60) FILTER(WHERE kind='UNAVAILABLE'),0) AS leave FROM dispatch_allocations WHERE profile_id=:p AND active AND occupied_range && tstzrange(:s,:e,'[)')",
                p=p["id"],
                s=start,
                e=end,
            )
            shift = one(
                self.c,
                "SELECT coalesce(sum(extract(epoch FROM (least(ends_at,:e)-greatest(starts_at,:s)))/60),0) AS minutes FROM dispatch_shifts WHERE profile_id=:p AND status='ACTIVE' AND starts_at<:e AND ends_at>:s",
                p=p["id"],
                s=start,
                e=end,
            )["minutes"]
            leave = one(
                self.c,
                "SELECT coalesce(sum(extract(epoch FROM (least(upper(a.occupied_range),s.ends_at,:e)-greatest(lower(a.occupied_range),s.starts_at,:start)))/60),0) AS minutes FROM dispatch_allocations a JOIN dispatch_shifts s ON s.profile_id=a.profile_id AND s.status='ACTIVE' AND a.occupied_range && tstzrange(s.starts_at,s.ends_at,'[)') WHERE a.profile_id=:p AND a.active AND a.kind='UNAVAILABLE' AND a.occupied_range && tstzrange(:start,:e,'[)') AND s.starts_at<:e AND s.ends_at>:start",
                p=p["id"],
                start=start,
                e=end,
            )["minutes"]
            available = max(0, int(shift) - int(leave))
            unplanned = self.unplanned(p)
            count = one(
                self.c,
                "SELECT count(*) AS n FROM appointments WHERE assignee_id=:m AND status IN ('CONFIRMED','CHECKED_IN') AND arrival_start<:e AND arrival_end>:s",
                m=p["membership_id"],
                s=start,
                e=end,
            )["n"]
            overdue = one(
                self.c,
                "SELECT count(*) AS n FROM work_orders WHERE assignee_id=:m AND status NOT IN ('COMPLETED','CANCELLED') AND due_at<now()",
                m=p["membership_id"],
            )["n"]
            return {
                "technician_membership_id": p["membership_id"],
                "confirmed_appointments": count,
                "planned_occupied_minutes": int(reserved["planned"]),
                "unplanned_work_count": unplanned,
                "overdue_work_count": overdue,
                "available_shift_minutes": available,
                "known_load_ratio": float(reserved["planned"]) / available
                if available and not unplanned and float(reserved["planned"]) <= available
                else None,
                "scheduling_health": self.health(p),
            }

        page = self.page(rows, project)
        return {**page, "from": start, "to": end, "timezone": "Asia/Kolkata"}
