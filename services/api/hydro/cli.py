"""Private operator bootstrap. No passwords or tokens accepted as CLI arguments."""

import argparse
import getpass
import os
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import create_engine

from .contracts import OPERATIONS
from .db import one
from .errors import require
from .events import record
from .repository import insert
from .security import PASSWORDS, now


def reference_id(value):
    return uuid5(NAMESPACE_URL, "https://hydrooverity.local/catalogue/" + value)


def seed_catalogue(c):
    roles = {"ADMIN", "ENGINEER", "SUPERVISOR", "TECHNICIAN", "CITIZEN", "EVALUATOR"}
    for role in sorted(roles):
        if not one(c, "SELECT id FROM roles WHERE code=:v", v=role):
            insert(
                c,
                "roles",
                id=reference_id("role/" + role),
                code=role,
                description="Explicit " + role + " capability",
            )
    grants = set()
    from .service_contracts import ACTIVE
    from .service_contracts import OPERATIONS as service_operations

    for op in OPERATIONS + [o for o in service_operations if o["id"] in ACTIVE]:
        permission = op["permission"]
        if not one(c, "SELECT id FROM permissions WHERE code=:v", v=permission):
            insert(
                c,
                "permissions",
                id=reference_id("permission/" + permission),
                code=permission,
                description="Allow-listed " + permission,
            )
        if "PUBLIC" in op["roles"]:
            continue
        for role in roles - {"EVALUATOR"} if "ALL" in op["roles"] else set(op["roles"]):
            grants.add((role, permission))
    for role, permission in sorted(grants):
        rid = reference_id("role/" + role)
        pid = reference_id("permission/" + permission)
        if not one(
            c, "SELECT id FROM role_permissions WHERE role_id=:r AND permission_id=:p", r=rid, p=pid
        ):
            insert(
                c,
                "role_permissions",
                id=reference_id("grant/" + role + "/" + permission),
                role_id=rid,
                permission_id=pid,
            )


def bootstrap(
    c, *, confirmed_database, slug, name, email, display_name, password, reporting_enabled=False
):
    require(
        one(c, "SELECT current_database() AS name")["name"] == confirmed_database,
        400,
        "DATABASE_CONFIRMATION",
        "Target database confirmation does not match",
    )
    require(15 <= len(password) <= 128)
    email = email.strip().casefold()
    seed_catalogue(c)
    org = one(c, "SELECT * FROM organizations WHERE public_slug=:s FOR UPDATE", s=slug)
    user = one(c, "SELECT * FROM users WHERE email_normalized=:e FOR UPDATE", e=email)
    if org:
        require(
            user and org["name"] == name,
            409,
            "BOOTSTRAP_CONFLICT",
            "Existing organization differs; use authenticated governance",
        )
        m = one(
            c,
            "SELECT m.* FROM organization_memberships m JOIN role_assignments a ON a.membership_id=m.id JOIN roles r ON r.id=a.role_id WHERE m.organization_id=:o AND m.user_id=:u AND m.status='ACTIVE' AND a.revoked_at IS NULL AND r.code='ADMIN'",
            o=org["id"],
            u=user["id"],
        )
        require(
            m,
            409,
            "BOOTSTRAP_CONFLICT",
            "Existing organization requires authenticated administration",
        )
        return org, m, False
    require(
        user is None,
        409,
        "BOOTSTRAP_CONFLICT",
        "Existing identity requires invitation; bootstrap will not change it",
    )
    org = insert(
        c,
        "organizations",
        name=name,
        public_slug=slug,
        status="ACTIVE",
        retention_policy={},
        public_reporting_enabled=reporting_enabled,
    )
    user = insert(
        c,
        "users",
        email_normalized=email,
        display_name=display_name,
        password_hash=PASSWORDS.hash(password),
        email_verified_at=now(),
    )
    m = insert(
        c,
        "organization_memberships",
        organization_id=org["id"],
        user_id=user["id"],
        status="ACTIVE",
    )
    insert(
        c,
        "role_assignments",
        organization_id=org["id"],
        membership_id=m["id"],
        role_id=reference_id("role/ADMIN"),
        granted_by_id=m["id"],
    )
    record(
        c,
        org["id"],
        m["id"],
        "operator.bootstrap",
        "organizations",
        org["id"],
        uuid4(),
        "administration.read",
    )
    return org, m, True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("bootstrap")
    b.add_argument("--confirm-database", required=True)
    b.add_argument("--slug", required=True)
    b.add_argument("--name", required=True)
    b.add_argument("--admin-email", required=True)
    b.add_argument("--display-name", required=True)
    b.add_argument("--enable-reporting", action="store_true")
    sub.add_parser("catalogue")
    args = p.parse_args()
    connection = create_engine(os.environ["HYDRO_MIGRATION_URL"], hide_parameters=True)
    with connection.begin() as c:
        if args.command == "catalogue":
            seed_catalogue(c)
            print("Catalogue reconciled; no user grants created")
        else:
            password = os.environ.get("HYDRO_BOOTSTRAP_PASSWORD") or getpass.getpass(
                "Private bootstrap password (15..128 characters): "
            )
            org, member, created = bootstrap(
                c,
                confirmed_database=args.confirm_database,
                slug=args.slug,
                name=args.name,
                email=args.admin_email,
                display_name=args.display_name,
                password=password,
                reporting_enabled=args.enable_reporting,
            )
            print(
                "Organization",
                org["id"],
                "administrator membership",
                member["id"],
                "created" if created else "already present; password unchanged",
            )


if __name__ == "__main__":
    main()
