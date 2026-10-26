"""Synthetic PostgreSQL communications acceptance, never delivery to real people."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from helpers import expect, login, mutate, provision
from test_service_foundation import create, resident, triage

from hydro.db import execute, one, query
from hydro.notification_worker import run_once


def fixture(env):
    admin = login(env, "admin-a@example.invalid")
    sup, membership = provision(
        env, "SUPERVISOR", "communications-supervisor@example.invalid", admin
    )
    citizen = resident(env, "communications-resident@example.invalid")
    with env["owner"].begin() as c:
        user = one(
            c, "SELECT user_id FROM organization_memberships WHERE id=:i", i=membership["id"]
        )["user_id"]
    return citizen, sup, admin, user, f"/api/v1/orgs/{env['org']['id']}"


def enable(client, base):
    p = expect(client.request("GET", base + "/notification-preferences"), 200)
    body = {k: p[k] for k in ("channels", "event_categories", "quiet_hours")}
    body["channels"]["in_app"] = True
    body["event_categories"] = [
        "SERVICE_PROGRESS",
        "APPOINTMENT",
        "WORK_ASSIGNMENT",
        "SERVICE_FEEDBACK",
    ]
    return expect(
        mutate(client, base + "/notification-preferences", body, p["version"], method="PUT"), 200
    )


def drain(env, user):
    results = []
    for _ in range(30):
        result = run_once(env["app"].state.engine, user, env["org"]["id"])
        if result == "IDLE":
            return results
        results.append(result)
    raise AssertionError("Worker did not drain bounded synthetic queue")


def test_preferences_real_inbox_safe_audit_and_monotonic_receipt(env):
    citizen, sup, admin, user, base = fixture(env)
    pref = enable(citizen, base)
    case = create(citizen, base)
    case = triage(sup, base + "/service-requests/" + case["id"], case, "UNDER_REVIEW")
    assert "FAILED" not in drain(env, user)
    inbox = expect(citizen.request("GET", base + "/notifications"), 200)
    assert len(inbox["items"]) == 1  # old intake snapshot is suppressed after triage
    item = inbox["items"][0]
    assert item["event_category"] == "SERVICE_PROGRESS" and not item["read"]
    assert "private" not in item["message"] and "internal_reason" not in str(inbox)
    key = uuid4()
    path = base + "/notifications/" + item["id"] + "/read"
    result = expect(mutate(citizen, path, None, item["version"], key), 200)
    assert expect(mutate(citizen, path, None, item["version"], key), 200) == result
    again = expect(mutate(citizen, path, None, result["version"]), 200)
    assert again == result
    outsider = resident(env, "other-reader@example.invalid")
    expect(mutate(outsider, path, None, item["version"]), 404)
    audit = expect(
        sup.request("GET", base + "/service-requests/" + case["id"] + "/delivery-audit"), 200
    )
    assert {i["state"] for i in audit["items"]} == {"SUPPRESSED", "DELIVERED"}
    assert all(
        set(i)
        == {
            "notification_id",
            "event_kind",
            "channel",
            "state",
            "attempt_number",
            "attempted_at",
            "next_attempt_at",
            "safe_error_code",
        }
        for i in audit["items"]
    )
    expect(admin.request("GET", base + "/service-requests/" + case["id"] + "/delivery-audit"), 403)
    assert pref["version"] == 2


def test_feedback_creation_review_idempotency_privacy_and_case_guards(env):
    citizen, sup, admin, user, base = fixture(env)
    enable(citizen, base)
    body = {
        "summary": "Synthetic product feedback",
        "description": "Synthetic feedback for engineering acceptance",
        "complaint_id": None,
    }
    key = uuid4()
    item = expect(mutate(citizen, base + "/feedback", body, key=key), 201)
    assert expect(mutate(citizen, base + "/feedback", body, key=key), 201)["id"] == item["id"]
    expect(
        mutate(
            citizen,
            base + "/feedback",
            {**body, "summary": "Different synthetic feedback"},
            key=key,
        ),
        409,
    )
    review = {
        "status": "RESOLVED",
        "severity": "PRIVATE_SYNTHETIC",
        "assignee_membership_id": None,
        "resolution_note": "Synthetic public explanation",
        "linked_github_issue_url": None,
    }
    reviewed = expect(
        mutate(sup, base + "/feedback/" + item["id"] + "/review", review, item["version"]), 201
    )
    assert reviewed["resolution_note"] == review["resolution_note"]
    own = expect(citizen.request("GET", base + "/feedback"), 200)
    assert len(own["items"]) == 1 and "PRIVATE_SYNTHETIC" not in str(own)
    stranger = resident(env, "stranger-feedback@example.invalid")
    assert expect(stranger.request("GET", base + "/feedback"), 200)["items"] == []
    case = create(citizen, base)
    expect(
        mutate(
            citizen,
            base + "/feedback",
            {**body, "service_request_id": case["id"], "service_rating": 5},
        ),
        409,
    )
    expect(mutate(stranger, base + "/feedback", {**body, "service_request_id": case["id"]}), 404)
    assert "FAILED" not in drain(env, user)
    assert any(
        i["event_category"] == "SERVICE_FEEDBACK"
        for i in expect(citizen.request("GET", base + "/notifications"), 200)["items"]
    )


def test_preference_and_mutation_security_boundaries(env):
    citizen, sup, admin, user, base = fixture(env)
    current = expect(citizen.request("GET", base + "/notification-preferences"), 200)
    assert not current["channels"]["in_app"]
    body = {k: current[k] for k in ("channels", "event_categories", "quiet_hours")}
    expect(mutate(citizen, base + "/notification-preferences", body, method="PUT"), 428)
    expect(mutate(citizen, base + "/notification-preferences", body, 999, method="PUT"), 412)
    expect(
        mutate(
            citizen,
            base + "/notification-preferences",
            {**body, "recipient_id": str(uuid4())},
            1,
            method="PUT",
        ),
        422,
    )
    expect(
        mutate(
            citizen,
            base + "/notification-preferences",
            {**body, "channels": {**body["channels"], "email": True}},
            1,
            method="PUT",
        ),
        422,
    )
    expect(citizen.request("GET", f"/api/v1/orgs/{env['other']['id']}/notifications"), 404)
    expect(citizen.raw("PUT", base + "/notification-preferences", json=body), 403)
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM notification_preferences WHERE organization_id=:o",
                o=env["org"]["id"],
            )["n"]
            == 3
        )


def test_worker_competing_claims_restart_dedup_and_revocation(env):
    citizen, sup, admin, user, base = fixture(env)
    enable(citizen, base)
    case = create(citizen, base)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda _: run_once(env["app"].state.engine, user, env["org"]["id"]), range(2))
        )
    assert sorted(results) == ["IDLE", "SUCCEEDED"]
    with env["owner"].begin() as c:
        execute(c, "UPDATE background_jobs SET state='QUEUED' WHERE state='SUCCEEDED'")
    assert drain(env, user) == ["SUCCEEDED"]
    assert len(expect(citizen.request("GET", base + "/notifications"), 200)["items"]) == 1
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM notification_delivery_attempts")["n"] == 1
    triage(sup, base + "/service-requests/" + case["id"], case, "UNDER_REVIEW")
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE organization_memberships SET status='SUSPENDED' WHERE id=(SELECT owner_membership_id FROM service_requests WHERE id=:i)",
            i=case["id"],
        )
    assert drain(env, user) == ["SUCCEEDED"]
    with env["owner"].begin() as c:
        latest = one(c, "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 1")
        assert latest["state"] == "SUPPRESSED" and latest["attempt_number"] == 0


def test_worker_three_attempt_limit_and_unconfigured_retry_are_honest(env, monkeypatch):
    citizen, sup, admin, user, base = fixture(env)
    enable(citizen, base)
    create(citizen, base)

    def fail(*args):
        raise RuntimeError("Synthetic processor failure, never emitted to customer")

    monkeypatch.setattr("hydro.notification_worker.deliver", fail)
    assert run_once(env["app"].state.engine, user, env["org"]["id"]) == "FAILED"
    with env["owner"].begin() as c:
        item = one(c, "SELECT * FROM notifications")
        assert item["state"] == "FAILED" and item["attempt_number"] == 1
        assert item["safe_error_code"] == "RETRY_POLICY_UNCONFIGURED"
    create(citizen, base)
    for attempt in range(3):
        assert (
            run_once(
                env["app"].state.engine, user, env["org"]["id"], (1, 2), "SYNTHETIC-TEST-POLICY"
            )
            == "FAILED"
        )
        with env["owner"].begin() as c:
            execute(c, "UPDATE background_jobs SET next_attempt_at=now() WHERE state='QUEUED'")
    assert (
        run_once(env["app"].state.engine, user, env["org"]["id"], (1, 2), "SYNTHETIC-TEST-POLICY")
        == "IDLE"
    )
    with env["owner"].begin() as c:
        item = one(c, "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 1")
        assert item["attempt_number"] == 3 and item["safe_error_code"] == "ATTEMPTS_EXHAUSTED"
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM notification_delivery_attempts WHERE notification_id=:i",
                i=item["id"],
            )["n"]
            == 3
        )


def test_quiet_hours_and_lost_lease_preserve_false_delivery_boundary(env):
    from hydro.notification_worker import quiet_until

    prefs = {
        "quiet_hours": {"start_local": "22:00", "end_local": "06:00", "timezone": "Asia/Kolkata"}
    }
    assert (
        quiet_until(prefs, datetime(2026, 10, 25, 18, tzinfo=UTC))
        .isoformat()
        .endswith("06:00:00+05:30")
    )
    assert quiet_until(prefs, datetime(2026, 10, 25, 8, tzinfo=UTC)) is None
    citizen, sup, admin, user, base = fixture(env)
    enable(citizen, base)
    create(citizen, base)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE background_jobs SET state='RUNNING',attempts=1,lease_token=:t,lease_until=now()-interval '1 second'",
            t=uuid4(),
        )
    assert run_once(env["app"].state.engine, user, env["org"]["id"]) == "RECOVERED"
    assert expect(citizen.request("GET", base + "/notifications"), 200)["items"] == []
    with env["owner"].begin() as c:
        assert one(c, "SELECT state FROM background_jobs")["state"] == "FAILED"


def test_closed_service_feedback_no_operational_or_scientific_side_effect(env):
    citizen, sup, admin, user, base = fixture(env)
    case = create(citizen, base)
    with env["owner"].begin() as c:
        # Synthetic fixture preparation only; actual public commands remain guarded.
        execute(c, "UPDATE service_requests SET status='CANCELLED' WHERE id=:i", i=case["id"])
    body = {
        "summary": "Synthetic cancelled case experience",
        "description": "Synthetic customer experience, no physical claims",
        "complaint_id": None,
        "service_request_id": case["id"],
        "service_rating": 5,
    }
    item = expect(mutate(citizen, base + "/feedback", body), 201)
    review = {
        "status": "RESOLVED",
        "severity": "PRIVATE",
        "assignee_membership_id": None,
        "resolution_note": "Public synthetic response",
        "linked_github_issue_url": None,
    }
    expect(
        mutate(admin, base + "/feedback/" + item["id"] + "/review", review, item["version"]), 404
    )
    expect(mutate(sup, base + "/feedback/" + item["id"] + "/review", review, item["version"]), 201)
    with env["owner"].begin() as c:
        assert (
            one(c, "SELECT status FROM service_requests WHERE id=:i", i=case["id"])["status"]
            == "CANCELLED"
        )
        assert not query(c, "SELECT id FROM verification_records")
        assert not query(c, "SELECT id FROM repair_records")


def test_atomic_queue_failure_rolls_back_business_state(env, monkeypatch):
    citizen, sup, admin, user, base = fixture(env)
    from test_service_foundation import submission

    def unavailable(*args):
        raise RuntimeError("SYNTHETIC queue unavailable")

    monkeypatch.setattr("hydro.notification_worker.enqueue", unavailable)
    with pytest.raises(RuntimeError, match="SYNTHETIC queue unavailable"):
        mutate(citizen, base + "/service-requests", submission())
    with env["owner"].begin() as c:
        assert not query(c, "SELECT id FROM service_requests")
        assert not query(c, "SELECT id FROM background_jobs")


def test_real_booking_stale_cancellation_and_current_technician_notifications(env):
    from test_scheduling import booking_fixture, confirm, request_visit

    f = booking_fixture(env)
    enable(f["citizen"], f["base"])
    enable(f["technician"], f["base"])
    with env["owner"].begin() as c:
        user = one(
            c,
            "SELECT m.user_id FROM organization_memberships m JOIN role_assignments a ON a.membership_id=m.id JOIN roles r ON r.id=a.role_id WHERE r.code='SUPERVISOR' AND a.revoked_at IS NULL LIMIT 1",
        )["user_id"]
    visit = confirm(f, request_visit(f))
    assert "FAILED" not in drain(env, user)
    tech = expect(f["technician"].request("GET", f["base"] + "/notifications"), 200)["items"]
    assert any(n["event_category"] == "WORK_ASSIGNMENT" for n in tech)
    # Pending older event after a newer cancellation must never deliver its stale snapshot.
    with env["owner"].begin() as c:
        appointment = one(c, "SELECT * FROM appointments WHERE id=:i", i=visit["appointment"]["id"])
        before = one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"]
        execute(c, "UPDATE appointments SET version=version+1 WHERE id=:i", i=appointment["id"])
        execute(
            c,
            "UPDATE work_orders SET assignee_id=NULL,assignment_version=assignment_version+1 WHERE id=:i",
            i=appointment["work_order_id"],
        )
    assert expect(f["technician"].request("GET", f["base"] + "/notifications"), 200)["items"] == []
    for n in tech:
        expect(
            mutate(
                f["technician"],
                f["base"] + "/notifications/" + n["id"] + "/read",
                None,
                n["version"],
            ),
            404,
        )
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE active")["n"] == before


def test_attachment_paths_remain_unregistered_and_runtime_rls(env):
    from hydro.communications_contracts import DESIGN

    citizen, sup, admin, user, base = fixture(env)
    for path, methods in DESIGN["paths"].items():
        if "/attachments" not in path and "/uploads" not in path:
            continue
        for method in methods:
            target = path.replace("{organization_id}", str(env["org"]["id"]))
            import re

            target = re.sub(r"\{[^}]+\}", str(uuid4()), target)
            expect(citizen.request(method.upper(), "/api/v1" + target), 404)
    from hydro.db import context

    with env["owner"].begin() as c:
        rows = query(
            c,
            "SELECT relname,relrowsecurity,relforcerowsecurity FROM pg_class WHERE relname IN ('notifications','notification_preferences','notification_delivery_attempts','background_jobs','feedback_items','feedback_events')",
        )
        assert len(rows) == 6 and all(
            r["relrowsecurity"] and r["relforcerowsecurity"] for r in rows
        )
    with env["app"].state.engine.begin() as c:
        context(c, organization_id=env["other"]["id"])
        assert query(c, "SELECT id FROM notifications") == []


def test_m07c_empty_roundtrip_and_populated_downgrade_refusal(env):
    from alembic import command
    from alembic.config import Config

    from hydro.config import ROOT

    config = Config(str(ROOT / "services/api/alembic.ini"))
    command.downgrade(config, "m07_b_005")
    command.upgrade(config, "head")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_004"
        assert one(c, "SELECT count(*) AS n FROM notification_preferences")["n"] == 2
        count = one(
            c,
            "SELECT count(*) AS n FROM pg_tables WHERE schemaname='public' AND tablename NOT IN ('spatial_ref_sys','alembic_version')",
        )["n"]
        assert count == 57
    citizen, sup, admin, user, base = fixture(env)
    item = expect(
        mutate(
            citizen,
            base + "/feedback",
            {
                "summary": "Synthetic durable feedback",
                "description": "Synthetic history must survive failed downgrade",
                "complaint_id": None,
            },
        ),
        201,
    )
    with pytest.raises(RuntimeError, match="Populated M07-C history is forward-only"):
        command.downgrade(config, "m07_b_005")
    assert expect(citizen.request("GET", base + "/feedback"), 200)["items"][0]["id"] == item["id"]
