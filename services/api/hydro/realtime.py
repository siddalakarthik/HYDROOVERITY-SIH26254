"""Bounded authorized outbox history; opaque cursors contain no global sequence."""

import asyncio
import hashlib
import hmac
import json
import threading
import time
from dataclasses import dataclass
from uuid import UUID, uuid4

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from .auth import Auth
from .contracts import DESIGN, INVENTORY
from .db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from .errors import Problem, require
from .security import now, verifier
from .tenant import Tenant

OPERATIONS = [
    op
    for op in INVENTORY
    if op["path"]
    in {
        "/orgs/{organization_id}/events",
        "/orgs/{organization_id}/events/history",
    }
]
MAX_EVENTS = 100
MAX_BYTES = 256 * 1024
MAX_SESSION_CURSORS = 1000
HEARTBEAT_SECONDS = 15.0
POLL_SECONDS = 2.0
CONNECTION_SECONDS = 30.0
SEND_SECONDS = 5.0
READ_PERMISSIONS = {
    "citizen_complaints": "complaints.read",
    "complaint_status_events": "complaints.read",
    "work_orders": "work_orders.read",
    "work_order_actions": "work_orders.read",
    "repair_records": "repairs.read",
    "verification_records": "verification.read",
    "incidents": "incidents.read",
    "incident_links": "incidents.read",
    "water_zones": "water_zones.read",
    "network_junctions": "pipeline_assets.read",
    "pipe_segments": "pipeline_assets.read",
    "service_requests": "service_requests.read",
    "service_public_updates": "service_requests.read",
    "service_request_events": "service_requests.read",
    "service_work_order_links": "service_requests.read",
    "work_investigation_findings": "work_orders.read",
    "appointments": "dispatch.read",
    "appointment_requests": "dispatch.read",
    "appointment_events": "dispatch.read",
    "feedback_items": "feedback.read",
}


@dataclass
class EventScope:
    connection: object
    auth: Auth
    tenant: Tenant
    mode: str
    fingerprint: str
    key: bytes
    headers: Response


class BoundedStreamingResponse(StreamingResponse):
    """Do not retain a blocked consumer past the transport write deadline."""

    def __init__(self, *args, on_close=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_close = on_close

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            # Synchronous/idempotent capacity release also covers cancellation
            # before response headers or the first generator iteration.
            if self.on_close is not None:
                self.on_close()

    async def stream_response(self, send):
        async def bounded_send(message):
            await asyncio.wait_for(send(message), timeout=SEND_SECONDS)

        try:
            await super().stream_response(bounded_send)
        except TimeoutError:
            # Delivery is unconfirmed. The connection closes and the client must
            # replay from its last *received* cursor or request a fresh snapshot.
            await self.body_iterator.aclose()


def authenticated_scope(app, request, op, c, organization, mode, *, count_request=True):
    require(principal_is_safe(c), 503, "UNSAFE_DATABASE_PRINCIPAL", "Unsafe runtime identity")
    require(
        one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
        503,
        "MIGRATION_REQUIRED",
        "Database migration is required",
    )
    headers = Response()
    auth = Auth(c, request, headers, app)
    auth.identify(count_request=count_request)
    auth.authenticated()
    # Match business mutations: auth/session -> organization lock -> member/role
    # locks. Reversing these last two can deadlock a concurrent role revocation.
    execute(
        c,
        "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
        key="hydro-dispatch:" + str(UUID(str(organization))),
    )
    tenant = Tenant(auth, op, {"organization_id": str(UUID(str(organization)))})
    require(mode in {"OPERATIONAL", "SIMULATION"}, 422, "INVALID_FILTER", "Invalid workspace mode")
    require(
        mode == "OPERATIONAL" or "ENGINEER" in tenant.roles,
        403,
        "MODE_FORBIDDEN",
        "Simulation events require engineer access",
    )
    execute(c, "SELECT set_config('hydro.session_id',:s,true)", s=str(auth.session["id"]))
    permissions = query(
        c,
        "SELECT p.code FROM role_assignments a JOIN role_permissions rp ON rp.role_id=a.role_id "
        "JOIN permissions p ON p.id=rp.permission_id WHERE a.membership_id=:m AND a.revoked_at IS NULL",
        m=tenant.member_id,
    )
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "roles": sorted(tenant.roles),
                "permissions": sorted({p["code"] for p in permissions}),
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return EventScope(
        c,
        auth,
        tenant,
        mode,
        fingerprint,
        app.state.settings.hmac_key.get_secret_value().encode(),
        headers,
    )


def token_for(value, identifier):
    return hmac.new(
        value.key, b"hydro-realtime-cursor:" + UUID(str(identifier)).bytes, "sha256"
    ).hexdigest()


def issue_cursor(value, position):
    c, tenant = value.connection, value.tenant
    params = dict(
        o=tenant.organization_id,
        m=tenant.member_id,
        s=value.auth.session["id"],
        mode=value.mode,
        fingerprint=value.fingerprint,
        position=position,
    )
    existing = one(
        c,
        "SELECT id,expires_at,token_hash,revoked_at FROM realtime_cursors WHERE organization_id=:o AND membership_id=:m "
        "AND session_id=:s AND workspace_mode=:mode AND permission_fingerprint=:fingerprint AND position=:position",
        **params,
    )
    if existing and existing["revoked_at"] is None and existing["expires_at"] > now():
        token = token_for(value, existing["id"])
        if bytes(existing["token_hash"]) != verifier(token):
            execute(
                c,
                "UPDATE realtime_cursors SET token_hash=:h WHERE id=:i",
                h=verifier(token),
                i=existing["id"],
            )
        return token
    active = one(
        c,
        "SELECT count(*) AS n FROM realtime_cursors WHERE session_id=:s AND expires_at>now() AND revoked_at IS NULL",
        s=value.auth.session["id"],
    )["n"]
    if active >= MAX_SESSION_CURSORS:
        # Capacity invalidation is explicit on replay: an evicted token resets
        # to an authoritative snapshot; it never silently skips missed records.
        execute(
            c,
            "UPDATE realtime_cursors SET revoked_at=now() WHERE id IN "
            "(SELECT id FROM realtime_cursors WHERE session_id=:s AND revoked_at IS NULL "
            "ORDER BY created_at,id LIMIT 100)",
            s=value.auth.session["id"],
        )
    identifier = uuid4()
    token = token_for(value, identifier)
    one(
        c,
        "INSERT INTO realtime_cursors(id,organization_id,membership_id,session_id,workspace_mode,permission_fingerprint,position,token_hash) "
        "VALUES(:i,:o,:m,:s,:mode,:fingerprint,:position,:hash) "
        "ON CONFLICT(organization_id,membership_id,session_id,workspace_mode,permission_fingerprint,position) "
        "DO UPDATE SET id=EXCLUDED.id,token_hash=EXCLUDED.token_hash,revoked_at=NULL,created_at=now(),expires_at=now()+interval '168 hours' RETURNING id",
        i=identifier,
        hash=verifier(token),
        **params,
    )
    return token


def cursor_position(value, token, watermark):
    if (
        not isinstance(token, str)
        or len(token) != 64
        or any(ch not in "0123456789abcdef" for ch in token)
    ):
        return None
    row = one(
        value.connection, "SELECT * FROM realtime_cursors WHERE token_hash=:h", h=verifier(token)
    )
    if (
        not row
        or row["revoked_at"] is not None
        or row["expires_at"] <= now()
        or row["position"] > watermark
    ):
        return None
    if row["workspace_mode"] != value.mode or row["permission_fingerprint"] != value.fingerprint:
        return None
    if not hmac.compare_digest(token, token_for(value, row["id"])):
        return None
    return row["position"]


def allowed(value, event):
    c, t = value.connection, value.tenant
    table = event["resource_type"]
    permission = READ_PERMISSIONS.get(table)
    if permission is None:
        return False
    grants = one(
        c,
        "SELECT 1 FROM role_assignments a JOIN role_permissions rp ON rp.role_id=a.role_id "
        "JOIN permissions p ON p.id=rp.permission_id WHERE a.membership_id=:m "
        "AND a.revoked_at IS NULL AND p.code=:p LIMIT 1",
        m=t.member_id,
        p=permission,
    )
    if not grants:
        return False
    # Table identifiers are exclusively from this source allowlist, never client data.
    row = one(
        c,
        f"SELECT * FROM {table} WHERE organization_id=:o AND id=:i",
        o=t.organization_id,
        i=event["resource_id"],
    )
    if not row:
        return False
    if table in {"complaint_status_events"}:
        row = one(c, "SELECT * FROM citizen_complaints WHERE id=:i", i=row["complaint_id"])
        table = "citizen_complaints"
    if table == "citizen_complaints":
        return row and ("SUPERVISOR" in t.roles or row["reporter_id"] == t.member_id)
    if table in {"work_order_actions", "repair_records", "work_investigation_findings"}:
        work_id = row["work_order_id"]
        row = one(c, "SELECT * FROM work_orders WHERE id=:i", i=work_id)
        table = "work_orders"
    if table == "verification_records":
        row = one(
            c,
            "SELECT w.* FROM work_orders w JOIN repair_records r ON r.work_order_id=w.id WHERE r.id=:i",
            i=row["repair_id"],
        )
        table = "work_orders"
    if table == "work_orders":
        return row and (
            bool(t.roles & {"SUPERVISOR", "ENGINEER"}) or row["assignee_id"] == t.member_id
        )
    if table in {"service_public_updates", "service_request_events", "service_work_order_links"}:
        if (
            table in {"service_request_events", "service_work_order_links"}
            and "SUPERVISOR" not in t.roles
        ):
            return False
        row = one(c, "SELECT * FROM service_requests WHERE id=:i", i=row["request_id"])
        table = "service_requests"
    if table == "service_requests":
        return row and ("SUPERVISOR" in t.roles or row["owner_membership_id"] == t.member_id)
    if table in {"appointments", "appointment_requests", "appointment_events"}:
        if table == "appointment_events":
            row = one(c, "SELECT * FROM appointments WHERE id=:i", i=row["appointment_id"])
        if not row:
            return False
        if "SUPERVISOR" in t.roles:
            return True
        if row.get("assignee_id") == t.member_id:
            work = one(
                c,
                "SELECT assignee_id,assignment_version FROM work_orders WHERE id=:i",
                i=row["work_order_id"],
            )
            return bool(
                work
                and work["assignee_id"] == t.member_id
                and work["assignment_version"] == row["assignment_version"]
            )
        case = one(c, "SELECT * FROM service_requests WHERE id=:i", i=row["request_id"])
        return case and case["owner_membership_id"] == t.member_id
    if table == "feedback_items":
        return row and ("SUPERVISOR" in t.roles or row["owner_membership_id"] == t.member_id)
    return bool(t.roles & {"ENGINEER", "SUPERVISOR"})


def linked_booking_change(tenant, table, row):
    """Outbox-only signal for linked rows changed by an audited booking command.

    Caller holds the existing organization mutation lock and transaction. The
    command's existing audit and notification behavior remain unchanged.
    """
    require(table in {"appointments", "work_orders"}, 500, "INVALID_EVENT", "Invalid linked update")
    execute(
        tenant.c,
        "INSERT INTO domain_events(organization_id,event_type,resource_type,resource_id,workspace_mode,minimum_permission,occurred_at,safe_summary) "
        "VALUES(:o,'linked_record_changed',:t,:i,'OPERATIONAL',:p,now(),'{}')",
        o=tenant.organization_id,
        t=table,
        i=row["id"],
        p=READ_PERMISSIONS[table],
    )


def history(
    app, request, op, organization, mode="OPERATIONAL", token=None, limit=100, *, count_request=True
):
    require(
        type(limit) is int and 1 <= limit <= MAX_EVENTS,
        422,
        "INVALID_LIMIT",
        "Invalid history limit",
    )
    with app.state.engine.begin() as c:
        value = authenticated_scope(
            app, request, op, c, organization, mode, count_request=count_request
        )
        watermark = one(
            c,
            "SELECT coalesce(max(sequence),0) AS n FROM domain_events WHERE organization_id=:o",
            o=value.tenant.organization_id,
        )["n"]
        after = cursor_position(value, token, watermark)
        reset = after is None
        if reset:
            position, rows = watermark, []
        else:
            rows = query(
                c,
                "SELECT * FROM domain_events WHERE organization_id=:o AND sequence>:n AND workspace_mode=:mode "
                "ORDER BY sequence LIMIT :limit",
                o=value.tenant.organization_id,
                n=after,
                mode=mode,
                limit=limit,
            )
            if any((now() - row["created_at"]).total_seconds() > 7 * 86400 for row in rows):
                reset, rows = True, []
                position = watermark
            else:
                position = rows[-1]["sequence"] if rows else watermark
        output, event_cursors = [], []
        for row in rows:
            if allowed(value, row):
                event_cursors.append(issue_cursor(value, row["sequence"]))
                output.append(
                    {
                        "id": str(row["id"]),
                        "event_type": "record_changed",
                        "resource_id": row["resource_id"],
                        "occurred_at": row["occurred_at"],
                        "workspace_mode": row["workspace_mode"],
                        "safe_summary": "An authorized record changed; fetch its current state.",
                    }
                )
        page = jsonable_encoder(
            {"items": output, "next_cursor": issue_cursor(value, position), "as_of": now()}
        )
        require(
            len(json.dumps(page).encode()) <= MAX_BYTES,
            503,
            "REPLAY_CAPACITY",
            "Replay payload capacity exceeded",
        )
        value.headers.headers["X-HYDRO-Reset-Required"] = "true" if reset else "false"
        value.headers.headers["X-HYDRO-Record-Updates"] = "not-physical-sensor-freshness"
        return page, value.headers, reset, event_cursors


def current_event_allowed(app, request, op, organization, mode, identifier):
    with app.state.engine.begin() as c:
        value = authenticated_scope(app, request, op, c, organization, mode, count_request=False)
        row = one(
            c,
            "SELECT * FROM domain_events WHERE id=:i AND organization_id=:o AND workspace_mode=:mode",
            i=UUID(identifier),
            o=value.tenant.organization_id,
            mode=mode,
        )
        return row is not None and bool(allowed(value, row))


def extend_openapi(spec):
    for operation in OPERATIONS:
        path, method = operation["path"], operation["method"]
        spec["paths"].setdefault(path, {})[method] = DESIGN["paths"][path][method]
    for name in ("EventEnvelope", "Page_EventEnvelope"):
        spec["components"]["schemas"][name] = DESIGN["components"]["schemas"][name]
    return spec


def dispatch(app, request, op, body, params):
    require(body is None, 422, "UNEXPECTED_BODY", "This read operation accepts no body")
    raw = request.query_params.get("limit", "50")
    try:
        limit = int(raw)
    except ValueError:
        raise Problem(422, "INVALID_LIMIT", "Invalid history limit") from None
    page, headers, _, _ = history(
        app,
        request,
        op,
        params["organization_id"],
        request.query_params.get("workspace_mode", "OPERATIONAL"),
        request.query_params.get("cursor"),
        limit,
    )
    return page, 200, headers


def frame(kind, value, cursor=None):
    prefix = f"id: {cursor}\n" if cursor else ""
    return (
        prefix + "event: " + kind + "\ndata: " + json.dumps(value, separators=(",", ":")) + "\n\n"
    )


def bind(app):
    from .routes import endpoint

    app.state.realtime_capacity = threading.BoundedSemaphore(20)
    for operation in OPERATIONS:
        if operation["path"].endswith("/history"):
            app.add_api_route(
                "/api/v1" + operation["path"],
                endpoint(app, operation, DESIGN, dispatch),
                methods=["GET"],
                operation_id=operation["id"],
                include_in_schema=False,
            )
        else:
            app.add_api_route(
                "/api/v1" + operation["path"],
                sse_endpoint(app, operation),
                methods=["GET"],
                operation_id=operation["id"],
                include_in_schema=False,
            )


def sse_endpoint(app, operation):
    async def connect(request: Request):
        require(
            set(request.query_params) <= {"workspace_mode"}
            and len(request.query_params.multi_items()) == len(request.query_params),
            422,
            "INVALID_FILTER",
            "Invalid stream filter",
        )
        async for chunk in request.stream():
            require(not chunk, 422, "UNEXPECTED_BODY", "Stream subscriptions accept no body")
        mode = request.query_params.get("workspace_mode", "OPERATIONAL")
        cursor = request.headers.get("last-event-id")
        require(
            cursor is None or len(cursor) <= 500, 422, "INVALID_CURSOR", "Invalid replay cursor"
        )
        # Authenticate before reporting connection capacity; no anonymous stream resource allocation.
        initial = await run_in_threadpool(
            history,
            app,
            request,
            operation,
            request.path_params["organization_id"],
            mode,
            cursor,
            MAX_EVENTS,
        )
        require(
            app.state.realtime_capacity.acquire(blocking=False),
            503,
            "STREAM_CAPACITY",
            "Stream connection capacity reached",
        )
        released, release_lock = False, threading.Lock()

        def release_capacity():
            nonlocal released
            with release_lock:
                if not released:
                    released = True
                    app.state.realtime_capacity.release()

        async def generate():
            nonlocal cursor
            page, _, reset, cursors = initial
            started = last_heartbeat = time.monotonic()
            try:
                while True:
                    if reset:
                        yield frame(
                            "reset_required",
                            {
                                "cursor": page["next_cursor"],
                                "reason": "fetch_authoritative_snapshot",
                                "workspace_mode": mode,
                            },
                            page["next_cursor"],
                        )
                    for item, event_cursor in zip(page["items"], cursors, strict=True):
                        try:
                            permitted = await run_in_threadpool(
                                current_event_allowed,
                                app,
                                request,
                                operation,
                                request.path_params["organization_id"],
                                mode,
                                item["id"],
                            )
                        except Problem as exc:
                            kind = (
                                "authorization_lost"
                                if exc.status in {401, 403, 404}
                                else "reset_required"
                            )
                            yield frame(kind, {"reason": "reauthorization_or_snapshot_required"})
                            return
                        except Exception:
                            yield frame("reset_required", {"reason": "persistence_unavailable"})
                            return
                        if not permitted:
                            continue
                        yield frame("record_changed", item, event_cursor)
                    cursor = page["next_cursor"]
                    yield frame(
                        "checkpoint",
                        {"cursor": cursor, "as_of": page["as_of"], "workspace_mode": mode},
                        cursor,
                    )
                    if time.monotonic() - started >= CONNECTION_SECONDS:
                        yield frame(
                            "reconnect_required",
                            {"reason": "reauthorize_connection", "cursor": cursor},
                        )
                        return
                    if await request.is_disconnected():
                        return
                    await asyncio.sleep(POLL_SECONDS)
                    if time.monotonic() - last_heartbeat >= HEARTBEAT_SECONDS:
                        yield ": heartbeat\n\n"
                        last_heartbeat = time.monotonic()
                    try:
                        page, _, reset, cursors = await run_in_threadpool(
                            history,
                            app,
                            request,
                            operation,
                            request.path_params["organization_id"],
                            mode,
                            cursor,
                            MAX_EVENTS,
                            count_request=False,
                        )
                    except Problem as exc:
                        kind = (
                            "authorization_lost"
                            if exc.status in {401, 403, 404}
                            else "reset_required"
                        )
                        yield frame(kind, {"reason": "reauthorization_or_snapshot_required"})
                        return
                    except Exception:
                        yield frame("reset_required", {"reason": "persistence_unavailable"})
                        return
            finally:
                release_capacity()

        response = BoundedStreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-store",
                "X-Accel-Buffering": "no",
                "X-HYDRO-Record-Updates": "not-physical-sensor-freshness",
            },
            on_close=release_capacity,
        )
        for key, value in initial[1].raw_headers:
            if key.lower() not in {b"content-length", b"content-type"}:
                response.raw_headers.append((key, value))
        return response

    return connect
