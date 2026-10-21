"""Synthetic API scenario helpers; private tokens are never printed."""

import json
from uuid import uuid4


def expect(response, status):
    assert response.status_code == status, (
        f"Expected {status}, got {response.status_code}: {response.json().get('error', {}).get('code', 'unexpected response')}"
    )
    return response.json()


def token(env, purpose, email):
    files = sorted(
        env["settings"].mail_directory.glob("*.json"),
        key=lambda p: p.stat().st_mtime_ns,
        reverse=True,
    )
    for p in files:
        value = json.loads(p.read_text())
        if value["purpose"] == purpose and value["recipient"] == email:
            return value["token"]
    raise AssertionError("Expected private synthetic development delivery was not found")


def login(env, email, client=None):
    client = client or env["client"]()
    expect(
        client.request(
            "POST", "/api/v1/auth/login", json={"email": email, "password": env["password"]}
        ),
        200,
    )
    return client


def register(env, email, verify=True):
    client = env["client"]()
    expect(
        client.request(
            "POST",
            "/api/v1/auth/register",
            json={
                "utility_slug": env["org"]["public_slug"],
                "email": email,
                "display_name": "SYNTHETIC integration person",
                "password": env["password"],
            },
        ),
        200,
    )
    if verify:
        expect(
            client.request(
                "POST", "/api/v1/auth/verify", json={"token": token(env, "VERIFY", email)}
            ),
            200,
        )
    return client


def mutate(client, path, body, version=None, key=None, method="POST"):
    headers = {"Idempotency-Key": str(key or uuid4())}
    if version is not None:
        headers["If-Match"] = f'"{version}"'
    return client.request(method, path, json=body, headers=headers)


def provision(env, role, email, administrator=None):
    admin = administrator or login(env, "admin-a@example.invalid")
    client = register(env, email)
    login(env, email, client)
    expect(
        mutate(
            admin, f"/api/v1/orgs/{env['org']['id']}/invitations", {"email": email, "role": role}
        ),
        200,
    )
    expect(
        client.request(
            "POST",
            "/api/v1/auth/invitation-accept",
            json={"token": token(env, "INVITATION", email)},
        ),
        200,
    )
    login(env, email, client)
    membership = next(
        m
        for m in expect(client.request("GET", "/api/v1/me/memberships"), 200)["items"]
        if m["organization_id"] == str(env["org"]["id"])
    )
    return client, membership
