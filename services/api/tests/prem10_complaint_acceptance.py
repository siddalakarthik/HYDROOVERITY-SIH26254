"""Explicit pre-M10 F01 acceptance; synthetic PostgreSQL fixtures only."""

import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from helpers import expect, mutate
from test_communications import drain, fixture
from test_service_foundation import create, resident
from test_workflow import complaint_body

from hydro.config import ROOT
from hydro.db import execute, one, query
from hydro.notification_worker import run_once


def preferences(citizen, base, categories):
    current = expect(citizen.request("GET", base + "/notification-preferences"), 200)
    return expect(
        mutate(
            citizen,
            base + "/notification-preferences",
            {
                "channels": {"in_app": True, "email": False, "sms": False, "push": False},
                "event_categories": categories,
                "quiet_hours": None,
            },
            current["version"],
            method="PUT",
        ),
        200,
    )


def inbox(citizen, base):
    return expect(citizen.request("GET", base + "/notifications"), 200)["items"]


def review(supervisor, base, complaint):
    return expect(
        mutate(
            supervisor,
            base + "/complaints/" + complaint["id"] + "/review",
            {
                "public_status": "UNDER_REVIEW",
                "public_message": "SYNTHETIC-PUBLIC-MESSAGE-SENTINEL",
                "internal_reason": "SYNTHETIC-PRIVATE-REASON-SENTINEL",
                "incident_id": None,
            },
            complaint["version"],
        ),
        200,
    )


def test_f01_receipt_lifecycle_delivery_and_worker_dedup(env):
    citizen, supervisor, _, user, base = fixture(env)
    preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    body = {**complaint_body(), "description": "SYNTHETIC-DESCRIPTION-SENTINEL"}
    key = uuid4()
    complaint = expect(mutate(citizen, base + "/complaints", body, key=key), 201)
    assert complaint["tracking_number"].startswith("HYD-")
    for _ in range(2):
        assert expect(mutate(citizen, base + "/complaints", body, key=key), 201) == complaint
    expect(mutate(citizen, base + "/complaints", complaint_body(), key=key), 409)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda _: run_once(env["app"].state.engine, user, env["org"]["id"]), range(2))
        )
    assert sorted(results) == ["IDLE", "SUCCEEDED"]
    assert len(inbox(citizen, base)) == 1
    path = base + "/complaints/" + complaint["id"]
    review(supervisor, base, complaint)
    assert drain(env, user) == ["SUCCEEDED"]
    current = expect(citizen.request("GET", path), 200)
    expect(
        mutate(
            citizen,
            path + "/follow-ups",
            {
                "description": "SYNTHETIC-FOLLOWUP-SENTINEL",
                "photo_consent": False,
                "attachment_ids": [],
            },
            current["version"],
        ),
        200,
    )
    assert drain(env, user) == ["SUCCEEDED"]
    with env["owner"].begin() as c:
        execute(c, "UPDATE background_jobs SET state='QUEUED' WHERE state='SUCCEEDED'")
    assert drain(env, user) == ["SUCCEEDED"] * 3
    items = inbox(citizen, base)
    assert len(items) == 3
    assert all(item["event_category"] == "COMPLAINT_PROGRESS" for item in items)
    assert all(item["resource_path"] == "/complaints/" + complaint["id"] for item in items)
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM citizen_complaints")["n"] == 1
        assert one(c, "SELECT count(*) AS n FROM notification_delivery_attempts")["n"] == 3
        assert one(c, "SELECT count(*) AS n FROM background_jobs")["n"] == 3
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM domain_events WHERE resource_type IN ('citizen_complaints','complaint_status_events')",
            )["n"]
            == 3
        )
        for table in ("service_requests", "incidents", "work_orders"):
            assert one(c, f"SELECT count(*) AS n FROM {table}")["n"] == 0
        notices = query(c, "SELECT * FROM notifications")
        assert {n["resource_version"] for n in notices} == {1, 2, 3}
        assert all(n["service_request_id"] is None for n in notices)
        safe = json.dumps(
            {
                "inbox": items,
                "jobs": query(c, "SELECT targets FROM background_jobs"),
                "events": query(c, "SELECT safe_summary FROM domain_events"),
            },
            default=str,
        )
        assert "SENTINEL" not in safe
        assert "SYNTHETIC locality only" not in safe


@pytest.mark.parametrize("categories", [None, ["SERVICE_PROGRESS"]])
def test_f01_default_and_existing_service_opt_in_do_not_enable_complaints(env, categories):
    citizen, _, _, user, base = fixture(env)
    if categories is not None:
        preferences(citizen, base, categories)
    expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    assert drain(env, user) == ["SUCCEEDED"]
    assert inbox(citizen, base) == []
    with env["owner"].begin() as c:
        row = one(c, "SELECT state,safe_error_code,attempt_number FROM notifications")
        assert row == {
            "state": "SUPPRESSED",
            "safe_error_code": "PREFERENCES_DISABLED",
            "attempt_number": 0,
        }


def test_f01_pending_snapshot_is_suppressed_after_parent_version_changes(env):
    citizen, supervisor, _, user, base = fixture(env)
    preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    complaint = expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    review(supervisor, base, complaint)
    assert drain(env, user) == ["SUCCEEDED", "SUCCEEDED"]
    assert len(inbox(citizen, base)) == 1
    with env["owner"].begin() as c:
        rows = query(
            c, "SELECT resource_version,state FROM notifications ORDER BY resource_version"
        )
        assert rows == [
            {"resource_version": 1, "state": "SUPPRESSED"},
            {"resource_version": 2, "state": "DELIVERED"},
        ]


def test_f01_owner_tenant_and_read_receipt_reauthorization(env):
    citizen, _, _, user, base = fixture(env)
    preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    complaint = expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    drain(env, user)
    item = inbox(citizen, base)[0]
    path = base + "/notifications/" + item["id"] + "/read"
    outsider = resident(env, "f01-outsider@example.invalid")
    assert inbox(outsider, base) == []
    expect(mutate(outsider, path, None, item["version"]), 404)
    foreign_env = {**env, "org": env["other"]}
    foreign = resident(foreign_env, "f01-foreign@example.invalid")
    other_base = f"/api/v1/orgs/{env['other']['id']}"
    assert inbox(foreign, other_base) == []
    expect(
        mutate(
            foreign, other_base + "/notifications/" + item["id"] + "/read", None, item["version"]
        ),
        404,
    )
    expect(mutate(foreign, path, None, item["version"]), 404)
    key = uuid4()
    receipt = expect(mutate(citizen, path, None, item["version"], key), 200)
    assert expect(mutate(citizen, path, None, item["version"], key), 200) == receipt
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE citizen_complaints SET reporter_id=(SELECT m.id FROM organization_memberships m JOIN users u ON u.id=m.user_id WHERE u.email_normalized='f01-outsider@example.invalid') WHERE id=:i",
            i=complaint["id"],
        )
    assert inbox(citizen, base) == []
    assert inbox(outsider, base) == []
    expect(mutate(citizen, path, None, item["version"], key), 404)


def test_f01_revoked_membership_suppresses_pending_and_revoked_session_denied(env):
    citizen, _, _, user, base = fixture(env)
    preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE organization_memberships SET status='SUSPENDED' WHERE id=(SELECT reporter_id FROM citizen_complaints)",
        )
    assert drain(env, user) == ["SUCCEEDED"]
    with env["owner"].begin() as c:
        assert one(c, "SELECT state,attempt_number FROM notifications") == {
            "state": "SUPPRESSED",
            "attempt_number": 0,
        }
    expect(citizen.request("GET", base + "/notifications"), 404)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE sessions SET revoked_at=now() WHERE user_id=(SELECT user_id FROM organization_memberships WHERE id=(SELECT reporter_id FROM citizen_complaints))",
        )
    expect(citizen.request("GET", base + "/notifications"), 401)


def test_f01_current_complaint_permission_required_for_delivery_inbox_and_replay(env):
    citizen, supervisor, _, user, base = fixture(env)
    preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    complaint = expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    drain(env, user)
    item = inbox(citizen, base)[0]
    path = base + "/notifications/" + item["id"] + "/read"
    key = uuid4()
    expect(mutate(citizen, path, None, item["version"], key), 200)
    review(supervisor, base, complaint)
    with env["owner"].begin() as c:
        execute(
            c,
            "DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE code='CITIZEN') AND permission_id IN (SELECT id FROM permissions WHERE code='complaints.read')",
        )
    assert drain(env, user) == ["SUCCEEDED"]
    assert inbox(citizen, base) == []
    expect(mutate(citizen, path, None, item["version"], key), 404)
    with env["owner"].begin() as c:
        assert one(
            c, "SELECT state,attempt_number FROM notifications WHERE resource_version=2"
        ) == {"state": "SUPPRESSED", "attempt_number": 0}


def test_f01_enqueue_failure_rolls_back_complaint_and_receipt(env, monkeypatch):
    citizen, _, _, _, base = fixture(env)

    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic queue failure")

    key = uuid4()
    with monkeypatch.context() as patch:
        patch.setattr("hydro.notification_worker.enqueue", fail)
        with pytest.raises(RuntimeError, match="Synthetic queue failure"):
            mutate(citizen, base + "/complaints", complaint_body(), key=key)
    with env["owner"].begin() as c:
        for table in (
            "citizen_complaints",
            "complaint_status_events",
            "background_jobs",
            "notifications",
            "evidence_records",
        ):
            assert one(c, f"SELECT count(*) AS n FROM {table}")["n"] == 0
        assert (
            one(c, "SELECT count(*) AS n FROM idempotency_records WHERE operation_key=:k", k=key)[
                "n"
            ]
            == 0
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM domain_events WHERE resource_type='citizen_complaints'",
            )["n"]
            == 0
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM audit_logs WHERE resource_type='citizen_complaints'",
            )["n"]
            == 0
        )
    expect(mutate(citizen, base + "/complaints", complaint_body(), key=key), 201)


@pytest.mark.parametrize("stored", ["preferences", "queued", "delivered"])
def test_f01_migration_roundtrip_and_data_preservation(env, stored):
    config = Config(str(ROOT / "services/api/alembic.ini"))
    command.downgrade(config, "m07_c_001")
    command.upgrade(config, "head")
    citizen, _, _, user, base = fixture(env)
    if stored in {"preferences", "delivered"}:
        preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    if stored in {"queued", "delivered"}:
        expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    if stored == "delivered":
        drain(env, user)
        # Isolate the notification-row guard from both other downgrade guards.
        preferences(citizen, base, [])
        with env["owner"].begin() as c:
            execute(c, "UPDATE background_jobs SET targets='[]'::jsonb")
    with pytest.raises(RuntimeError, match="non-destructive downgrade refused"):
        command.downgrade(config, "m07_c_001")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_002"
        if stored == "preferences":
            assert (
                one(
                    c,
                    "SELECT count(*) AS n FROM notification_preferences WHERE event_categories ? 'COMPLAINT_PROGRESS'",
                )["n"]
                == 1
            )
        else:
            assert one(c, "SELECT count(*) AS n FROM citizen_complaints")["n"] == 1
    if stored == "delivered":
        assert len(inbox(citizen, base)) == 1


def test_f01_pending_recipient_is_not_retargeted_after_ownership_change(env):
    citizen, _, _, user, base = fixture(env)
    preferences(citizen, base, ["COMPLAINT_PROGRESS"])
    successor = resident(env, "f01-successor@example.invalid")
    preferences(successor, base, ["COMPLAINT_PROGRESS"])
    complaint = expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    with env["owner"].begin() as c:
        original = one(
            c, "SELECT reporter_id FROM citizen_complaints WHERE id=:i", i=complaint["id"]
        )
        # Preserve version deliberately so this isolates ownership authorization.
        execute(
            c,
            "UPDATE citizen_complaints SET reporter_id=(SELECT m.id FROM organization_memberships m JOIN users u ON u.id=m.user_id WHERE u.email_normalized='f01-successor@example.invalid') WHERE id=:i",
            i=complaint["id"],
        )
    assert drain(env, user) == ["SUCCEEDED"]
    assert inbox(citizen, base) == []
    assert inbox(successor, base) == []
    with env["owner"].begin() as c:
        notice = one(
            c, "SELECT recipient_id,state,attempt_number,safe_error_code FROM notifications"
        )
        assert notice == {
            "recipient_id": original["reporter_id"],
            "state": "SUPPRESSED",
            "attempt_number": 0,
            "safe_error_code": "RECIPIENT_UNAVAILABLE",
        }
        assert one(c, "SELECT count(*) AS n FROM notification_delivery_attempts")["n"] == 0


def test_f01_upgrade_preserves_configured_service_preferences_and_delivery_history(env):
    citizen, _, _, user, base = fixture(env)
    preferences(citizen, base, ["SERVICE_PROGRESS"])
    create(citizen, base)
    assert drain(env, user) == ["SUCCEEDED"]
    original_inbox = inbox(citizen, base)
    assert len(original_inbox) == 1
    tables = (
        "notification_preferences",
        "notifications",
        "notification_delivery_attempts",
        "background_jobs",
    )
    with env["owner"].begin() as c:
        original = {table: query(c, f"SELECT * FROM {table} ORDER BY id") for table in tables}
    config = Config(str(ROOT / "services/api/alembic.ini"))
    # These rows use only the previous schema's categories and resource types.
    command.downgrade(config, "m07_c_001")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "m07_c_001"
        assert {
            table: query(c, f"SELECT * FROM {table} ORDER BY id") for table in tables
        } == original
    command.upgrade(config, "head")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_002"
        assert {
            table: query(c, f"SELECT * FROM {table} ORDER BY id") for table in tables
        } == original
    assert inbox(citizen, base) == original_inbox
    assert drain(env, user) == []
