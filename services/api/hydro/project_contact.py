"""Fixed private inbox. Operational intake/purge activation remains unavailable."""

import html
import unicodedata

from fastapi import Response

from .auth import Auth
from .contact_policy import ContactTestPolicy
from .contracts import DESIGN, INVENTORY, validator
from .db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from .errors import require

OPERATIONS = [op for op in INVENTORY if op["path"] == "/public/contact"]
LOCK = "hydro-project-contact-capacity"


def extend_openapi(spec):
    spec["paths"]["/public/contact"] = DESIGN["paths"]["/public/contact"]
    spec["components"]["schemas"]["ContactWrite"] = DESIGN["components"]["schemas"]["ContactWrite"]
    return spec


def configured(policy):
    require(
        isinstance(policy, ContactTestPolicy),
        503,
        "PROJECT_CONTACT_DISABLED",
        "Project contact intake is disabled pending operator and policy review",
    )
    return policy


def capacity_lock(c):
    execute(c, "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))", key=LOCK)


def text_body(value):
    require(
        not list(validator("ContactWrite").iter_errors(value)),
        422,
        "INVALID_BODY",
        "Body does not match the project contact contract",
    )
    message = value["message"].strip()
    email = value.get("reply_email", "").strip().casefold() or None
    require(len(message) >= 10, 422, "INVALID_BODY", "A meaningful project message is required")
    require(
        not any(unicodedata.category(ch) == "Cc" and ch not in "\n\t" for ch in message)
        and not any(ch.isspace() or unicodedata.category(ch) == "Cc" for ch in email or ""),
        422,
        "INVALID_BODY",
        "Control characters are not accepted",
    )
    return value["category"], message, email


def dispatch(app, request, op, value, params):
    response = Response()
    with app.state.engine.begin() as c:
        require(principal_is_safe(c), 503, "UNSAFE_DATABASE_PRINCIPAL", "Unsafe runtime identity")
        require(
            one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
            503,
            "MIGRATION_REQUIRED",
            "Database migration is required",
        )
        auth = Auth(c, request, response, app)
        auth.identify()
        auth.csrf()
        require(
            not request.headers.get("idempotency-key"),
            400,
            "IDEMPOTENCY_NOT_ALLOWED",
            "Project contact has no business receipt",
        )
        policy = configured(app.state.settings.contact_test_policy)
        limits = app.state.limits
        limits.hit("project-contact-session", str(auth.session["id"]), 3, 60)
        limits.hit("project-contact-ip", request.client.host if request.client else "local", 3, 60)
        category, message, email = text_body(value)
        if email:
            limits.hit("project-contact-email", email, 5, 86400)
        capacity_lock(c)
        count = one(c, "SELECT count(capacity_marker) AS n FROM project_contact_submissions")["n"]
        require(
            count < policy.capacity, 503, "PROJECT_CONTACT_CAPACITY", "Project inbox unavailable"
        )
        # No RETURNING: the runtime cannot retrieve inbox IDs/content/email.
        execute(
            c,
            "INSERT INTO project_contact_submissions(category,message,reply_email) VALUES(:category,:message,:email)",
            category=category,
            message=message,
            email=email,
        )
    return {"message": "Your project message has been accepted for review."}, 202, response


def owner(c, policy):
    configured(policy)
    require(
        one(
            c,
            "SELECT current_user=pg_get_userbyid(relowner) AS allowed "
            "FROM pg_class WHERE oid='public.project_contact_submissions'::regclass",
        )["allowed"],
        403,
        "PROJECT_OPERATOR_REQUIRED",
        "Separate project operator database identity required",
    )


def audit(c, policy, identifier, action):
    execute(
        c,
        "INSERT INTO project_contact_operator_audit(contact_id,operator_reference,action,policy_reference) "
        "VALUES(:i,:operator,:action,:policy)",
        i=identifier,
        operator=policy.operator_reference,
        action=action,
        policy=policy.policy_reference,
    )


def review_inbox(c, policy, limit=50):
    owner(c, policy)
    require(type(limit) is int and 1 <= limit <= 100, 422, "INVALID_LIMIT", "Invalid review limit")
    rows = query(
        c, "SELECT * FROM project_contact_submissions ORDER BY created_at,id LIMIT :n", n=limit
    )
    for row in rows:
        audit(c, policy, row["id"], "READ")
        row["message"] = html.escape(row["message"], quote=True)
        if row["reply_email"]:
            row["reply_email"] = html.escape(row["reply_email"], quote=True)
    return rows


def mark_reviewed(c, policy, identifier, version):
    owner(c, policy)
    row = one(
        c,
        "UPDATE project_contact_submissions SET status='REVIEWED',version=version+1,updated_at=now() "
        "WHERE id=:i AND version=:v RETURNING id",
        i=identifier,
        v=version,
    )
    require(row, 412, "VERSION_CONFLICT", "Project message changed or unavailable")
    audit(c, policy, identifier, "REVIEW")


def set_hold(c, policy, identifier, version, reference):
    owner(c, policy)
    require(
        reference is None or (isinstance(reference, str) and 10 <= len(reference) <= 128),
        422,
        "INVALID_HOLD",
        "A bounded separately reviewed hold reference is required",
    )
    row = one(
        c,
        "UPDATE project_contact_submissions SET hold_reference=:hold,version=version+1,updated_at=now() "
        "WHERE id=:i AND version=:v RETURNING id",
        i=identifier,
        v=version,
        hold=reference,
    )
    require(row, 412, "VERSION_CONFLICT", "Project message changed or unavailable")
    audit(c, policy, identifier, "HOLD" if reference else "RELEASE_HOLD")


def purge_synthetic_policy(c, policy):
    """Only synthetic test policy is representable; real purge activation is not implemented."""
    owner(c, policy)
    capacity_lock(c)
    rows = query(
        c,
        "SELECT id FROM project_contact_submissions WHERE expires_at<=now() "
        "AND hold_reference IS NULL ORDER BY expires_at,id LIMIT 100 FOR UPDATE",
    )
    for row in rows:
        audit(c, policy, row["id"], "PURGE")
        execute(c, "DELETE FROM project_contact_submissions WHERE id=:i", i=row["id"])
    return len(rows)
