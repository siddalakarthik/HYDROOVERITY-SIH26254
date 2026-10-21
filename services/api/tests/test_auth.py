from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from helpers import expect, login, register, token

from hydro.db import execute, one
from hydro.security import COOKIE, verifier


def test_registration_generic_duplicate_no_credential_or_membership_change(env):
    email = "citizen@example.invalid"
    client = register(env, email, False)
    original = token(env, "VERIFY", email)
    with env["owner"].begin() as c:
        before = one(c, "SELECT password_hash FROM users WHERE email_normalized=:e", e=email)[
            "password_hash"
        ]
    response = client.request(
        "POST",
        "/api/v1/auth/register",
        json={
            "utility_slug": env["other"]["public_slug"],
            "email": " CITIZEN@example.invalid ".strip(),
            "display_name": "Another name",
            "password": "another-long-secret-for-synthetic-case",
        },
    )
    expect(response, 200)
    with env["owner"].begin() as c:
        assert (
            one(c, "SELECT password_hash FROM users WHERE email_normalized=:e", e=email)[
                "password_hash"
            ]
            == before
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM organization_memberships WHERE user_id=(SELECT id FROM users WHERE email_normalized=:e)",
                e=email,
            )["n"]
            == 1
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM account_recovery_tokens WHERE purpose='VERIFY' AND used_at IS NULL",
            )["n"]
            == 1
        )
    assert token(env, "VERIFY", email) == original
    expect(
        client.request(
            "POST", "/api/v1/auth/login", json={"email": email, "password": env["password"]}
        ),
        401,
    )
    expect(client.request("POST", "/api/v1/auth/verify", json={"token": original}), 200)
    expect(client.request("POST", "/api/v1/auth/verify", json={"token": original}), 422)
    expect(client.request("GET", "/api/v1/me"), 401)
    login(env, email, client)


def test_registration_unknown_fields_and_no_staff_self_grant(env):
    client = env["client"]()
    request = {
        "utility_slug": "synthetic-utility-a",
        "email": "x@example.invalid",
        "display_name": "Synthetic",
        "password": env["password"],
        "role": "ADMIN",
    }
    expect(client.request("POST", "/api/v1/auth/register", json=request), 422)
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM users")["n"] == 2


def test_origin_csrf_idempotency_and_no_store(env):
    client = env["client"]()
    csrf = expect(client.request("GET", "/api/v1/auth/csrf"), 200)["csrf_token"]
    b = {"email": "admin-a@example.invalid", "password": env["password"]}
    for headers in [
        {},
        {"Origin": "https://evil.invalid", "X-CSRF-Token": csrf},
        {"Origin": client.origin, "X-CSRF-Token": "wrong"},
        {"Origin": client.origin, "X-CSRF-Token": csrf, "Sec-Fetch-Site": "cross-site"},
    ]:
        r = client.raw("POST", "/api/v1/auth/login", json=b, headers=headers)
        expect(r, 403)
        assert r.headers["cache-control"] == "no-store"
    r = client.request(
        "POST", "/api/v1/auth/login", json=b, headers={"Idempotency-Key": str(uuid4())}
    )
    expect(r, 400)
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM idempotency_records")["n"] == 0


def test_login_rotates_and_logout_cleanup_is_monotonic(env):
    client = env["client"]()
    expect(client.request("GET", "/api/v1/auth/csrf"), 200)
    old_cookie = client.http.cookies.get(COOKIE)
    login(env, "admin-a@example.invalid", client)
    assert client.http.cookies.get(COOKIE) != old_cookie
    expect(client.raw("GET", "/api/v1/me", headers={"Cookie": COOKIE + "=" + old_cookie}), 401)
    csrf = expect(client.request("GET", "/api/v1/auth/csrf"), 200)["csrf_token"]
    raw = client.http.cookies.get(COOKIE)
    h = {"Cookie": COOKIE + "=" + raw, "Origin": client.origin, "X-CSRF-Token": csrf}
    expect(client.raw("POST", "/api/v1/auth/logout", headers=h), 200)
    expect(client.raw("GET", "/api/v1/me", headers={"Cookie": COOKIE + "=" + raw}), 401)
    expect(client.raw("POST", "/api/v1/auth/logout", headers=h), 200)
    expect(client.raw("POST", "/api/v1/auth/logout", headers={**h, "X-CSRF-Token": "wrong"}), 403)
    expect(
        client.raw("POST", "/api/v1/auth/logout", headers={**h, "Cookie": COOKIE + "=unknown"}), 401
    )
    expect(client.request("POST", "/api/v1/auth/logout"), 200)


def test_recovery_cooldown_replaces_old_token_and_reset_is_single_use(env):
    client = login(env, "admin-a@example.invalid")
    other = env["client"]()
    known = expect(
        other.request("POST", "/api/v1/auth/recovery", json={"email": "admin-a@example.invalid"}),
        202,
    )
    original = token(env, "RESET", "admin-a@example.invalid")
    unknown = expect(
        other.request("POST", "/api/v1/auth/recovery", json={"email": "unknown@example.invalid"}),
        202,
    )
    assert known == unknown
    expect(
        other.request("POST", "/api/v1/auth/recovery", json={"email": "admin-a@example.invalid"}),
        202,
    )
    assert token(env, "RESET", "admin-a@example.invalid") == original
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE account_recovery_tokens SET created_at=now()-interval '61 seconds' WHERE purpose='RESET'",
        )
    expect(
        other.request("POST", "/api/v1/auth/recovery", json={"email": "admin-a@example.invalid"}),
        202,
    )
    replacement = token(env, "RESET", "admin-a@example.invalid")
    assert replacement != original
    b = {"token": original, "new_password": "synthetic-replacement-password-only"}
    expect(other.request("POST", "/api/v1/auth/reset", json=b), 422)
    b["token"] = replacement
    expect(other.request("POST", "/api/v1/auth/reset", json=b), 200)
    expect(other.request("POST", "/api/v1/auth/reset", json=b), 422)
    expect(other.request("GET", "/api/v1/me"), 401)
    expect(client.request("GET", "/api/v1/me"), 401)
    expect(
        other.request(
            "POST",
            "/api/v1/auth/login",
            json={"email": "admin-a@example.invalid", "password": env["password"]},
        ),
        401,
    )
    expect(
        other.request(
            "POST",
            "/api/v1/auth/login",
            json={"email": "admin-a@example.invalid", "password": b["new_password"]},
        ),
        200,
    )


def test_concurrent_reset_consumes_once(env):
    first = env["client"]()
    second = env["client"]()
    expect(
        first.request("POST", "/api/v1/auth/recovery", json={"email": "admin-a@example.invalid"}),
        202,
    )
    b = {
        "token": token(env, "RESET", "admin-a@example.invalid"),
        "new_password": "synthetic-concurrent-new-password",
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(
            pool.map(
                lambda client: client.request("POST", "/api/v1/auth/reset", json=b).status_code,
                [first, second],
            )
        )
    assert sorted(statuses) == [200, 422]


def test_reset_login_race_never_leaves_old_password_session(env):
    recover = env["client"]()
    old_login = env["client"]()
    expect(
        recover.request("POST", "/api/v1/auth/recovery", json={"email": "admin-a@example.invalid"}),
        202,
    )
    b = {
        "token": token(env, "RESET", "admin-a@example.invalid"),
        "new_password": "synthetic-race-replacement-password",
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        reset = pool.submit(recover.request, "POST", "/api/v1/auth/reset", json=b)
        issue = pool.submit(
            old_login.request,
            "POST",
            "/api/v1/auth/login",
            json={"email": "admin-a@example.invalid", "password": env["password"]},
        )
        expect(reset.result(), 200)
        assert issue.result().status_code in {200, 401}
    expect(old_login.request("GET", "/api/v1/me"), 401)
    # Both legal race outcomes must end with the new credential usable. This
    # also makes positive login evidence independent of which request won.
    expect(
        old_login.request(
            "POST",
            "/api/v1/auth/login",
            json={"email": "admin-a@example.invalid", "password": b["new_password"]},
        ),
        200,
    )


@pytest.mark.parametrize("expiry", ["idle", "absolute", "revoked"])
def test_session_expiry_and_recognized_cleanup(env, expiry):
    client = login(env, "admin-a@example.invalid")
    csrf = expect(client.request("GET", "/api/v1/auth/csrf"), 200)["csrf_token"]
    raw = client.http.cookies.get(COOKIE)
    with env["owner"].begin() as c:
        assignments = {
            "idle": "idle_expires_at=now()-interval '1 second'",
            "absolute": "idle_expires_at=now()-interval '1 second',absolute_expires_at=now()-interval '1 second'",
            "revoked": "revoked_at=now()",
        }
        execute(
            c,
            "UPDATE sessions SET " + assignments[expiry] + " WHERE token_hash=:h",
            h=verifier(raw),
        )
    expect(client.raw("GET", "/api/v1/me"), 401)
    expect(
        client.raw(
            "POST", "/api/v1/auth/logout", headers={"Origin": client.origin, "X-CSRF-Token": csrf}
        ),
        200,
    )


def test_rate_limits_are_bounded_hmac_and_failures_count(env):
    client = env["client"]()
    b = {"email": "admin-a@example.invalid", "password": "wrong synthetic credential"}
    for _ in range(5):
        expect(client.request("POST", "/api/v1/auth/login", json=b), 401)
    r = client.request("POST", "/api/v1/auth/login", json=b)
    expect(r, 429)
    assert r.headers["retry-after"] == "60"
    assert all(len(k) == 64 and "@" not in k for k in env["app"].state.limits.buckets)


def test_profile_etag_self_revoke_and_global_retry_exceptions(env):
    client = login(env, "admin-a@example.invalid")
    profile = client.request("GET", "/api/v1/me")
    expect(profile, 200)
    b = {"display_name": "Synthetic updated operator"}
    expect(client.request("PATCH", "/api/v1/me", json=b), 428)
    expect(client.request("PATCH", "/api/v1/me", json=b, headers={"If-Match": '"999"'}), 412)
    expect(
        client.request(
            "PATCH",
            "/api/v1/me",
            json=b,
            headers={"If-Match": profile.headers["etag"], "Idempotency-Key": str(uuid4())},
        ),
        400,
    )
    expect(
        client.request(
            "PATCH", "/api/v1/me", json=b, headers={"If-Match": profile.headers["etag"]}
        ),
        200,
    )
    sessions = expect(client.request("GET", "/api/v1/me/sessions"), 200)["items"]
    expect(client.request("DELETE", "/api/v1/me/sessions/" + sessions[0]["id"]), 200)
    expect(client.request("GET", "/api/v1/me"), 401)


def test_private_delivery_failure_remains_generic_and_retry_uses_new_verifier(env, tmp_path):
    from hydro.security import PrivateMail

    broken = tmp_path / "not-a-directory"
    broken.write_text("Synthetic filesystem failure fixture")
    env["app"].state.mail = PrivateMail(broken)
    client = register(env, "delivery@example.invalid", False)
    with env["owner"].begin() as c:
        before = one(
            c,
            "SELECT token_hash FROM account_recovery_tokens WHERE user_id=(SELECT id FROM users WHERE email_normalized='delivery@example.invalid')",
        )["token_hash"]
        execute(
            c,
            "UPDATE account_recovery_tokens SET created_at=now()-interval '61 seconds' WHERE user_id=(SELECT id FROM users WHERE email_normalized='delivery@example.invalid')",
        )
    env["app"].state.mail = PrivateMail(env["settings"].mail_directory)
    register(env, "delivery@example.invalid", False)
    with env["owner"].begin() as c:
        after = one(
            c,
            "SELECT token_hash FROM account_recovery_tokens WHERE user_id=(SELECT id FROM users WHERE email_normalized='delivery@example.invalid') AND used_at IS NULL",
        )["token_hash"]
        if bytes(before) == bytes(after):
            raise AssertionError("Failed delivery verifier was reused")
    expect(
        client.request(
            "POST",
            "/api/v1/auth/verify",
            json={"token": token(env, "VERIFY", "delivery@example.invalid")},
        ),
        200,
    )
