"""Route orchestration: authenticate, authorize, transact, validate, then deliver."""

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi import Response
from fastapi.encoders import jsonable_encoder

from .auth import Auth, user_view
from .contracts import DESIGN, body, validator
from .db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from .errors import require
from .operations import Operations
from .repository import change, insert
from .security import now
from .tenant import Tenant


def lock(c, value):
    number = int.from_bytes(hashlib.sha256(value.encode()).digest()[:8], "big", signed=True)
    execute(c, "SELECT pg_advisory_xact_lock(:n)", n=number)


def global_page(rows, request):
    # Global identity lists are small but still use a scope-bound signed cursor.
    import base64
    import hmac

    from .errors import Problem

    params = dict(request.query_params)
    require(set(params) <= {"limit", "cursor"}, 422, "INVALID_FILTER", "Unknown list parameter")
    try:
        n = int(params.get("limit", 50))
        require(1 <= n <= 100)
        after = 0
        if params.get("cursor"):
            raw, sig = params["cursor"].split(".")
            key = request.app.state.settings.hmac_key.get_secret_value().encode()
            require(hmac.compare_digest(sig, hmac.new(key, raw.encode(), "sha256").hexdigest()))
            data = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
            require(data["scope"] == request.state.global_scope)
            after = next((i + 1 for i, r in enumerate(rows) if str(r["id"]) == data["id"]), -1)
            require(after >= 0)
        page = rows[after : after + n]
        cursor = None
        if after + n < len(rows):
            raw = (
                base64.urlsafe_b64encode(
                    json.dumps(
                        {"scope": request.state.global_scope, "id": str(page[-1]["id"])},
                        separators=(",", ":"),
                    ).encode()
                )
                .decode()
                .rstrip("=")
            )
            cursor = (
                raw
                + "."
                + hmac.new(
                    request.app.state.settings.hmac_key.get_secret_value().encode(),
                    raw.encode(),
                    "sha256",
                ).hexdigest()
            )
        return {"items": page, "next_cursor": cursor, "as_of": now()}
    except (ValueError, KeyError, TypeError):
        raise Problem(422, "INVALID_CURSOR", "Invalid list cursor or limit")


def current_user(auth, op, b, params):
    c = auth.c
    user = auth.user
    path = op["path"]
    method = op["method"]
    auth.request.state.global_scope = str(user["id"]) + path
    if path == "/me":
        if method == "patch":
            header = auth.request.headers.get("if-match")
            require(header, 428, "PRECONDITION_REQUIRED", "If-Match resource version required")
            require(
                header == f'"{user["version"]}"',
                412,
                "VERSION_CONFLICT",
                "Profile changed; refetch",
            )
            user = change(c, "users", user["id"], display_name=b["display_name"])
        auth.response.headers["ETag"] = f'"{user["version"]}"'
        return user_view(user)
    if path == "/me/memberships":
        return global_page(
            query(c, "SELECT * FROM hydro_memberships() ORDER BY organization_id,id"), auth.request
        )
    if path == "/me/sessions":
        rows = query(
            c,
            "SELECT id,created_at,idle_expires_at,absolute_expires_at,id=:i AS current FROM sessions WHERE user_id=:u AND revoked_at IS NULL AND absolute_expires_at>now() AND idle_expires_at>now() ORDER BY created_at DESC,id DESC",
            i=auth.session["id"],
            u=user["id"],
        )
        return global_page(rows, auth.request)
    row = one(
        c,
        "SELECT id FROM sessions WHERE id=:i AND user_id=:u",
        i=params["session_id"],
        u=user["id"],
    )
    require(row, 404, "NOT_FOUND", "Resource unavailable")
    execute(
        c,
        "UPDATE sessions SET revoked_at=coalesce(revoked_at,now()),updated_at=now() WHERE id=:i",
        i=row["id"],
    )
    return {"message": "Session revoked"}


def replay_table(op):
    g = op["group"]
    p = op["path"]
    if g == "Administration":
        return "invitations" if p.endswith("/invitations") else "organization_memberships"
    if g == "Water zones":
        return "water_zones"
    if g == "Pipeline assets":
        return "network_junctions" if "/junctions" in p else "pipe_segments"
    if g == "Complaints":
        return (
            "complaint_status_events"
            if p.endswith(("/review", "/follow-ups"))
            else "citizen_complaints"
        )
    if g == "Incidents":
        return "incident_links" if p.endswith("/links") else "incidents"
    if g == "Work orders":
        return "work_order_actions" if p.endswith("/actions") else "work_orders"
    return {
        "Repairs": "repair_records",
        "Verification": "verification_records",
        "Evidence": "evidence_assessments",
    }[g]


def dispatch(app, request, op, value, params):
    response = Response()
    deliveries = []
    spec = DESIGN["paths"][op["path"]][op["method"]]
    successes = [int(k) for k in spec["responses"] if str(k).startswith("2")]
    status = min(successes)
    with app.state.engine.begin() as c:
        require(
            principal_is_safe(c),
            503,
            "UNSAFE_DATABASE_PRINCIPAL",
            "Runtime database identity is not safe",
        )
        require(
            one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
            503,
            "MIGRATION_REQUIRED",
            "Database migration is required",
        )
        auth = Auth(c, request, response, app)
        identity_write = op["method"] != "get" and op["group"] in {
            "Authentication",
            "Current user",
            "Administration",
        }
        if identity_write:
            # Pilot serialization for identity mutation races; never distributed
            # process locks or a lock held across external delivery.
            lock(c, "hydro-global-identity-mutation")
        if op["path"] == "/auth/csrf":
            require(
                not request.headers.get("idempotency-key"),
                400,
                "IDEMPOTENCY_NOT_ALLOWED",
                "Authentication has no business receipt",
            )
            result = auth.bootstrap_csrf()
        else:
            public = op["group"] == "Public"
            if not public:
                auth.identify(cleanup=op["path"] == "/auth/logout", identity_write=identity_write)
            if op["method"] != "get":
                auth.csrf()
                if op["group"] in {"Authentication", "Current user"}:
                    require(
                        not request.headers.get("idempotency-key"),
                        400,
                        "IDEMPOTENCY_NOT_ALLOWED",
                        "This identity operation has no business receipt",
                    )
            b = body(op["request"], value) if op["request"] else {}
            if not op["request"]:
                require(
                    value is None, 422, "UNEXPECTED_BODY", "This operation accepts no request body"
                )
            for key, identifier in params.items():
                if key != "slug":
                    try:
                        params[key] = str(UUID(identifier))
                    except ValueError:
                        require(False, 422, "INVALID_IDENTIFIER", "Invalid resource identifier")
            if op["group"] == "Authentication":
                result = auth.run(op["path"].split("/")[-1], b)
            elif public:
                if op["path"].endswith("project-status"):
                    result = {
                        "project": "HYDROOVERITY",
                        "stage": "M03 private backend development",
                        "hardware_validation": "NOT_ESTABLISHED",
                        "field_validation": "NOT_ESTABLISHED",
                        "limitations": [
                            "Scientific results are simulation-only evidence",
                            "Digital hardware is not physically tested",
                            "No field-validated detection performance is established",
                        ],
                    }
                else:
                    org = one(
                        c,
                        "SELECT public_slug AS slug,name,public_reporting_enabled AS reporting_enabled FROM organizations WHERE public_slug=:s AND status='ACTIVE' AND public_reporting_enabled",
                        s=params["slug"],
                    )
                    require(org, 404, "NOT_FOUND", "Utility unavailable")
                    result = {**org, "service_areas": []}
            else:
                auth.authenticated()
                if op["group"] == "Current user":
                    result = current_user(auth, op, b, params)
                else:
                    scope = Tenant(auth, op, params)
                    if op["path"].endswith("/links"):
                        lock(c, "incident-links:" + str(scope.organization_id))
                    parent = scope.preauthorize(b)
                    if op["path"].endswith("/actions") and b:
                        require(
                            b["assignment_version"] == parent["assignment_version"],
                            409,
                            "ASSIGNMENT_CHANGED",
                            "Assignment changed; refetch current task",
                        )
                    service = Operations(scope)
                    if op["method"] == "get":
                        result = service.run(b, parent)
                        if parent and "version" in parent:
                            response.headers["ETag"] = f'"{parent["version"]}"'
                    else:
                        raw = request.headers.get("idempotency-key")
                        try:
                            key = UUID(raw or "")
                        except ValueError:
                            require(
                                False,
                                400,
                                "IDEMPOTENCY_REQUIRED",
                                "A UUID Idempotency-Key is required",
                            )
                        actor = str(scope.member_id)
                        route = op["path"]
                        request_hash = hashlib.sha256(
                            json.dumps(
                                {"body": b, "path": params},
                                sort_keys=True,
                                separators=(",", ":"),
                                allow_nan=False,
                            ).encode()
                        ).hexdigest()
                        lock(
                            c,
                            "receipt:"
                            + str(scope.organization_id)
                            + actor
                            + op["method"]
                            + route
                            + str(key),
                        )
                        execute(c, "SELECT hydro_expire_receipts()")
                        prior = one(
                            c,
                            "SELECT * FROM idempotency_records WHERE organization_id=:o AND actor_scope=:a AND method=:m AND route_template=:r AND operation_key=:k",
                            o=scope.organization_id,
                            a=actor,
                            m=op["method"],
                            r=route,
                            k=key,
                        )
                        if prior:
                            require(
                                prior["request_hash"] == request_hash,
                                409,
                                "IDEMPOTENCY_CONFLICT",
                                "Key was already used with different content",
                            )
                            row = scope.row(replay_table(op), prior["result_resource_id"])
                            result = scope.view(replay_table(op), row)
                            status = prior["result_status"]
                        else:
                            if any(
                                p["name"] == "If-Match" and p.get("required")
                                for p in spec.get("parameters", [])
                            ):
                                require(parent, 422, "MISSING_PARENT", "Versioned parent required")
                                scope.version(parent)
                            result = service.run(b, parent)
                            insert(
                                c,
                                "idempotency_records",
                                organization_id=scope.organization_id,
                                actor_scope=actor,
                                operation_key=key,
                                method=op["method"],
                                route_template=route,
                                request_hash=request_hash,
                                result_resource_id=service.result["id"],
                                result_status=status,
                                expires_at=now() + __import__("datetime").timedelta(days=7),
                            )
                            if "version" in service.result:
                                response.headers["ETag"] = f'"{service.result["version"]}"'
        wire = jsonable_encoder(
            result,
            custom_encoder={
                datetime: lambda value: value.astimezone(UTC).isoformat().replace("+00:00", "Z")
            },
        )
        name = ("Page_" + op["response"]) if op.get("list") else op["response"]
        require(
            not list(validator(name).iter_errors(wire)),
            500,
            "RESPONSE_CONTRACT",
            "Server projection failed contract validation",
        )
        deliveries = auth.deliveries
    # No delivery side effect before the database transaction commits.
    for purpose, recipient, token in deliveries:
        app.state.mail.deliver(purpose, recipient, token)
    return wire, status, response
