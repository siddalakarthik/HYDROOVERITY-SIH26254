"""Independent M09 scenarios; run explicitly after the historical acceptance suite.

All identities, visits and findings are SYNTHETIC software fixtures, never field
evidence. Keeping this suite explicit preserves the historical operation matrix.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import uuid4

from conftest import Client
from helpers import expect, login, mutate, provision
from test_communications import drain, enable
from test_scheduling import booking_fixture, confirm, request_visit
from test_service_foundation import create, resident, submission, triage
from test_workflow import incident, transition

from hydro.db import context, one, query
from hydro.main import create_app

pytest_plugins = ["test_science"]


def test_runtime_inventory_and_database_principal_remain_private(env):
    from hydro.contracts import runtime_openapi

    spec = runtime_openapi()
    assert sum(len(methods) for methods in spec["paths"].values()) == 111
    assert not any(
        any(word in p for word in ("/actuate", "/valves/", "/uploads", "/attachments"))
        for p in spec["paths"]
    )
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_001"
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM pg_tables WHERE schemaname='public' AND tablename NOT IN ('spatial_ref_sys','alembic_version')",
            )["n"]
            == 51
        )
    with env["app"].state.engine.begin() as c:
        role = one(c, "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user")
        assert role == {"rolsuper": False, "rolbypassrls": False}
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM pg_tables WHERE schemaname='public' AND tableowner=current_user",
            )["n"]
            == 0
        )


def test_all_69_replay_exports_and_frames_keep_truth_private(env, science):
    import json
    import os
    from pathlib import Path

    first, _, data, base = science
    # Distinct authorized synthetic members keep each below the unchanged
    # 120/min member-wide science throttle and 30/min IP CSRF throttle.
    second, _ = provision(env, "ENGINEER", "m09-science-b@example.invalid")
    third, _ = provision(env, "ENGINEER", "m09-science-c@example.invalid")
    clients = [first, second, third]
    forbidden = {
        "truth",
        "seed",
        "position_m",
        "hidden_label",
        "artifact_path",
        "password_hash",
        "hmac_key",
    }

    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    sizes = []
    for index, case in enumerate(data["cases"]):
        client = clients[index % 3]
        row = expect(mutate(client, base, {"scenario_code": case["code"]}), 200)
        response = client.request("GET", base + "/" + row["id"] + "/export")
        exported = expect(response, 200)
        inspect(exported)
        assert exported["snapshot"]["case"] == case
        frames = client.request("GET", base + "/" + row["id"] + "/frames?limit=2")
        inspect(expect(frames, 200))
        sizes.append(len(frames.content))
    assert len(sizes) == 69
    target = os.environ.get("HYDRO_TEST_EVIDENCE_DIR")
    if target:
        Path(target).mkdir(parents=True, exist_ok=True)
        (Path(target) / "replay-boundary-measurement.json").write_text(
            json.dumps(
                {
                    "recordings": 69,
                    "frame_page_limit": 2,
                    "frame_page_bytes_min_max": [min(sizes), max(sizes)],
                    "result": "ALL_EXPORTS_EQUAL_APPROVED_SAFE_SNAPSHOTS; FORBIDDEN_KEYS_ABSENT",
                    "numerical_reproduction": "Run tests/unit/test_m06_reproduction.py separately",
                }
            )
        )


def test_actual_worker_process_restart_retains_queue_and_safe_delivery(env, tmp_path):
    import json
    import os
    import subprocess
    import sys
    import time

    from test_communications import fixture

    from hydro.config import ROOT
    from hydro.db import execute
    from hydro.operator import private_directory

    citizen, sup, _, user, base = fixture(env)
    enable(citizen, base)
    private_directory(tmp_path / "m09-worker")
    config = tmp_path / "m09-worker/runtime.json"
    settings = env["settings"]
    payload = settings.model_dump(mode="json")
    payload.update(
        database_url=settings.database_url.get_secret_value(),
        hmac_key=settings.hmac_key.get_secret_value(),
    )
    config.write_text(json.dumps(payload))
    child_env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(
            ("HYDRO_TEST_OWNER", "HYDRO_OPERATOR", "HYDRO_MIGRATION", "HYDRO_TEST_ADMIN")
        )
    }
    child_env["PYTHONPATH"] = str(ROOT / "services/api")

    def once():
        result = subprocess.run(
            [
                sys.executable,
                "services/api/tools/notification_worker.py",
                "--runtime-config",
                str(config),
                "--organization",
                str(env["org"]["id"]),
                "--supervisor-user",
                str(user),
                "--once",
            ],
            cwd=ROOT,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        assert result.returncode == 0, (
            "Owned synthetic worker failed; private output retained by operator"
        )
        return result.stdout.strip()

    case = create(citizen, base)
    started = time.perf_counter()
    assert once() == "SUCCEEDED"
    triage(sup, base + "/service-requests/" + case["id"], case, "UNDER_REVIEW")
    assert once() == "SUCCEEDED"  # a new OS process recovers the persisted queue
    assert once() == "IDLE"
    assert len(expect(citizen.request("GET", base + "/notifications"), 200)["items"]) == 2
    case = create(citizen, base)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE background_jobs SET state='RUNNING',attempts=1,lease_token=:t,lease_until=now()-interval '1 second' WHERE state='QUEUED'",
            t=uuid4(),
        )
    assert once() == "RECOVERED"
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM notifications WHERE state='DELIVERED'")["n"] == 2
        assert one(c, "SELECT count(*) AS n FROM background_jobs WHERE state='FAILED'")["n"] == 1
    target = os.environ.get("HYDRO_TEST_EVIDENCE_DIR")
    if target:
        from pathlib import Path

        (Path(target) / "worker-process-measurement.json").write_text(
            json.dumps(
                {
                    "provenance": "SYNTHETIC_ONLY",
                    "delivered_jobs": 2,
                    "process_launches": 4,
                    "elapsed_s_including_startup_and_idle_recovery": time.perf_counter() - started,
                    "limitation": "Two deliveries; no steady-state throughput or percentile claim",
                }
            )
        )


def second_case(env, f):
    """Distinct resident and legitimately triaged work, sharing the real roster."""
    other = resident(env, "m09-competing-resident@example.invalid")
    case = create(other, f["base"])
    cp = f["base"] + "/service-requests/" + case["id"]
    for state in ("UNDER_REVIEW", "ACCEPTED"):
        case = triage(f["supervisor"], cp, case, state)
    item = incident(env, f)
    ip = f["base"] + "/incidents/" + item["id"]
    for state in ("UNDER_REVIEW", "ACCEPTED"):
        item = transition(f["supervisor"], ip, item, state)
    work = expect(
        mutate(
            f["supervisor"],
            f["base"] + "/work-orders",
            dict(
                incident_id=item["id"],
                priority="MEDIUM",
                instructions="SYNTHETIC independent competing investigation",
                task_purpose="INVESTIGATION",
            ),
        ),
        201,
    )
    expect(
        mutate(
            f["supervisor"],
            cp + "/work-order-links",
            dict(
                work_order_id=work["id"],
                expected_work_version=work["version"],
                purpose="INVESTIGATION",
                internal_reason="SYNTHETIC reviewed eligibility",
                dispatch_service_area_code="SYNTHETIC_AREA",
                dispatch_required_skill_codes=["SYNTHETIC_INSPECTION"],
            ),
            case["version"],
        ),
        201,
    )
    return {**f, "citizen": other, "case_path": cp, "work": work}


def test_two_residents_compete_for_one_technician_with_exactly_one_booking(env):
    f = booking_fixture(env)
    g = second_case(env, f)
    requests = [request_visit(f), request_visit(g)]
    staff = [
        expect(f["supervisor"].request("GET", f["base"] + "/appointment-requests/" + r["id"]), 200)
        for r in requests
    ]
    clients = [f["supervisor"], login(env, "supervisor@example.invalid")]

    def attempt(index):
        row = staff[index]
        return mutate(
            clients[index],
            f["base"] + "/appointment-requests/" + row["id"] + "/decisions",
            dict(
                decision="CONFIRM_REQUESTED",
                expectations=row["expectations"],
                public_message="SYNTHETIC competing confirmation",
                internal_reason="SYNTHETIC contention",
            ),
            row["version"],
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sorted(r.status_code for r in results) in ([200, 409], [200, 412])
    winner = next(r.json()["appointment"] for r in results if r.status_code == 200)
    with env["owner"].begin() as c:
        rows = query(c, "SELECT appointment_id FROM dispatch_allocations WHERE active")
        assert len(rows) == 1 and str(rows[0]["appointment_id"]) == winner["id"]
        assert one(c, "SELECT count(*) AS n FROM appointments")["n"] == 1
        assert (
            one(c, "SELECT count(*) AS n FROM appointment_requests WHERE status='CONFIRMED'")["n"]
            == 1
        )


def test_reschedule_confirmation_races_original_cancellation_atomically(env):
    f = booking_fixture(env)
    original = confirm(f, request_visit(f))["appointment"]
    replacement = request_visit(f, 1, original)
    path = f["base"] + "/appointment-requests/" + replacement["id"]
    row = expect(f["supervisor"].request("GET", path), 200)
    case = expect(f["citizen"].request("GET", f["case_path"]), 200)
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(
            mutate,
            f["supervisor"],
            path + "/decisions",
            dict(
                decision="CONFIRM_REQUESTED",
                expectations=row["expectations"],
                public_message="SYNTHETIC replacement confirmation",
                internal_reason="SYNTHETIC race",
            ),
            row["version"],
        )
        b = pool.submit(
            mutate,
            f["citizen"],
            f["base"] + "/appointments/" + original["id"] + "/cancellations",
            dict(
                caller_action="RESIDENT",
                reason_code="RESIDENT",
                public_reason="SYNTHETIC cancel original visit",
                expected_service_version=case["version"],
            ),
            original["version"],
        )
        replacement_result, cancellation_result = a.result(), b.result()
    assert sorted((replacement_result.status_code, cancellation_result.status_code)) in (
        [200, 409],
        [200, 412],
    )
    with env["owner"].begin() as c:
        saved = one(c, "SELECT status FROM appointments WHERE id=:i", i=original["id"])
        if replacement_result.status_code == 200:
            assert saved["status"] == "SUPERSEDED"
            assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 1
        else:
            assert saved["status"] == "CANCELLED"
            assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 0
            assert one(c, "SELECT count(*) AS n FROM appointments")["n"] == 1


def supervisor_user(env):
    with env["owner"].begin() as c:
        return one(
            c,
            "SELECT m.user_id FROM organization_memberships m JOIN role_assignments a ON a.membership_id=m.id JOIN roles r ON r.id=a.role_id WHERE r.code='SUPERVISOR' AND a.revoked_at IS NULL LIMIT 1",
        )["user_id"]


def test_two_current_sessions_cannot_accept_one_stale_alternative_twice(env):
    from datetime import timedelta

    f = booking_fixture(env)
    row = request_visit(f)
    path = f["base"] + "/appointment-requests/" + row["id"]
    staff = expect(f["supervisor"].request("GET", path), 200)
    w = f["windows"][1]
    calendar = expect(f["supervisor"].request("GET", f["base"] + "/dispatch/technicians"), 200)[
        "items"
    ][0]
    offer = dict(
        decision="OFFER_ALTERNATIVE",
        alternative_window_id=w["id"],
        expected_window_version=w["version"],
        expectations={
            **staff["expectations"],
            "window_version": w["version"],
            "calendar_version": calendar["calendar_version"],
            "policy_version": w["policy_version"],
        },
        offer_expires_at=(datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        public_message="SYNTHETIC offered alternative",
        internal_reason="SYNTHETIC review",
    )
    expect(mutate(f["supervisor"], path + "/decisions", offer, staff["version"]), 200)
    safe = expect(f["citizen"].request("GET", path), 200)
    case = expect(f["citizen"].request("GET", f["case_path"]), 200)
    body = dict(
        proposal_revision=safe["proposal_revision"],
        expected_window_version=w["version"],
        expected_service_version=case["version"],
        expected_replaced_appointment_version=None,
    )
    second = login(env, "citizen@example.invalid")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: mutate(client, path + "/accept-alternative", body, safe["version"]),
                [f["citizen"], second],
            )
        )
    assert sorted(r.status_code for r in results) == [200, 412]
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM appointments")["n"] == 1
        assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 1


def test_rescheduling_and_legacy_reassignment_cannot_bypass_commitments(env):
    f = booking_fixture(env)
    visit = confirm(f, request_visit(f))["appointment"]
    requested = request_visit(f, 1, visit)
    path = f["base"] + "/appointment-requests/" + requested["id"]
    row = expect(f["supervisor"].request("GET", path), 200)
    wp = f["base"] + "/work-orders/" + f["work"]["id"]
    work = expect(f["supervisor"].request("GET", wp), 200)
    second = login(env, "supervisor@example.invalid")
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(
            mutate,
            f["supervisor"],
            path + "/decisions",
            dict(
                decision="CONFIRM_REQUESTED",
                expectations=row["expectations"],
                public_message="SYNTHETIC reviewed replacement",
                internal_reason="SYNTHETIC race",
            ),
            row["version"],
        )
        b = pool.submit(
            mutate,
            second,
            wp + "/assignment",
            dict(
                assignee_membership_id=f["tech_membership"]["id"],
                due_at=None,
                reason="SYNTHETIC legacy bypass attempt",
            ),
            work["version"],
        )
        booking, reassignment = a.result(), b.result()
    expect(booking, 200)
    assert reassignment.status_code in {409, 412}
    profile = expect(f["supervisor"].request("GET", f["base"] + "/dispatch/technicians"), 200)[
        "items"
    ][0]
    with env["owner"].begin() as c:
        shift = one(c, "SELECT * FROM dispatch_shifts WHERE status='ACTIVE'")
    expect(
        mutate(
            f["supervisor"],
            f["base"] + "/dispatch/shifts/" + str(shift["id"]),
            dict(
                interval=dict(
                    start_at=shift["starts_at"].isoformat(), end_at=shift["ends_at"].isoformat()
                ),
                status="WITHDRAWN",
                expected_calendar_version=profile["calendar_version"],
                reason="SYNTHETIC unsafe withdrawal with booking",
            ),
            shift["version"],
            method="PATCH",
        ),
        409,
    )
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 1
        assert (
            one(c, "SELECT status FROM dispatch_shifts WHERE id=:i", i=shift["id"])["status"]
            == "ACTIVE"
        )


def visit_event(f, appointment, event):
    path = f["base"] + "/appointments/" + appointment["id"]
    brief = expect(f["technician"].request("GET", path), 200)
    return expect(
        mutate(
            f["technician"],
            path + "/visit-events",
            dict(
                operation_id=str(uuid4()),
                event_type=event,
                observed_at=datetime.now(UTC).isoformat(),
                assignment_version=brief["assignment_version"],
                expected_work_version=brief["work_version"],
                note="SYNTHETIC M09 manual visit activity; no field work performed",
                supersedes_event_id=None,
            ),
            brief["version"],
        ),
        201,
    )["appointment"]


def test_cross_role_investigation_booking_closure_notifications_and_feedback(env):
    """One persisted chain, rather than disconnected feature assertions."""
    f = booking_fixture(env)
    base, citizen, sup, tech = f["base"], f["citizen"], f["supervisor"], f["technician"]
    enable(citizen, base)
    enable(tech, base)
    user = supervisor_user(env)
    appointment = confirm(f, request_visit(f))["appointment"]
    assert (
        expect(citizen.request("GET", base + "/appointments/" + appointment["id"]), 200)["status"]
        == "CONFIRMED"
    )
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 1
    appointment = visit_event(f, appointment, "CHECK_IN")
    appointment = visit_event(f, appointment, "VISIT_FINISHED")
    wp = base + "/work-orders/" + f["work"]["id"]
    work = expect(tech.request("GET", wp), 200)
    assert work["status"] == "ASSIGNED"  # a finished visit is not finished work
    work = transition(tech, wp, work, "ACCEPTED")
    work = transition(tech, wp, work, "IN_PROGRESS")
    finding = expect(
        mutate(
            tech,
            wp + "/findings",
            dict(
                operation_id=str(uuid4()),
                assignment_version=work["assignment_version"],
                observed_at=datetime.now(UTC).isoformat(),
                findings="SYNTHETIC inspection: insufficient observations for a repair claim",
                no_repair_reason="SYNTHETIC investigation only; no physical repair performed",
                attachment_ids=[],
                supersedes_id=None,
            ),
            work["version"],
        ),
        201,
    )
    assert finding["resource"]["provenance"] == "MANUAL"
    work = expect(tech.request("GET", wp), 200)
    work = transition(tech, wp, work, "SUBMITTED_FOR_REVIEW")
    work = transition(sup, wp, work, "COMPLETED")
    case = expect(sup.request("GET", f["case_path"]), 200)
    for action in ("REQUEST_REVIEW", "CLOSE"):
        body = dict(
            action=action,
            reason_code="INVESTIGATED",
            public_message="SYNTHETIC investigation complete; no repair or scientific success claimed",
            internal_reason="PRIVATE_M09_REVIEW",
        )
        if action == "CLOSE":
            body.update(
                service_outcome="NO_ACTION_WITH_REASON",
                child_dispositions=[],
                expected_work_versions=[dict(work_order_id=work["id"], version=work["version"])],
            )
        case = expect(mutate(sup, f["case_path"] + "/transitions", body, case["version"]), 200)
    assert case["status"] == "SERVICE_CLOSED"
    assert case["verification_summary"] == "NOT_APPLICABLE"
    assert "FAILED" not in drain(env, user)
    inbox = expect(citizen.request("GET", base + "/notifications"), 200)["items"]
    assert inbox and all("PRIVATE_M09" not in str(n) for n in inbox)
    item = inbox[0]
    receipt = expect(
        mutate(citizen, base + "/notifications/" + item["id"] + "/read", None, item["version"]),
        200,
    )
    assert receipt["id"] == item["id"]
    assert next(
        n
        for n in expect(citizen.request("GET", base + "/notifications"), 200)["items"]
        if n["id"] == item["id"]
    )["read"]
    feedback = expect(
        mutate(
            citizen,
            base + "/feedback",
            dict(
                summary="SYNTHETIC completed investigation feedback",
                description="Resident experience only, never measurement verification",
                complaint_id=None,
                service_request_id=case["id"],
                service_rating=4,
            ),
        ),
        201,
    )
    expect(
        mutate(
            sup,
            base + "/feedback/" + feedback["id"] + "/review",
            dict(
                status="RESOLVED",
                severity="PRIVATE_M09",
                assignee_membership_id=None,
                resolution_note="SYNTHETIC experience reviewed; evidence status unchanged",
                linked_github_issue_url=None,
            ),
            feedback["version"],
        ),
        201,
    )
    assert "FAILED" not in drain(env, user)
    safe = expect(citizen.request("GET", f["case_path"]), 200)
    assert "PRIVATE_M09" not in str(safe)
    assert safe["verification_summary"] == "NOT_APPLICABLE"
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM repair_records")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM verification_records")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM work_investigation_findings")["n"] == 1
        assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM appointment_events")["n"] == 2
        assert one(c, "SELECT count(*) AS n FROM feedback_events")["n"] >= 1
        assert one(c, "SELECT count(*) AS n FROM service_request_events")["n"] >= 5


def test_lost_submission_response_restart_replay_and_current_ownership(env):
    citizen = resident(env, "m09-resident@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    key = uuid4()
    body = submission(description="SYNTHETIC M09 committed reply intentionally discarded")
    response = mutate(citizen, base + "/service-requests", body, key=key)
    assert response.status_code == 201
    del response  # emulate a client that never received the committed response
    restarted_app = create_app(env["settings"])
    restarted = Client(restarted_app)
    restarted.http.cookies.update(citizen.http.cookies)
    try:
        replay = expect(mutate(restarted, base + "/service-requests", body, key=key), 201)
        assert len(expect(restarted.request("GET", base + "/service-requests"), 200)["items"]) == 1
        with env["owner"].begin() as c:
            assert one(c, "SELECT count(*) AS n FROM service_requests")["n"] == 1
        stranger = resident(env, "m09-stranger@example.invalid")
        denied = stranger.request("GET", base + "/service-requests/" + replay["id"])
        expect(denied, 404)
        assert replay["tracking_reference"] not in denied.text
        expect(
            mutate(
                restarted, base + "/service-requests", {**body, "category": "LOW_PRESSURE"}, key=key
            ),
            409,
        )
    finally:
        restarted.close()
        restarted_app.state.engine.dispose()


def test_window_withdrawal_races_confirmation_with_durable_single_winner(env):
    f = booking_fixture(env)
    request = request_visit(f)
    sup = f["supervisor"]
    second = login(env, "supervisor@example.invalid")
    path = f["base"] + "/appointment-requests/" + request["id"]
    row = expect(sup.request("GET", path), 200)
    calendar = expect(sup.request("GET", f["base"] + "/dispatch/technicians"), 200)["items"][0]
    window = f["windows"][0]
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(
            mutate,
            sup,
            path + "/decisions",
            dict(
                decision="CONFIRM_REQUESTED",
                expectations=row["expectations"],
                public_message="SYNTHETIC confirmation",
                internal_reason="SYNTHETIC race",
            ),
            row["version"],
        )
        b = pool.submit(
            mutate,
            second,
            f["base"] + "/dispatch/appointment-windows/" + window["id"] + "/withdrawals",
            dict(
                expected_calendar_version=calendar["calendar_version"],
                reason="SYNTHETIC racing withdrawal",
            ),
            window["version"],
        )
        confirmed, withdrawn = a.result(), b.result()
    assert (confirmed.status_code, withdrawn.status_code) in {
        (200, 412),
        (200, 409),
        (409, 200),
        (412, 200),
    }
    with env["owner"].begin() as c:
        bookings = one(c, "SELECT count(*) AS n FROM appointments WHERE status='CONFIRMED'")["n"]
        allocations = one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"]
        state = one(c, "SELECT state FROM appointment_windows WHERE id=:i", i=window["id"])["state"]
        assert bookings == allocations == (1 if confirmed.status_code == 200 else 0)
        assert (state == "WITHDRAWN") == (withdrawn.status_code == 200)


def test_overrun_is_manual_and_does_not_consume_future_reservation(env):
    f = booking_fixture(env)
    first = confirm(f, request_visit(f))["appointment"]
    # Separate accepted service/work for the same authorized technician and shift.
    # A non-overlapping future unavailability block exercises the shared ledger.
    roster = expect(f["supervisor"].request("GET", f["base"] + "/dispatch/technicians"), 200)[
        "items"
    ][0]
    from datetime import timedelta

    block = expect(
        mutate(
            f["supervisor"],
            f["base"] + "/dispatch/blocks",
            dict(
                technician_membership_id=f["tech_membership"]["id"],
                expected_calendar_version=roster["calendar_version"],
                kind="UNAVAILABLE",
                interval=dict(
                    start_at=(f["start"] + timedelta(hours=5)).isoformat(),
                    end_at=(f["start"] + timedelta(hours=6)).isoformat(),
                ),
                work_order_id=None,
                expected_work_version=None,
                reason_code="SYNTHETIC",
                internal_reason="SYNTHETIC future reserved unavailable interval",
            ),
            roster["profile_version"],
        ),
        201,
    )
    first = visit_event(f, first, "CHECK_IN")
    first = visit_event(f, first, "OVERRUN_REPORTED")
    assert first["status"] == "CHECKED_IN"
    with env["owner"].begin() as c:
        assert one(c, "SELECT active FROM dispatch_allocations WHERE id=:i", i=block["id"])[
            "active"
        ]
        assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == 2
        assert one(c, "SELECT count(*) AS n FROM repair_records")["n"] == 0


def test_hostile_text_dto_and_pooled_context_do_not_expand_access(env):
    citizen = resident(env, "m09-security@example.invalid")
    stranger = resident(env, "m09-other@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    marker = "<img src=x onerror=alert('M09')> '; DROP TABLE users; --"
    row = expect(mutate(citizen, base + "/service-requests", submission(description=marker)), 201)
    safe = expect(citizen.request("GET", base + "/service-requests/" + row["id"]), 200)
    assert safe["description"] == marker  # rendering, not JSON, must escape this text
    forbidden = {
        "internal_reason",
        "owner_membership_id",
        "hmac_key",
        "password_hash",
        "seed",
        "truth",
    }

    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for item in value.values():
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)

    inspect(safe)
    for path in (
        base + "/service-requests/" + row["id"],
        base.replace(str(env["org"]["id"]), str(env["other"]["id"]))
        + "/service-requests/"
        + row["id"],
    ):
        denied = stranger.request("GET", path)
        expect(denied, 404)
        assert marker not in denied.text and row["tracking_reference"] not in denied.text
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM users")["n"] == 4
        member = one(
            c, "SELECT owner_membership_id FROM service_requests WHERE id=:i", i=row["id"]
        )["owner_membership_id"]
        user = one(c, "SELECT user_id FROM organization_memberships WHERE id=:i", i=member)[
            "user_id"
        ]
    for _ in range(5):
        with env["app"].state.engine.begin() as c:
            context(c, user, env["org"]["id"])
            assert len(query(c, "SELECT id FROM service_requests")) == 1
        with env["app"].state.engine.begin() as c:
            assert query(c, "SELECT id FROM service_requests") == []
            assert query(c, "SELECT id FROM service_request_events") == []
