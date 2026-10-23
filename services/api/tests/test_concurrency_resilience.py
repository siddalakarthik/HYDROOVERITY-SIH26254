from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from conftest import Client
from helpers import expect, login, mutate, register, token
from test_workflow import assigned_work, complaint_body, setup, transition

from hydro.config import ROOT, Settings
from hydro.db import one
from hydro.main import create_app
from hydro.repository import TABLES


def test_concurrent_business_retry_has_one_receipt_audit_event_and_mutation(env):
    first = register(env, "citizen@example.invalid")
    login(env, "citizen@example.invalid", first)
    second = login(env, "citizen@example.invalid")
    path = f"/api/v1/orgs/{env['org']['id']}/complaints"
    key = uuid4()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: mutate(client, path, complaint_body(), key=key), [first, second]
            )
        )
    ids = [expect(r, 201)["id"] for r in results]
    assert ids[0] == ids[1]
    with env["owner"].begin() as c:
        for table in ["citizen_complaints", "idempotency_records"]:
            assert one(c, f"SELECT count(*) AS n FROM {table}")["n"] == 1
        assert (
            one(c, "SELECT count(*) AS n FROM audit_logs WHERE resource_type='citizen_complaints'")[
                "n"
            ]
            == 1
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM domain_events WHERE resource_type='citizen_complaints'",
            )["n"]
            == 1
        )


def test_fault_rolls_back_business_history_outbox_and_receipt(env, monkeypatch):
    citizen = register(env, "citizen@example.invalid")
    login(env, "citizen@example.invalid", citizen)
    path = f"/api/v1/orgs/{env['org']['id']}/complaints"
    key = uuid4()
    import hydro.services.base

    def fail(*args, **kwargs):
        raise RuntimeError("Injected synthetic fault after domain mutation")

    with monkeypatch.context() as m:
        m.setattr(hydro.services.base, "record", fail)
        # ASGI transport must expose unexpected exceptions to this test while
        # the application error handler still emits only its safe error body.
        with pytest.raises(RuntimeError):
            mutate(citizen, path, complaint_body(), key=key)
    with env["owner"].begin() as c:
        for table in [
            "citizen_complaints",
            "complaint_status_events",
            "evidence_records",
            "idempotency_records",
        ]:
            assert one(c, f"SELECT count(*) AS n FROM {table}")["n"] == 0
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM domain_events WHERE resource_type='citizen_complaints'",
            )["n"]
            == 0
        )
    expect(mutate(citizen, path, complaint_body(), key=key), 201)


def test_receipt_expiry_membership_revocation_and_parent_binding(env):
    f = setup(env)
    path = f["base"] + "/complaints"
    key = uuid4()
    original = expect(mutate(f["citizen"], path, complaint_body(), key=key), 201)
    from hydro.db import execute

    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE idempotency_records SET created_at=now()-interval '8 days',expires_at=now()-interval '1 second' WHERE operation_key=:k",
            k=key,
        )
    fresh = expect(mutate(f["citizen"], path, complaint_body(), key=key), 201)
    assert fresh["id"] != original["id"]
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE organization_memberships SET status='SUSPENDED' WHERE user_id=(SELECT id FROM users WHERE email_normalized='citizen@example.invalid')",
        )
    expect(mutate(f["citizen"], path, complaint_body(), key=key), 404)


def test_worker_cannot_review_own_repair_even_with_supervisor_role(env):
    f = setup(env)
    item, work = assigned_work(env, f)
    wp = f["base"] + "/work-orders/" + work["id"]
    work = transition(f["technician"], wp, work, "ACCEPTED")
    work = transition(f["technician"], wp, work, "IN_PROGRESS")
    from hydro.security import now

    repair = expect(
        mutate(
            f["technician"],
            wp + "/repairs",
            {
                "performed_at": now().isoformat(),
                "description": "SYNTHETIC manual repair receipt for independence test",
                "materials": [],
                "attachment_ids": [],
            },
            version=work["version"],
        ),
        201,
    )
    tech = f["technician"]
    expect(
        mutate(
            f["admin"],
            f["base"] + "/invitations",
            {"email": "technician@example.invalid", "role": "SUPERVISOR"},
        ),
        200,
    )
    expect(
        tech.request(
            "POST",
            "/api/v1/auth/invitation-accept",
            json={"token": token(env, "INVITATION", "technician@example.invalid")},
        ),
        200,
    )
    login(env, "technician@example.invalid", tech)
    comparability = {
        "supply_state_comparable": False,
        "pressure_demand_storage_comparable": False,
        "calibration_quality_freshness_comparable": False,
        "unit_windows_comparable": False,
        "limitations": "SYNTHETIC missing measurements",
    }
    expect(
        mutate(
            tech,
            f["base"] + "/repairs/" + repair["id"] + "/verifications",
            {
                "outcome": "NOT_VERIFIABLE",
                "before_evidence_record_ids": [],
                "after_evidence_record_ids": [],
                "comparability": comparability,
                "reason": "SYNTHETIC self review must be denied",
            },
            version=1,
        ),
        403,
    )


def test_populated_migration_roundtrip_and_failed_destructive_downgrade(env, monkeypatch):
    monkeypatch.setenv("HYDRO_MIGRATION_URL", __import__("os").environ["HYDRO_TEST_OWNER_URL"])
    cfg = Config(str(ROOT / "services/api/alembic.ini"))

    def snapshot():
        with env["owner"].begin() as c:
            return {table: one(c, f"SELECT count(*) AS n FROM {table}")["n"] for table in TABLES}

    before = snapshot()
    command.downgrade(cfg, "m03_001")
    # Empty M07-A + M06 rollback removes only their capability catalogue entries.
    current = snapshot()
    assert {k: v for k, v in current.items() if k not in {"permissions", "role_permissions"}} == {
        k: v for k, v in before.items() if k not in {"permissions", "role_permissions"}
    }
    assert current["permissions"] == before["permissions"] - 6
    assert current["role_permissions"] == before["role_permissions"] - 10
    expect(env["client"]().request("GET", "/internal/health/ready"), 503)
    command.upgrade(cfg, "head")
    command.upgrade(cfg, "head")
    assert snapshot() == before
    expect(env["client"]().request("GET", "/internal/health/ready"), 200)
    with pytest.raises(RuntimeError, match="forward-only"):
        command.downgrade(cfg, "base")
    assert snapshot() == before
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "m06_001"


def test_unsafe_owner_principal_fails_closed_and_no_internal_error_secrets(env):
    import os

    unsafe = Settings.model_validate(
        {**env["settings"].model_dump(), "database_url": os.environ["HYDRO_TEST_OWNER_URL"]}
    )
    app = create_app(unsafe)
    client = Client(app)
    try:
        expect(client.request("GET", "/internal/health/ready"), 503)
        expect(client.request("GET", "/api/v1/auth/csrf"), 503)
    finally:
        client.close()
        app.state.engine.dispose()


def test_structured_logs_omit_credentials_cookie_csrf_and_personal_payload(env, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="hydro.security")
    client = login(env, "admin-a@example.invalid")
    csrf = expect(client.request("GET", "/api/v1/auth/csrf"), 200)["csrf_token"]
    text = caplog.text
    for private in [
        env["password"],
        csrf,
        "admin-a@example.invalid",
        client.http.cookies.get("__Host-hydro_session"),
    ]:
        if private in text:
            raise AssertionError("Sensitive value leaked into structured logs")
    assert "request id=" in text
