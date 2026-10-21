"""AdministrationService persistent operations and permission-aware projections."""

from datetime import timedelta

from ..db import execute, one, query
from ..errors import require
from ..repository import change, insert
from ..security import now, secret, verifier
from .base import Service


class AdministrationService(Service):
    def run(self, b, parent):
        s, c = self.s, self.c
        path = s.op["path"]
        method = s.op["method"]
        if method == "get":
            return s.page(
                "audit_logs" if path.endswith("/audit-logs") else "organization_memberships",
                dict(s.auth.request.query_params),
            )
        if path.endswith("/invitations"):
            token = secret()
            role = one(c, "SELECT id FROM roles WHERE code=:r", r=b["role"])
            row = insert(
                c,
                "invitations",
                organization_id=self.o,
                email_normalized=b["email"].strip().casefold(),
                role_id=role["id"],
                invited_by_id=self.a,
                token_hash=verifier(token),
                expires_at=now() + timedelta(minutes=30),
            )
            self.s.auth.deliveries.append(("INVITATION", row["email_normalized"], token))
            return self.save("invitations", row)
        # Serialize tenant governance and protect the last active administrator.
        one(c, "SELECT id FROM organizations WHERE id=:o FOR UPDATE", o=self.o)
        oldroles = {
            r["code"]
            for r in query(
                c,
                "SELECT r.code FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL",
                m=parent["id"],
            )
        }
        removes_admin = (path.endswith("/roles") and "ADMIN" not in b["roles"]) or b.get(
            "status"
        ) == "SUSPENDED"
        if parent["status"] == "ACTIVE" and "ADMIN" in oldroles and removes_admin:
            count = one(
                c,
                "SELECT count(DISTINCT m.id) AS n FROM organization_memberships m JOIN role_assignments a ON a.membership_id=m.id JOIN roles r ON r.id=a.role_id WHERE m.status='ACTIVE' AND a.revoked_at IS NULL AND r.code='ADMIN'",
            )["n"]
            require(
                count > 1,
                409,
                "LAST_ADMIN",
                "Transfer administration before removing the last active administrator",
            )
        if path.endswith("/roles"):
            wanted = set(b["roles"])
            require(len(wanted) == len(b["roles"]), 422, "DUPLICATE_ROLE", "Roles must be distinct")
            execute(
                c,
                "UPDATE role_assignments SET revoked_at=now(),updated_at=now(),version=version+1 WHERE membership_id=:m AND revoked_at IS NULL AND role_id IN (SELECT id FROM roles WHERE code<>ALL(:wanted))",
                m=parent["id"],
                wanted=list(wanted),
            )
            for role in wanted - oldroles:
                insert(
                    c,
                    "role_assignments",
                    organization_id=self.o,
                    membership_id=parent["id"],
                    role_id=one(c, "SELECT id FROM roles WHERE code=:r", r=role)["id"],
                    granted_by_id=self.a,
                )
            row = change(c, "organization_memberships", parent["id"], status=parent["status"])
        else:
            row = change(
                c,
                "organization_memberships",
                parent["id"],
                status=b["status"],
                suspended_at=now() if b["status"] == "SUSPENDED" else None,
            )
        # Global sessions are revoked immediately; other memberships remain unchanged.
        execute(
            c,
            "UPDATE invitations SET expires_at=least(expires_at,now()),updated_at=now(),version=version+1 "
            "WHERE accepted_at IS NULL AND (email_normalized=(SELECT email_normalized FROM users WHERE id=:u) "
            "OR (invited_by_id=:member AND :revoke_issued))",
            u=parent["user_id"],
            member=parent["id"],
            revoke_issued=b.get("status") == "SUSPENDED"
            or ("ADMIN" in oldroles and path.endswith("/roles") and "ADMIN" not in b["roles"]),
        )
        execute(
            c,
            "UPDATE sessions SET revoked_at=coalesce(revoked_at,now()),updated_at=now() WHERE user_id=:u",
            u=parent["user_id"],
        )
        return self.save("organization_memberships", row)
