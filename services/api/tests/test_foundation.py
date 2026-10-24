import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from hydro.db import context, one, principal_is_safe
from hydro.repository import insert


def test_actual_postgres_postgis_and_readiness(env):
    with env["app"].state.engine.begin() as c:
        assert principal_is_safe(c)
        assert int(one(c, "SHOW server_version_num")["server_version_num"]) >= 170000
        assert one(c, "SELECT postgis_version() AS version")["version"].startswith("3.")
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "m07_b_004"
    client = env["client"]()
    assert client.request("GET", "/internal/health/live").status_code == 200
    assert client.request("GET", "/internal/health/ready").status_code == 200


def test_rls_blocks_cross_tenant_and_pool_context_clears(env):
    engine = env["app"].state.engine
    with engine.begin() as c:
        context(c, organization_id=env["org"]["id"])
        rows = c.execute(text("SELECT organization_id FROM organization_memberships")).all()
        assert rows and all(r[0] == env["org"]["id"] for r in rows)
        assert (
            one(
                c,
                "SELECT id FROM organization_memberships WHERE organization_id=:o",
                o=env["other"]["id"],
            )
            is None
        )
    with engine.begin() as c:
        assert not c.execute(text("SELECT id FROM organization_memberships")).all()
    with pytest.raises(DBAPIError):
        with engine.begin() as c:
            context(c, organization_id=env["org"]["id"])
            insert(
                c,
                "water_zones",
                organization_id=env["other"]["id"],
                name="Must fail",
                demand_boundary_version="synthetic-v1",
                demand_accounting={},
                topology_quality="UNVERIFIED",
            )


def test_same_tenant_fk_and_immutable_history(env):
    with pytest.raises(DBAPIError):
        with env["owner"].begin() as c:
            insert(
                c,
                "role_assignments",
                organization_id=env["org"]["id"],
                membership_id=env["other_admin"]["id"],
                role_id=one(c, "SELECT id FROM roles WHERE code='TECHNICIAN'")["id"],
                granted_by_id=env["admin"]["id"],
            )
    with pytest.raises(DBAPIError):
        with env["app"].state.engine.begin() as c:
            context(c, organization_id=env["org"]["id"])
            c.exec_driver_sql("UPDATE audit_logs SET action='forbidden'")


def test_preauth_cookie_csrf_and_anonymous_denial(env):
    client = env["client"]()
    r = client.request("GET", "/api/v1/auth/csrf")
    assert r.status_code == 200
    cookie = r.headers["set-cookie"].lower()
    assert "__host-hydro_session=" in cookie
    assert (
        "secure" in cookie
        and "httponly" in cookie
        and "samesite=lax" in cookie
        and "path=/" in cookie
    )
    assert "domain=" not in cookie and r.headers["cache-control"] == "no-store"
    assert (
        client.raw(
            "POST",
            "/api/v1/auth/login",
            json={"email": "admin-a@example.invalid", "password": env["password"]},
        ).status_code
        == 403
    )
    assert client.request("GET", "/api/v1/me").status_code == 401


def test_real_login_and_admin_no_engineer_inheritance(env):
    client = env["client"]()
    r = client.request(
        "POST",
        "/api/v1/auth/login",
        json={"email": "admin-a@example.invalid", "password": env["password"]},
    )
    assert r.status_code == 200, "Real login failed"
    assert r.json()["verified"] is True
    assert client.request("GET", "/api/v1/me").status_code == 200
    assert client.request("GET", f"/api/v1/orgs/{env['org']['id']}/zones").status_code == 403
    assert client.request("GET", f"/api/v1/orgs/{env['other']['id']}").status_code == 404


def test_operator_bootstrap_repeat_never_overwrites_existing_credentials(env):
    from hydro.cli import bootstrap

    with env["owner"].begin() as c:
        before = one(
            c, "SELECT password_hash FROM users WHERE email_normalized='admin-a@example.invalid'"
        )["password_hash"]
        org, member, created = bootstrap(
            c,
            confirmed_database=__import__("os").environ["HYDRO_TEST_DATABASE_CONFIRM"],
            slug="synthetic-utility-a",
            name="SYNTHETIC integration utility A",
            email="admin-a@example.invalid",
            display_name="A repeated synthetic request",
            password="a-different-synthetic-bootstrap-secret",
            reporting_enabled=True,
        )
        assert (
            created is False
            and org["id"] == env["org"]["id"]
            and member["id"] == env["admin"]["id"]
        )
        after = one(
            c, "SELECT password_hash FROM users WHERE email_normalized='admin-a@example.invalid'"
        )["password_hash"]
        if before != after:
            raise AssertionError("Bootstrap changed an existing credential")
        assert (
            one(c, "SELECT count(*) AS n FROM audit_logs WHERE resource_id=:i", i=org["id"])["n"]
            == 1
        )
