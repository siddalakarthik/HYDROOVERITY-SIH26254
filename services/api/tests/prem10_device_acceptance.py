"""Real disposable PostgreSQL only; no physical device or measured evidence."""

from datetime import timedelta
from uuid import uuid4

import pytest
from helpers import expect, login, mutate, provision
from sqlalchemy.exc import DBAPIError

from hydro.db import execute, one, query
from hydro.security import now, verifier


def device(env, serial="SYNTHETIC proposed device", environment="LABORATORY", kind="WATCH"):
    admin = login(env, "admin-a@example.invalid")
    path = f"/api/v1/orgs/{env['org']['id']}/devices"
    body = {"serial_ref": serial, "device_kind": kind, "provisioning_environment": environment}
    value = expect(mutate(admin, path, body), 201)
    return admin, path + "/" + value["id"], value


def bind(env, value):
    with env["owner"].begin() as c:
        execute(
            c,
            "INSERT INTO device_provisioning_bindings(organization_id,device_id,environment,review_reference,classification) VALUES(:o,:i,:e,'SYNTHETIC TEST ONLY - NOT PHYSICAL APPROVAL','SYNTHETIC_TEST_ONLY')",
            o=env["org"]["id"],
            i=value["id"],
            e=value["environment"],
        )


def issue_body(environment="LABORATORY"):
    return {"environment": environment, "expires_at": (now() + timedelta(hours=1)).isoformat()}


def test_device_registration_is_metadata_only_and_physical_issuance_remains_closed(env):
    admin, path, value = device(env)
    assert value["health"] == "UNKNOWN" and value["environment"] == "LABORATORY"
    assert set(value) == {"id", "serial_ref", "device_kind", "environment", "health", "version"}
    expect(admin.request("GET", path), 200)
    response = mutate(admin, path + "/credentials", issue_body())
    assert expect(response, 503)["error"]["code"] == "PHYSICAL_PROVISIONING_NOT_APPROVED"
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM device_credentials")["n"] == 0
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM idempotency_records WHERE route_template LIKE '%/credentials'",
            )["n"]
            == 0
        )


def test_device_credential_one_time_secret_no_cache_and_no_redisclosure_even_after_receipt_expiry(
    env,
):
    admin, path, value = device(env)
    bind(env, value)
    body, key = issue_body(), uuid4()
    response = mutate(admin, path + "/credentials", body, key=key)
    issued = expect(response, 201)
    assert response.headers["cache-control"] == "no-store"
    assert 32 <= len(issued["one_time_secret"]) <= 300
    expect(mutate(admin, path + "/credentials", body, key=key), 409)
    with env["owner"].begin() as c:
        row = one(c, "SELECT * FROM device_credentials WHERE id=:i", i=issued["id"])
        assert bytes(row["token_hash"]) == verifier(issued["one_time_secret"])
        assert row["scope"] == "SCALAR_TEST_ONLY"
        # Mimic approved expiry cleanup; the persistent issuance key still prevents redisclosure.
        execute(c, "DELETE FROM idempotency_records WHERE route_template LIKE '%/credentials'")
        metadata = query(
            c, "SELECT safe_metadata FROM audit_logs WHERE resource_type='device_credentials'"
        )
        assert metadata == [{"safe_metadata": {}}]
        assert one(c, "SELECT count(*) AS n FROM background_jobs")["n"] == 0
    replay = expect(mutate(admin, path + "/credentials", body, key=key), 409)
    assert "one_time_secret" not in replay
    assert "one_time_secret" not in expect(admin.request("GET", path), 200)
    # A bearer device secret never authenticates human APIs.
    anonymous = env["client"]()
    expect(
        anonymous.request(
            "GET", "/api/v1/me", headers={"Authorization": "Bearer " + issued["one_time_secret"]}
        ),
        401,
    )


def test_device_roles_tenant_ownership_and_current_privilege_are_rechecked_before_replay(env):
    admin, path, value = device(env)
    engineer, _ = provision(env, "ENGINEER", "device-engineer@example.invalid")
    citizen = login(env, "device-engineer@example.invalid", engineer)
    expect(citizen.request("GET", path), 200)
    expect(mutate(citizen, path + "/credentials", issue_body()), 403)
    other = login(env, "admin-b@example.invalid")
    expect(other.request("GET", path.replace(str(env["org"]["id"]), str(env["other"]["id"]))), 404)
    expect(other.request("GET", path), 404)
    bind(env, value)
    key, body = uuid4(), issue_body()
    expect(mutate(admin, path + "/credentials", body, key=key), 201)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE role_assignments SET revoked_at=now() WHERE membership_id=:m",
            m=env["admin"]["id"],
        )
    expect(mutate(admin, path + "/credentials", body, key=key), 403)


def test_device_environment_is_fixed_and_expiry_is_bounded(env):
    admin, path, value = device(env)
    bind(env, value)
    expect(mutate(admin, path + "/credentials", issue_body("FIELD")), 422)
    for stamp in (now() - timedelta(seconds=1), now() + timedelta(days=31)):
        expect(
            mutate(
                admin,
                path + "/credentials",
                {"environment": "LABORATORY", "expires_at": stamp.isoformat()},
            ),
            422,
        )
    expect(
        mutate(admin, path + "/credentials", {**issue_body(), "source_category": "HARDWARE"}), 422
    )
    expect(
        mutate(
            admin,
            path.rsplit("/", 1)[0],
            {
                "serial_ref": "SYNTHETIC wrong virtual",
                "device_kind": "VIRTUAL",
                "provisioning_environment": "FIELD",
            },
        ),
        422,
    )


def test_device_revoke_is_audited_same_device_and_never_reenables_secret(env):
    admin, path, value = device(env)
    bind(env, value)
    issued = expect(mutate(admin, path + "/credentials", issue_body()), 201)
    _, stranger, _ = device(env, "SYNTHETIC second device")
    expect(mutate(admin, stranger + "/credentials/" + issued["id"], None, method="DELETE"), 404)
    key = uuid4()
    for _ in range(2):
        response = mutate(
            admin, path + "/credentials/" + issued["id"], None, key=key, method="DELETE"
        )
        assert expect(response, 200) == {"message": "Credential revoked"}
    with env["owner"].begin() as c:
        assert one(
            c,
            "SELECT revoked_at IS NOT NULL AS revoked FROM device_credentials WHERE id=:i",
            i=issued["id"],
        )["revoked"]
        assert (
            one(c, "SELECT count(*) AS n FROM audit_logs WHERE action LIKE 'devices_delete%'")["n"]
            == 1
        )


def test_device_page_cursor_is_signed_scoped_and_uses_snapshot_order(env):
    admin, path, value = device(env)
    _, _, second = device(env, "SYNTHETIC second device")
    base = path.rsplit("/", 1)[0]
    first = expect(admin.request("GET", base, params={"limit": 1}), 200)
    assert len(first["items"]) == 1 and first["next_cursor"]
    page = expect(
        admin.request("GET", base, params={"limit": 1, "cursor": first["next_cursor"]}), 200
    )
    assert {page["items"][0]["id"], first["items"][0]["id"]} == {value["id"], second["id"]}
    assert page["next_cursor"] is None
    expect(
        admin.request("GET", base, params={"cursor": first["next_cursor"], "environment": "FIELD"}),
        422,
    )
    expect(admin.request("GET", base, params={"cursor": "untrusted"}), 422)


def test_device_csrf_origin_recent_auth_and_key_validation(env):
    admin, path, value = device(env)
    bind(env, value)
    endpoint = path + "/credentials"
    for headers in (
        {"X-CSRF-Token": "INVALID", "Idempotency-Key": str(uuid4())},
        {"Origin": "https://foreign.example.invalid", "Idempotency-Key": str(uuid4())},
    ):
        expect(admin.request("POST", endpoint, json=issue_body(), headers=headers), 403)
    expect(admin.request("POST", endpoint, json=issue_body()), 400)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE sessions SET reauthenticated_at=now()-interval '11 minutes' WHERE user_id=(SELECT user_id FROM organization_memberships WHERE id=:m)",
            m=env["admin"]["id"],
        )
    assert expect(mutate(admin, endpoint, issue_body()), 403)["error"]["code"] == "REAUTHENTICATE"


def test_device_runtime_rls_cannot_approve_binding_cross_utility_or_read_credentials_as_engineer(
    env,
):
    from hydro.db import context

    admin, path, value = device(env)
    bind(env, value)
    expect(mutate(admin, path + "/credentials", issue_body()), 201)
    engineer, member = provision(env, "ENGINEER", "device-rls-engineer@example.invalid")
    with env["owner"].begin() as c:
        user = one(c, "SELECT user_id FROM organization_memberships WHERE id=:i", i=member["id"])[
            "user_id"
        ]
    with env["app"].state.engine.begin() as c:
        context(c, user, env["org"]["id"])
        assert one(c, "SELECT count(*) AS n FROM devices")["n"] == 1
        assert one(c, "SELECT count(*) AS n FROM device_credentials")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM device_provisioning_bindings")["n"] == 0
    with pytest.raises(DBAPIError), env["app"].state.engine.begin() as c:
        context(c, user, env["org"]["id"])
        execute(
            c,
            "INSERT INTO device_provisioning_bindings(organization_id,device_id,environment,review_reference,classification) VALUES(:o,:d,'LABORATORY','SYNTHETIC unauthorized approval','SYNTHETIC_TEST_ONLY')",
            o=env["org"]["id"],
            d=value["id"],
        )
    with env["app"].state.engine.begin() as c:
        context(c, user, env["other"]["id"])
        assert one(c, "SELECT count(*) AS n FROM devices")["n"] == 0


def test_device_database_preserves_profile_history_and_permanent_revocation(env):
    admin, path, value = device(env)
    bind(env, value)
    issued = expect(mutate(admin, path + "/credentials", issue_body()), 201)
    expect(mutate(admin, path + "/credentials/" + issued["id"], None, method="DELETE"), 200)
    for statement, identifier in (
        ("UPDATE devices SET origin_profile='FIELD' WHERE id=:i", value["id"]),
        ("UPDATE device_credentials SET revoked_at=NULL WHERE id=:i", issued["id"]),
        ("DELETE FROM device_provisioning_bindings WHERE device_id=:i", value["id"]),
    ):
        with pytest.raises(DBAPIError), env["owner"].begin() as c:
            execute(c, statement, i=identifier)


def test_device_populated_downgrade_refuses_to_erase_records(env):
    from alembic import command
    from alembic.config import Config

    from hydro.config import ROOT

    device(env)
    cfg = Config(str(ROOT / "services/api/alembic.ini"))
    cfg.attributes["connection"] = env["owner"].connect()
    try:
        with pytest.raises(RuntimeError, match="non-destructive downgrade refused"):
            command.downgrade(cfg, "pre_m10_003")
    finally:
        cfg.attributes["connection"].close()
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_004"
        assert one(c, "SELECT count(*) AS n FROM devices")["n"] == 1


def test_device_concurrent_same_key_issues_at_most_one_secret(env):
    from concurrent.futures import ThreadPoolExecutor

    admin, path, value = device(env)
    bind(env, value)
    second = login(env, "admin-a@example.invalid")
    body, key = issue_body(), uuid4()
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda client: mutate(client, path + "/credentials", body, key=key), [admin, second]
            )
        )
    assert sorted(r.status_code for r in responses) == [201, 409]
    assert sum("one_time_secret" in r.json() for r in responses) == 1
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM device_credentials")["n"] == 1
        assert (
            one(c, "SELECT count(*) AS n FROM audit_logs WHERE resource_type='device_credentials'")[
                "n"
            ]
            == 1
        )


def test_device_fault_before_audit_rolls_back_secret_verifier_and_receipt(env, monkeypatch):
    import hydro.device_credentials as module

    admin, path, value = device(env)
    bind(env, value)

    def interrupted(*args, **kwargs):
        raise RuntimeError("SYNTHETIC failure before commit")

    with monkeypatch.context() as scoped:
        scoped.setattr(module, "record", interrupted)
        with pytest.raises(RuntimeError, match="SYNTHETIC failure before commit"):
            mutate(admin, path + "/credentials", issue_body())
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM device_credentials")["n"] == 0
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM idempotency_records WHERE route_template LIKE '%/credentials'",
            )["n"]
            == 0
        )


def test_device_empty_migration_round_trip_is_executed_without_erasing_rows(env):
    from alembic import command
    from alembic.config import Config

    from hydro.config import ROOT

    # The approved Alembic environment opens its own connection. Release read
    # locks before invoking DDL; never hold a separate transaction across it.
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM devices")["n"] == 0
    cfg = Config(str(ROOT / "services/api/alembic.ini"))
    command.downgrade(cfg, "pre_m10_003")
    with env["owner"].begin() as c:
        assert one(c, "SELECT to_regclass('public.devices') AS name")["name"] is None
    command.upgrade(cfg, "head")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_004"
    admin, path, _ = device(env)
    expect(admin.request("GET", path), 200)
