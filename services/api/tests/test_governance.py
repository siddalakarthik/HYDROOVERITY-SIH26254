from helpers import expect, login, mutate, provision, register, token

from hydro.db import execute, one


def directory(env, admin):
    return expect(admin.request("GET", f"/api/v1/orgs/{env['org']['id']}/memberships"), 200)[
        "items"
    ]


def test_invitation_verified_matching_identity_exact_role_and_replay(env):
    admin = login(env, "admin-a@example.invalid")
    target = "tech@example.invalid"
    invited = register(env, target)
    login(env, target, invited)
    expect(
        mutate(
            admin,
            f"/api/v1/orgs/{env['org']['id']}/invitations",
            {"email": target, "role": "TECHNICIAN"},
        ),
        200,
    )
    invitation = token(env, "INVITATION", target)
    wrong = register(env, "wrong@example.invalid")
    login(env, "wrong@example.invalid", wrong)
    expect(wrong.request("POST", "/api/v1/auth/invitation-accept", json={"token": invitation}), 422)
    expect(
        invited.request("POST", "/api/v1/auth/invitation-accept", json={"token": invitation}), 200
    )
    expect(invited.request("GET", "/api/v1/me"), 200)
    login(env, target, invited)
    expect(
        invited.request("POST", "/api/v1/auth/invitation-accept", json={"token": invitation}), 422
    )
    memberships = expect(invited.request("GET", "/api/v1/me/memberships"), 200)["items"]
    assert set(memberships[0]["roles"]) == {"CITIZEN", "TECHNICIAN"}
    assert len(directory(env, admin)) == 3


def test_invitation_no_existing_membership_required(env):
    admin = login(env, "admin-a@example.invalid")
    recipient = env["client"]()
    expect(
        recipient.request(
            "POST",
            "/api/v1/auth/register",
            json={
                "utility_slug": env["other"]["public_slug"],
                "email": "outsider@example.invalid",
                "display_name": "SYNTHETIC external identity",
                "password": env["password"],
            },
        ),
        200,
    )
    expect(
        recipient.request(
            "POST",
            "/api/v1/auth/verify",
            json={"token": token(env, "VERIFY", "outsider@example.invalid")},
        ),
        200,
    )
    login(env, "outsider@example.invalid", recipient)
    expect(
        mutate(
            admin,
            f"/api/v1/orgs/{env['org']['id']}/invitations",
            {"email": "outsider@example.invalid", "role": "SUPERVISOR"},
        ),
        200,
    )
    expect(
        recipient.request(
            "POST",
            "/api/v1/auth/invitation-accept",
            json={"token": token(env, "INVITATION", "outsider@example.invalid")},
        ),
        200,
    )
    login(env, "outsider@example.invalid", recipient)
    memberships = expect(recipient.request("GET", "/api/v1/me/memberships"), 200)["items"]
    assert len(memberships) == 2
    assert next(m for m in memberships if m["organization_id"] == str(env["org"]["id"]))[
        "roles"
    ] == ["SUPERVISOR"]


def test_last_admin_version_precondition_and_evaluator_denial(env):
    admin = login(env, "admin-a@example.invalid")
    item = directory(env, admin)[0]
    assert item["version"] == 1
    path = f"/api/v1/orgs/{env['org']['id']}/memberships/{env['admin']['id']}"
    expect(
        mutate(
            admin,
            path + "/roles",
            {"roles": ["CITIZEN"], "reason": "Synthetic removal must preserve last administrator"},
            version=1,
            method="PUT",
        ),
        409,
    )
    expect(
        mutate(
            admin,
            path + "/status",
            {
                "status": "SUSPENDED",
                "reason": "Synthetic attempted suspension of final administrator",
            },
            version=1,
        ),
        409,
    )
    expect(
        mutate(
            admin,
            path + "/roles",
            {
                "roles": ["ADMIN", "EVALUATOR"],
                "reason": "Synthetic evaluator escalation must be rejected",
            },
            version=1,
            method="PUT",
        ),
        422,
    )
    expect(
        mutate(
            admin,
            path + "/roles",
            {"roles": ["ADMIN"], "reason": "Synthetic stale version must be rejected"},
            version=99,
            method="PUT",
        ),
        412,
    )
    expect(
        mutate(
            admin,
            path + "/roles",
            {"roles": ["ADMIN"], "reason": "Synthetic missing version must be rejected"},
            method="PUT",
        ),
        428,
    )


def test_membership_suspension_revokes_immediately_and_retry_denies(env):
    admin = login(env, "admin-a@example.invalid")
    tech, membership = provision(env, "TECHNICIAN", "tech@example.invalid", admin)
    item = next(x for x in directory(env, admin) if x["id"] == membership["id"])
    path = f"/api/v1/orgs/{env['org']['id']}/memberships/{membership['id']}/status"
    expect(
        mutate(
            admin,
            path,
            {"status": "SUSPENDED", "reason": "Synthetic immediate access revocation test"},
            version=item["version"],
        ),
        201,
    )
    expect(tech.request("GET", f"/api/v1/orgs/{env['org']['id']}"), 401)
    assert (
        next(x for x in directory(env, admin) if x["id"] == membership["id"])["status"]
        == "SUSPENDED"
    )


def test_recent_reauthentication_and_safe_audit(env):
    admin = login(env, "admin-a@example.invalid")
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE sessions SET reauthenticated_at=now()-interval '11 minutes' WHERE user_id=(SELECT id FROM users WHERE email_normalized='admin-a@example.invalid')",
        )
    expect(
        mutate(
            admin,
            f"/api/v1/orgs/{env['org']['id']}/invitations",
            {"email": "tech@example.invalid", "role": "TECHNICIAN"},
        ),
        403,
    )
    login(env, "admin-a@example.invalid", admin)
    expect(
        mutate(
            admin,
            f"/api/v1/orgs/{env['org']['id']}/invitations",
            {"email": "tech@example.invalid", "role": "TECHNICIAN"},
        ),
        200,
    )
    logs = expect(admin.request("GET", f"/api/v1/orgs/{env['org']['id']}/audit-logs"), 200)["items"]
    assert logs and all(
        set(x) == {"id", "action", "resource_type", "resource_id", "occurred_at", "request_id"}
        for x in logs
    )
    assert "tech@example.invalid" not in str(logs)


def test_role_editor_persists_reason_and_revokes_old_sessions(env):
    admin = login(env, "admin-a@example.invalid")
    tech, member = provision(env, "TECHNICIAN", "tech@example.invalid", admin)
    item = next(x for x in directory(env, admin) if x["id"] == member["id"])
    path = f"/api/v1/orgs/{env['org']['id']}/memberships/{member['id']}/roles"
    reason = "SYNTHETIC explicit role revocation justification"
    expect(
        mutate(
            admin,
            path,
            {"roles": ["CITIZEN"], "reason": reason},
            version=item["version"],
            method="PUT",
        ),
        200,
    )
    expect(tech.request("GET", "/api/v1/me"), 401)
    with env["owner"].begin() as c:
        metadata = one(
            c,
            "SELECT safe_metadata FROM audit_logs WHERE resource_id=:i AND action LIKE '%roles' ORDER BY created_at DESC LIMIT 1",
            i=member["id"],
        )
        assert metadata["safe_metadata"] == {"governance_reason": reason}
