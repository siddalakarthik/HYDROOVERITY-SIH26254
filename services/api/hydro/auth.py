"""Global identity repository. Auth never enters tenant business idempotency."""

import hmac
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import Connection

from .db import context, execute, one, query
from .errors import require
from .security import COOKIE, DUMMY, PASSWORDS, now, password_matches, secret, verifier


def user_view(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "display_name": user["display_name"],
        "email": user["email_normalized"],
        "verified": user["email_verified_at"] is not None,
    }


class Auth:
    def __init__(self, c: Connection, request, response, app):
        self.c, self.request, self.response, self.app = c, request, response, app
        self.session: dict[str, Any] | None = None
        self.user: dict[str, Any] | None = None
        self.deliveries: list[tuple[str, str, str]] = []

    def identify(
        self, cleanup: bool = False, identity_write: bool = False, *, count_request: bool = True
    ) -> None:
        raw = self.request.cookies.get(COOKIE, "")
        row = (
            one(self.c, "SELECT * FROM sessions WHERE token_hash=:h", h=verifier(raw))
            if raw
            else None
        )
        require(row, 401, "UNAUTHENTICATED", "A current session is required")
        # Consistent order: identity before session. Login/reset/suspension share
        # a transaction advisory lock acquired by the dispatcher before identify.
        if row["user_id"]:
            self.user = one(
                self.c,
                "SELECT * FROM users WHERE id=:u "
                + ("FOR UPDATE" if identity_write else "FOR SHARE"),
                u=row["user_id"],
            )
        self.session = one(self.c, "SELECT * FROM sessions WHERE id=:i FOR UPDATE", i=row["id"])
        s = self.session
        if cleanup:
            require(
                now() < s["absolute_expires_at"] + timedelta(days=30),
                401,
                "UNAUTHENTICATED",
                "Unknown cleanup session",
            )
        else:
            require(
                s["revoked_at"] is None
                and now() < min(s["idle_expires_at"], s["absolute_expires_at"]),
                401,
                "UNAUTHENTICATED",
                "A current session is required",
            )
            require(
                not self.user or self.user["deactivated_at"] is None,
                401,
                "UNAUTHENTICATED",
                "Identity unavailable",
            )
            if self.user:
                execute(
                    self.c,
                    "UPDATE sessions SET idle_expires_at=least(now()+interval '30 minutes',absolute_expires_at),updated_at=now() WHERE id=:i",
                    i=s["id"],
                )
        context(self.c, self.user["id"] if self.user else None)
        # A stream's internal reauthorization repeats every security check but
        # does not invent additional HTTP requests for the session throttle.
        # Ordinary endpoints use the default; realtime separately bounds its
        # initial subscription/history requests.
        if count_request:
            self.app.state.limits.hit("general", str(s["id"]), 120, 60)

    def authenticated(self) -> None:
        require(
            self.user
            and self.session["auth_level"] == "AUTHENTICATED"
            and self.user["email_verified_at"],
            401,
            "UNAUTHENTICATED",
            "Verified authentication is required",
        )

    def csrf(self) -> None:
        headers = self.request.headers
        require(
            headers.get("origin") == self.app.state.settings.origin,
            403,
            "ORIGIN_DENIED",
            "Same-origin mutation required",
        )
        require(
            headers.get("sec-fetch-site", "same-origin") in {"same-origin", "none"},
            403,
            "ORIGIN_DENIED",
            "Same-origin mutation required",
        )
        submitted = headers.get("x-csrf-token", "")
        require(
            submitted
            and hmac.compare_digest(verifier(submitted), bytes(self.session["csrf_hash"])),
            403,
            "CSRF_DENIED",
            "Session-bound CSRF token is required",
        )

    def bootstrap_csrf(self) -> dict[str, Any]:
        ip = self.request.client.host if self.request.client else "local"
        self.app.state.limits.hit("csrf", ip, 30, 60)
        try:
            self.identify()
        except Exception as exc:
            from .errors import Problem

            if not isinstance(exc, Problem) or exc.status != 401:
                raise
            self.session = None
            self.user = None
        csrf = secret()
        if self.session:
            execute(
                self.c,
                "UPDATE sessions SET csrf_hash=:h,updated_at=now() WHERE id=:i",
                h=verifier(csrf),
                i=self.session["id"],
            )
            expiry = min(self.session["idle_expires_at"], self.session["absolute_expires_at"])
        else:
            token = secret()
            expiry = now() + timedelta(minutes=10)
            # Bound preauth rows independently of IP buckets and retain cleanup
            # verifiers only for the explicitly supported 30-day window.
            execute(self.c, "SELECT hydro_expire_sessions()")
            require(
                one(
                    self.c,
                    "SELECT count(*) AS n FROM sessions WHERE auth_level='PREAUTH' AND revoked_at IS NULL AND absolute_expires_at>now()",
                )["n"]
                < 10000,
                503,
                "PREAUTH_CAPACITY",
                "Preauthentication capacity reached",
            )
            execute(
                self.c,
                "INSERT INTO sessions(token_hash,csrf_hash,auth_level,idle_expires_at,absolute_expires_at) VALUES(:h,:c,'PREAUTH',:e,:e)",
                h=verifier(token),
                c=verifier(csrf),
                e=expiry,
            )
            self.cookie(token, 600)
        return {"csrf_token": csrf, "expires_at": expiry}

    def cookie(self, token: str, lifetime: int) -> None:
        self.response.set_cookie(
            COOKIE, token, secure=True, httponly=True, samesite="lax", path="/", max_age=lifetime
        )

    def issue_session(
        self, user: dict[str, Any], absolute: datetime, reauthenticated: datetime | None
    ) -> None:
        token = secret()
        csrf = secret()
        execute(
            self.c,
            "INSERT INTO sessions(user_id,token_hash,csrf_hash,auth_level,idle_expires_at,absolute_expires_at,reauthenticated_at) VALUES(:u,:h,:csrf,'AUTHENTICATED',:idle,:absolute,:reauth)",
            u=user["id"],
            h=verifier(token),
            csrf=verifier(csrf),
            idle=min(now() + timedelta(minutes=30), absolute),
            absolute=absolute,
            reauth=reauthenticated,
        )
        self.cookie(token, max(1, int((absolute - now()).total_seconds())))

    def email_token(self, user: dict[str, Any], purpose: str) -> None:
        previous = one(
            self.c,
            "SELECT created_at FROM account_recovery_tokens WHERE user_id=:u AND purpose=:p ORDER BY created_at DESC LIMIT 1",
            u=user["id"],
            p=purpose,
        )
        if previous and now() - previous["created_at"] < timedelta(seconds=60):
            return
        execute(
            self.c,
            "UPDATE account_recovery_tokens SET used_at=now(),updated_at=now(),version=version+1 WHERE user_id=:u AND purpose=:p AND used_at IS NULL",
            u=user["id"],
            p=purpose,
        )
        token = secret()
        execute(
            self.c,
            "INSERT INTO account_recovery_tokens(user_id,purpose,token_hash,expires_at) VALUES(:u,:p,:h,now()+interval '30 minutes')",
            u=user["id"],
            p=purpose,
            h=verifier(token),
        )
        self.deliveries.append((purpose, user["email_normalized"], token))

    def run(self, action: str, body: dict[str, Any] | None) -> dict[str, Any]:
        b = body or {}
        c = self.c
        ip = self.request.client.host if self.request.client else "local"
        email = b.get("email", "").strip().casefold()
        limits = self.app.state.limits
        if action in {"login", "recovery"}:
            limits.hit(action + "-ip", ip, 5, 60)
            limits.hit(action + "-account", email, 20, 3600)
        elif action == "register":
            limits.hit("register-account", email, 5, 3600)
        elif action in {"reset", "verify", "invitation-accept"}:
            limits.hit(action + "-ip", ip, 10, 60)
            limits.hit(action + "-session", str(self.session["id"]), 10, 60)
        message = {
            "message": "Request accepted; check the private development delivery channel where applicable"
        }
        if action == "register":
            org = one(
                c,
                "SELECT * FROM organizations WHERE public_slug=:s AND public_reporting_enabled AND status='ACTIVE'",
                s=b["utility_slug"],
            )
            require(org, 404, "NOT_FOUND", "Utility unavailable")
            user = one(c, "SELECT * FROM users WHERE email_normalized=:e FOR UPDATE", e=email)
            if user is None:
                user = one(
                    c,
                    "INSERT INTO users(email_normalized,display_name,password_hash) VALUES(:e,:n,:h) RETURNING *",
                    e=email,
                    n=b["display_name"],
                    h=PASSWORDS.hash(b["password"]),
                )
                context(c, user["id"], org["id"])
                m = one(
                    c,
                    "INSERT INTO organization_memberships(organization_id,user_id,status) VALUES(:o,:u,'PENDING') RETURNING id",
                    o=org["id"],
                    u=user["id"],
                )
                execute(
                    c,
                    "INSERT INTO role_assignments(organization_id,membership_id,role_id,granted_by_id) SELECT :o,:m,id,:m FROM roles WHERE code='CITIZEN'",
                    o=org["id"],
                    m=m["id"],
                )
            else:
                # Keep the dominant password cost for generic duplicate replies.
                PASSWORDS.hash(b["password"])
            if user["email_verified_at"] is None:
                self.email_token(user, "VERIFY")
            return message
        if action == "login":
            user = one(c, "SELECT * FROM users WHERE email_normalized=:e FOR UPDATE", e=email)
            valid = password_matches(user["password_hash"] if user else DUMMY, b["password"])
            require(
                valid and user and user["email_verified_at"] and user["deactivated_at"] is None,
                401,
                "INVALID_CREDENTIALS",
                "Credentials are invalid or identity is not verified",
            )
            execute(
                c,
                "UPDATE sessions SET revoked_at=coalesce(revoked_at,now()),updated_at=now() WHERE id=:i",
                i=self.session["id"],
            )
            self.issue_session(user, now() + timedelta(hours=12), now())
            return user_view(user)
        if action == "logout":
            execute(
                c,
                "UPDATE sessions SET revoked_at=coalesce(revoked_at,now()),updated_at=now() WHERE id=:i",
                i=self.session["id"],
            )
            self.response.delete_cookie(
                COOKIE, path="/", secure=True, httponly=True, samesite="lax"
            )
            return {"message": "Session revoked"}
        if action == "recovery":
            user = one(c, "SELECT * FROM users WHERE email_normalized=:e FOR UPDATE", e=email)
            if user and user["email_verified_at"] and user["deactivated_at"] is None:
                self.email_token(user, "RESET")
            return message
        if action in {"reset", "verify"}:
            purpose = "RESET" if action == "reset" else "VERIFY"
            t = one(
                c,
                "SELECT * FROM account_recovery_tokens WHERE token_hash=:h AND purpose=:p AND used_at IS NULL AND expires_at>now() FOR UPDATE",
                h=verifier(b["token"]),
                p=purpose,
            )
            require(t, 422, "INVALID_TOKEN", "Token is invalid, expired or already used")
            user = one(
                c,
                "SELECT * FROM users WHERE id=:u AND deactivated_at IS NULL FOR UPDATE",
                u=t["user_id"],
            )
            require(user, 422, "INVALID_TOKEN", "Token is invalid, expired or already used")
            if action == "verify":
                limits.hit("verify-account", user["email_normalized"], 5, 3600)
                execute(
                    c,
                    "UPDATE users SET email_verified_at=coalesce(email_verified_at,now()),updated_at=now(),version=version+1 WHERE id=:u",
                    u=user["id"],
                )
                # Discover only this identity's memberships, then bind each tenant.
                context(c, user["id"])
                for m in query(c, "SELECT * FROM hydro_memberships()"):
                    context(c, user["id"], m["organization_id"])
                    execute(
                        c,
                        "UPDATE organization_memberships SET status='ACTIVE',version=version+1,updated_at=now() WHERE id=:m AND status='PENDING' AND EXISTS(SELECT 1 FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL AND r.code='CITIZEN') AND NOT EXISTS(SELECT 1 FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL AND r.code<>'CITIZEN')",
                        m=m["id"],
                    )
            else:
                execute(
                    c,
                    "UPDATE users SET password_hash=:h,version=version+1,updated_at=now() WHERE id=:u",
                    h=PASSWORDS.hash(b["new_password"]),
                    u=user["id"],
                )
                execute(
                    c,
                    "UPDATE sessions SET revoked_at=coalesce(revoked_at,now()),updated_at=now() WHERE user_id=:u AND auth_level='AUTHENTICATED'",
                    u=user["id"],
                )
            execute(
                c,
                "UPDATE account_recovery_tokens SET used_at=now(),updated_at=now(),version=version+1 WHERE id=:i",
                i=t["id"],
            )
            return {"message": "Identity action completed; authenticate separately"}
        if action == "invitation-accept":
            self.authenticated()
            inv = one(c, "SELECT * FROM hydro_invitation(:h)", h=verifier(b["token"]))
            require(inv, 422, "INVALID_TOKEN", "Token is invalid, expired or already used")
            context(c, self.user["id"], inv["organization_id"])
            i = one(
                c,
                "SELECT i.*,r.code FROM invitations i JOIN roles r ON r.id=i.role_id WHERE i.id=:i AND i.accepted_at IS NULL AND i.expires_at>now() FOR UPDATE OF i",
                i=inv["id"],
            )
            require(
                i
                and i["email_normalized"] == self.user["email_normalized"]
                and i["code"] in {"ADMIN", "SUPERVISOR", "ENGINEER", "TECHNICIAN"},
                422,
                "INVALID_TOKEN",
                "Token is invalid, expired or already used",
            )
            issuer = one(
                c,
                "SELECT m.id FROM organization_memberships m JOIN users u ON u.id=m.user_id "
                "JOIN role_assignments a ON a.membership_id=m.id JOIN roles r ON r.id=a.role_id "
                "WHERE m.id=:m AND m.status='ACTIVE' AND u.deactivated_at IS NULL "
                "AND a.revoked_at IS NULL AND r.code='ADMIN' FOR SHARE OF m,a",
                m=i["invited_by_id"],
            )
            require(issuer, 422, "INVALID_TOKEN", "Token is invalid, expired or already used")
            m = one(
                c,
                "SELECT * FROM organization_memberships WHERE user_id=:u AND organization_id=:o FOR UPDATE",
                u=self.user["id"],
                o=i["organization_id"],
            )
            require(
                not m or m["status"] != "SUSPENDED",
                403,
                "MEMBERSHIP_SUSPENDED",
                "Suspension requires administrator review",
            )
            if not m:
                m = one(
                    c,
                    "INSERT INTO organization_memberships(organization_id,user_id,status) VALUES(:o,:u,'ACTIVE') RETURNING *",
                    o=i["organization_id"],
                    u=self.user["id"],
                )
            execute(
                c,
                "INSERT INTO role_assignments(organization_id,membership_id,role_id,granted_by_id) VALUES(:o,:m,:r,:g) ON CONFLICT (organization_id,membership_id,role_id) WHERE revoked_at IS NULL DO NOTHING",
                o=i["organization_id"],
                m=m["id"],
                r=i["role_id"],
                g=i["invited_by_id"],
            )
            execute(
                c,
                "UPDATE invitations SET accepted_at=now(),updated_at=now(),version=version+1 WHERE id=:i",
                i=i["id"],
            )
            from .events import record

            record(
                c,
                i["organization_id"],
                m["id"],
                "invitation.accepted",
                "organization_memberships",
                m["id"],
                self.request.state.request_id,
                "administration.read",
            )
            # Privilege changed: rotate this session without extending its
            # absolute lifetime or pretending that reauthentication occurred.
            execute(
                c,
                "UPDATE sessions SET revoked_at=coalesce(revoked_at,now()) WHERE user_id=:u",
                u=self.user["id"],
            )
            self.issue_session(
                self.user, self.session["absolute_expires_at"], self.session["reauthenticated_at"]
            )
            return {"message": "Invitation accepted; session rotated"}
        raise AssertionError("Unregistered authentication operation")
