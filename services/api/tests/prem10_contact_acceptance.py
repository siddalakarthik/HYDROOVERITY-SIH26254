"""Synthetic-policy-only project inbox acceptance; no real legal policy approved."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from helpers import expect
from sqlalchemy.exc import DBAPIError, OperationalError

from hydro.contact_policy import ContactTestPolicy
from hydro.db import execute, one
from hydro.errors import Problem
from hydro.project_contact import mark_reviewed, purge_synthetic_policy, review_inbox, set_hold

PATH = "/api/v1/public/contact"
BODY = {
    "category": "QUESTION",
    "message": "SYNTHETIC project enquiry <script>alert('inert')</script>",
    "reply_email": "Synthetic.Project@Example.Invalid",
}


@pytest.fixture
def contact_env(env):
    with env["owner"].begin() as c:
        assert one(c, "SELECT current_database() AS name")["name"].startswith("hydro_disposable_")
        c.exec_driver_sql("TRUNCATE project_contact_submissions,project_contact_operator_audit")
    return env


def enabled(env, capacity=5):
    policy = ContactTestPolicy(
        provenance="SYNTHETIC_TEST_POLICY_ONLY",
        operator_reference="SYNTHETIC-OPERATOR-NOT-A-LIVE-ENROLLMENT",
        policy_reference="SYNTHETIC-30-DAY-TEST-NOT-LEGAL-APPROVAL",
        retention_days=30,
        capacity=capacity,
    )
    env["app"].state.settings.contact_test_policy = policy
    return policy


def test_contact_default_disabled_and_rejects_unapproved_policy(contact_env):
    env = contact_env
    response = env["client"]().request("POST", PATH, json=BODY)
    assert expect(response, 503)["error"]["code"] == "PROJECT_CONTACT_DISABLED"
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 0
    with pytest.raises(ValueError):
        ContactTestPolicy(
            provenance="APPROVED_PRODUCTION_POLICY",
            operator_reference="SYNTHETIC-OPERATOR",
            policy_reference="SYNTHETIC-NOT-APPROVAL",
            retention_days=30,
            capacity=5,
        )


def test_contact_actual_persistence_fixed_owner_and_escaped_operator_review(contact_env):
    env = contact_env
    policy = enabled(env)
    client = env["client"]()
    accepted = expect(client.request("POST", PATH, json=BODY), 202)
    assert accepted == {"message": "Your project message has been accepted for review."}
    with env["owner"].begin() as c:
        row = one(c, "SELECT * FROM project_contact_submissions")
        assert row["reply_email"] == "synthetic.project@example.invalid"
        assert row["status"] == "NEW" and row["version"] == 1
        assert (row["expires_at"] - row["created_at"]).total_seconds() == 30 * 86400
        assert not any(key in row for key in ("organization_id", "user_id", "session_id", "ip"))
        assert one(c, "SELECT count(*) AS n FROM citizen_complaints")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM service_requests")["n"] == 0
        rows = review_inbox(c, policy)
        assert len(rows) == 1 and "&lt;script&gt;" in rows[0]["message"]
        assert "<script>" not in rows[0]["message"]
        audit = one(c, "SELECT * FROM project_contact_operator_audit")
        assert audit["action"] == "READ" and audit["contact_id"] == row["id"]
    with env["app"].state.engine.begin() as c:
        assert (
            one(c, "SELECT count(capacity_marker) AS n FROM project_contact_submissions")["n"] == 1
        )
    for sql in (
        "SELECT id FROM project_contact_submissions",
        "SELECT message,reply_email FROM project_contact_submissions",
        "SELECT * FROM project_contact_operator_audit",
    ):
        with pytest.raises(DBAPIError), env["app"].state.engine.begin() as c:
            c.exec_driver_sql(sql)


def test_contact_csrf_origin_idempotency_and_no_public_inbox(contact_env):
    env = contact_env
    enabled(env)
    client = env["client"]()
    csrf = expect(client.request("GET", "/api/v1/auth/csrf"), 200)["csrf_token"]
    for headers in (
        {"Origin": "https://unrelated.invalid", "X-CSRF-Token": csrf},
        {"Origin": env["settings"].origin, "X-CSRF-Token": "incorrect"},
        {"X-CSRF-Token": csrf},
    ):
        expect(client.raw("POST", PATH, json=BODY, headers=headers), 403)
    expect(client.request("POST", PATH, json=BODY, headers={"Idempotency-Key": str(uuid4())}), 400)
    expect(client.request("GET", PATH), 405)
    expect(client.request("GET", PATH + "/" + str(uuid4())), 404)
    with env["owner"].begin() as c:
        execute(c, "UPDATE sessions SET revoked_at=now()")
    expect(
        client.raw(
            "POST",
            PATH,
            json=BODY,
            headers={"Origin": env["settings"].origin, "X-CSRF-Token": csrf},
        ),
        401,
    )
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 0


@pytest.mark.parametrize(
    "extra",
    [
        {"organization_id": str(uuid4())},
        {"owner_id": str(uuid4())},
        {"attachment_ids": []},
        {"reply_email": "injected\r\nheader@example.invalid"},
        {"message": "SYNTHETIC\x00invalid input"},
    ],
)
def test_contact_rejects_routing_and_unsafe_inputs(contact_env, extra):
    enabled(contact_env)
    expect(contact_env["client"]().request("POST", PATH, json={**BODY, **extra}), 422)


def test_contact_8kib_body_cap_and_bounded_lost_response_duplicate(contact_env):
    env = contact_env
    enabled(env)
    client = env["client"]()
    expect(client.request("POST", PATH, json={**BODY, "message": "x" * 9000}), 413)
    first = expect(client.request("POST", PATH, json=BODY), 202)
    assert expect(client.request("POST", PATH, json=BODY), 202) == first
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 2
        assert one(c, "SELECT count(*) AS n FROM idempotency_records")["n"] == 0


def test_contact_session_and_normalized_email_limits_use_only_hmac_keys(contact_env):
    env = contact_env
    enabled(env, 100)
    client = env["client"]()
    for _ in range(3):
        expect(
            client.request(
                "POST", PATH, json={k: v for k, v in BODY.items() if k != "reply_email"}
            ),
            202,
        )
    expect(client.request("POST", PATH, json=BODY), 429)
    for n in range(5):
        email = BODY["reply_email"].upper() if n % 2 else BODY["reply_email"].lower()
        expect(env["client"]().request("POST", PATH, json={**BODY, "reply_email": email}), 202)
    expect(env["client"]().request("POST", PATH, json=BODY), 429)
    assert all(
        len(key) == 64 and all(ch in "0123456789abcdef" for ch in key)
        for key in env["app"].state.limits.buckets
    )


def test_contact_capacity_is_atomic_across_sessions(contact_env):
    env = contact_env
    enabled(env, 1)
    clients = [env["client"](), env["client"]()]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda client: client.request("POST", PATH, json=BODY), clients))
    assert sorted(r.status_code for r in results) == [202, 503]
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 1


def test_contact_insert_fault_rolls_back_and_never_returns_accepted(
    contact_env, monkeypatch, caplog
):
    env = contact_env
    enabled(env)
    import hydro.project_contact as module

    original = module.execute

    def fail(c, sql, **values):
        original(c, sql, **values)
        if sql.startswith("INSERT INTO project_contact_submissions"):
            raise OperationalError(
                "SYNTHETIC injected post-insert failure", {}, Exception("SYNTHETIC")
            )

    with monkeypatch.context() as patch:
        patch.setattr(module, "execute", fail)
        expect(env["client"]().request("POST", PATH, json=BODY), 503)
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 0
    assert BODY["message"] not in caplog.text and BODY["reply_email"] not in caplog.text


def test_contact_owner_review_version_hold_and_synthetic_purge(contact_env):
    env = contact_env
    policy = enabled(env)
    expect(env["client"]().request("POST", PATH, json=BODY), 202)
    with env["owner"].begin() as c:
        row = one(c, "SELECT * FROM project_contact_submissions")
        mark_reviewed(c, policy, row["id"], 1)
        set_hold(c, policy, row["id"], 2, "SYNTHETIC-HOLD-NOT-LEGAL-INSTRUCTION")
        execute(
            c,
            "UPDATE project_contact_submissions SET created_at=now()-interval '31 days',expires_at=now()-interval '24 hours' WHERE id=:i",
            i=row["id"],
        )
        assert purge_synthetic_policy(c, policy) == 0
        set_hold(c, policy, row["id"], 3, None)
        assert purge_synthetic_policy(c, policy) == 1
        assert one(c, "SELECT count(*) AS n FROM project_contact_submissions")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM project_contact_operator_audit")["n"] == 4
    with pytest.raises(Problem), env["owner"].begin() as c:
        mark_reviewed(c, policy, row["id"], 1)
    with pytest.raises(Problem), env["app"].state.engine.begin() as c:
        review_inbox(c, policy)
    with pytest.raises(DBAPIError), env["owner"].begin() as c:
        c.exec_driver_sql("DELETE FROM project_contact_operator_audit")
