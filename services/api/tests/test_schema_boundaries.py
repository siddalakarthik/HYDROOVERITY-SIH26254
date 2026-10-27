import json
import re
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from helpers import expect, login, mutate, provision, register, token

from hydro.config import ROOT
from hydro.contracts import INVENTORY, OPERATIONS, runtime_openapi
from hydro.db import execute, one, query
from hydro.repository import TABLES


def test_live_selected_columns_and_tenant_foreign_keys_match_m02_catalogue(env):
    catalogue = json.loads((ROOT / "data/schemas/m02-database-design.json").read_text())
    with env["owner"].begin() as c:
        actual = query(
            c,
            "SELECT t.relname AS table_name,a.attname AS name,format_type(a.atttypid,a.atttypmod) AS type,a.attnotnull AS required FROM pg_attribute a JOIN pg_class t ON t.oid=a.attrelid JOIN pg_namespace n ON n.oid=t.relnamespace WHERE n.nspname='public' AND a.attnum>0 AND NOT a.attisdropped",
        )
        columns = {(r["table_name"], r["name"]): r for r in actual}
        definitions = query(
            c,
            "SELECT t.relname AS table_name,pg_get_constraintdef(k.oid) AS definition FROM pg_constraint k JOIN pg_class t ON t.oid=k.conrelid JOIN pg_namespace n ON n.oid=t.relnamespace WHERE n.nspname='public'",
        )
        for table in catalogue["tables"]:
            if table["name"] not in TABLES:
                continue
            for field in table["columns"]:
                current = columns[(table["name"], field["name"])]
                expected = field["type"]
                if expected in catalogue["enums"]:
                    expected = "text"
                if expected == "timestamptz":
                    expected = "timestamp with time zone"
                assert current["type"].lower() == expected.lower()
                if not field["nullable"]:
                    assert current["required"]
            for fk in table["foreign_keys"]:
                if fk["target"] not in TABLES:
                    assert any(
                        r["table_name"] == table["name"]
                        and fk["column"] + "ISNULL" in re.sub(r"[\s()]", "", r["definition"])
                        for r in definitions
                    )
                elif fk["same_tenant"]:
                    expected = (
                        "FOREIGNKEY(organization_id,"
                        + fk["column"]
                        + ")REFERENCES"
                        + fk["target"]
                        + "(organization_id,id)"
                    )
                    assert any(
                        r["table_name"] == table["name"]
                        and expected in r["definition"].replace(" ", "")
                        for r in definitions
                    )
        assert len(TABLES) == 30


def test_concurrent_registration_has_one_identity_and_citizen_grant(env):
    a = env["client"]()
    b = env["client"]()
    body = {
        "utility_slug": "synthetic-utility-a",
        "email": "race@example.invalid",
        "display_name": "SYNTHETIC concurrent resident",
        "password": env["password"],
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: client.request("POST", "/api/v1/auth/register", json=body), [a, b]
            )
        )
    for result in results:
        expect(result, 200)
    with env["owner"].begin() as c:
        assert (
            one(c, "SELECT count(*) AS n FROM users WHERE email_normalized='race@example.invalid'")[
                "n"
            ]
            == 1
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM role_assignments a JOIN organization_memberships m ON m.id=a.membership_id JOIN users u ON u.id=m.user_id WHERE u.email_normalized='race@example.invalid'",
            )["n"]
            == 1
        )


def test_expired_tokens_and_revoked_pending_grants_cannot_reactivate_roles(env):
    admin = login(env, "admin-a@example.invalid")
    tech, member = provision(env, "TECHNICIAN", "tech@example.invalid", admin)
    base = f"/api/v1/orgs/{env['org']['id']}"
    expect(
        mutate(admin, base + "/invitations", {"email": "tech@example.invalid", "role": "ENGINEER"}),
        200,
    )
    outstanding = token(env, "INVITATION", "tech@example.invalid")
    directory = expect(admin.request("GET", base + "/memberships"), 200)["items"]
    current = next(x for x in directory if x["id"] == member["id"])
    expect(
        mutate(
            admin,
            base + "/memberships/" + member["id"] + "/roles",
            {
                "roles": ["CITIZEN"],
                "reason": "SYNTHETIC security revocation also invalidates pending grants",
            },
            version=current["version"],
            method="PUT",
        ),
        200,
    )
    login(env, "tech@example.invalid", tech)
    expect(tech.request("POST", "/api/v1/auth/invitation-accept", json={"token": outstanding}), 422)
    pending = register(env, "pending@example.invalid", False)
    value = token(env, "VERIFY", "pending@example.invalid")
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE account_recovery_tokens SET expires_at=now()-interval '1 second' WHERE user_id=(SELECT id FROM users WHERE email_normalized='pending@example.invalid')",
        )
    expect(pending.request("POST", "/api/v1/auth/verify", json={"token": value}), 422)


def test_deferred_routes_remain_unregistered_and_runtime_schema_is_precise(env):
    client = login(env, "admin-a@example.invalid")
    from hydro.communications_contracts import OPERATIONS as communications
    from hydro.device_credentials import OPERATIONS as devices
    from hydro.project_contact import OPERATIONS as contact
    from hydro.realtime import OPERATIONS as realtime

    registered = {op["id"] for op in OPERATIONS + communications + contact + realtime + devices}
    for op in INVENTORY:
        if op["id"] in registered:
            continue
        path = re.sub(r"\{[^}]+\}", str(uuid4()), op["path"])
        response = client.raw(op["method"].upper(), "/api/v1" + path)
        assert response.status_code in {404, 405}, "A deferred operation was reachable"
    # Contact is a newly registered gated protocol, not an unregistered route.
    expect(client.raw("POST", "/api/v1/public/contact"), 403)
    response = client.request(
        "POST",
        "/api/v1/public/contact",
        json={"category": "QUESTION", "message": "SYNTHETIC default-disabled contact boundary"},
    )
    assert expect(response, 503)["error"]["code"] == "PROJECT_CONTACT_DISABLED"
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 0
    runtime = runtime_openapi()
    assert sum(len(x) for x in runtime["paths"].values()) == 119
    assert "EvaluationResult" not in runtime["components"]["schemas"]
    assert "deviceBearer" not in runtime["components"]["securitySchemes"]


def test_nul_text_rejected_without_changing_password_rules(env):
    client = env["client"]()
    body = {
        "utility_slug": "synthetic-utility-a",
        "email": "nul@example.invalid",
        "display_name": "SYNTHETIC\x00name",
        "password": env["password"],
    }
    expect(client.request("POST", "/api/v1/auth/register", json=body), 422)
    with env["owner"].begin() as c:
        assert one(c, "SELECT id FROM users WHERE email_normalized='nul@example.invalid'") is None
