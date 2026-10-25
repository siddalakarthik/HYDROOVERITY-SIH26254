"""Current-principal communications and feedback, with transactional receipts."""

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from starlette.responses import Response

from ..auth import Auth
from ..communications_contracts import DESIGN, validator
from ..db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from ..errors import require
from ..events import record
from ..repository import insert as receipt_insert
from ..security import now
from ..tenant import Tenant, receipt

TABLES = {"notification_preferences", "notifications", "feedback_items"}


def row(c, table, identifier, organization, lock=False):
    assert table in TABLES
    result = one(
        c,
        f"SELECT * FROM {table} WHERE id=:i AND organization_id=:o"
        + (" FOR UPDATE" if lock else ""),
        i=identifier,
        o=organization,
    )
    require(result, 404, "NOT_FOUND", "Resource unavailable")
    return result


class Scope(Tenant):
    def feedback(self, identifier, lock=False):
        item = row(self.c, "feedback_items", identifier, self.organization_id, lock)
        general = item["service_request_id"] is None and item["complaint_id"] is None
        require(
            item["owner_membership_id"] == self.member_id
            or "SUPERVISOR" in self.roles
            or (general and "ADMIN" in self.roles),
            404,
            "NOT_FOUND",
            "Resource unavailable",
        )
        return item

    def notification(self, identifier, lock=False):
        item = row(self.c, "notifications", identifier, self.organization_id, lock)
        require(
            item["recipient_id"] == self.member_id and item["state"] == "DELIVERED",
            404,
            "NOT_FOUND",
            "Resource unavailable",
        )
        from ..notification_worker import authorized_target

        require(
            authorized_target(self.c, item, self.member_id),
            404,
            "NOT_FOUND",
            "Notification resource is no longer available",
        )
        return item

    def view(self, table, item):
        if table == "notification_preferences":
            return {
                "version": item["version"],
                "channels": {"in_app": item["in_app"], "email": False, "sms": False, "push": False},
                "event_categories": item["event_categories"],
                "quiet_hours": item["quiet_hours"],
                "email_available": False,
            }
        if table == "feedback_items":
            return {
                k: item[k]
                for k in (
                    "id",
                    "summary",
                    "description",
                    "status",
                    "resolution_note",
                    "version",
                    "service_request_id",
                    "service_rating",
                )
            }
        if self.op["id"] == "m07_n42":
            return {
                "notification_id": item["id"],
                "event_kind": item["event_category"],
                **{
                    k: item[k]
                    for k in (
                        "channel",
                        "state",
                        "attempt_number",
                        "attempted_at",
                        "next_attempt_at",
                        "safe_error_code",
                    )
                },
            }
        return {
            "read": item["read_at"] is not None,
            **{
                k: item[k]
                for k in (
                    "id",
                    "message",
                    "created_at",
                    "version",
                    "event_category",
                    "resource_path",
                )
            },
        }

    def listing(self, table, extra="true", **values):
        filters = dict(self.auth.request.query_params)
        service_id = filters.pop("service_request_id", None)
        if service_id:
            try:
                service_id = UUID(service_id)
            except ValueError:
                require(False, 422, "INVALID_FILTER", "Invalid service identifier")
            case = one(
                self.c,
                "SELECT * FROM service_requests WHERE organization_id=:o AND id=:r",
                o=self.organization_id,
                r=service_id,
            )
            require(
                case
                and (case["owner_membership_id"] == self.member_id or "SUPERVISOR" in self.roles),
                404,
                "NOT_FOUND",
                "Resource unavailable",
            )
            extra += " AND service_request_id=:service_filter"
            values["service_filter"] = service_id
        # HMAC keyset cursor binds membership, current roles, parent and filter.
        binding = hashlib.sha256(
            json.dumps(
                [
                    str(self.member_id),
                    sorted(self.roles),
                    self.op["id"],
                    self.params,
                    str(service_id),
                ],
                sort_keys=True,
            ).encode()
        ).hexdigest()[:24]
        secret = self.auth.app.state.settings.hmac_key.get_secret_value().encode()
        stamp = now()
        try:
            limit = int(filters.get("limit", 50))
            require(1 <= limit <= 100, 422, "INVALID_FILTER", "Invalid page limit")
            if filters.get("cursor"):
                payload, signature = filters["cursor"].split(".")
                require(
                    hmac.compare_digest(
                        signature, hmac.new(secret, payload.encode(), "sha256").hexdigest()
                    ),
                    422,
                    "INVALID_CURSOR",
                    "Invalid cursor",
                )
                decoded = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
                require(
                    decoded["scope"] == binding,
                    422,
                    "INVALID_CURSOR",
                    "Cursor belongs to another scope",
                )
                stamp = datetime.fromisoformat(decoded["as_of"])
                extra += " AND (created_at,id)<(:after_time,:after_id)"
                values.update(
                    after_time=datetime.fromisoformat(decoded["time"]), after_id=UUID(decoded["id"])
                )
        except (ValueError, TypeError, KeyError):
            require(False, 422, "INVALID_CURSOR", "Invalid cursor or page limit")
        items = query(
            self.c,
            f"SELECT * FROM {table} WHERE organization_id=:o AND ({extra}) AND created_at<=:stamp ORDER BY created_at DESC,id DESC LIMIT :n",
            o=self.organization_id,
            stamp=stamp,
            n=limit + 1,
            **values,
        )
        cursor = None
        if len(items) > limit:
            last = items[limit - 1]
            payload = (
                base64.urlsafe_b64encode(
                    json.dumps(
                        {
                            "scope": binding,
                            "as_of": stamp.isoformat(),
                            "time": last["created_at"].isoformat(),
                            "id": str(last["id"]),
                        }
                    ).encode()
                )
                .decode()
                .rstrip("=")
            )
            cursor = payload + "." + hmac.new(secret, payload.encode(), "sha256").hexdigest()
        return {
            "items": [self.view(table, i) for i in items[:limit]],
            "next_cursor": cursor,
            "as_of": stamp,
        }


def preferences(s, lock=False):
    result = one(
        s.c,
        "SELECT * FROM notification_preferences WHERE organization_id=:o AND membership_id=:m"
        + (" FOR UPDATE" if lock else ""),
        o=s.organization_id,
        m=s.member_id,
    )
    require(
        result,
        503,
        "PREFERENCES_NOT_PROVISIONED",
        "Membership preferences require provisioning; no read-side creation was performed",
    )
    return result


def parent_for(s, b, write):
    op = s.op["id"]
    if op in {"m07_n40", "m07_n41"}:
        return preferences(s, write), "notification_preferences"
    if "notification_id" in s.params:
        return s.notification(s.params["notification_id"], write), "notifications"
    if "feedback_id" in s.params:
        return s.feedback(s.params["feedback_id"], write), "feedback_items"
    if op == "m07_n42":
        case = one(
            s.c,
            "SELECT * FROM service_requests WHERE organization_id=:o AND id=:r",
            o=s.organization_id,
            r=s.params["request_id"],
        )
        require(case and "SUPERVISOR" in s.roles, 404, "NOT_FOUND", "Resource unavailable")
    if b.get("service_request_id"):
        case = one(
            s.c,
            "SELECT * FROM service_requests WHERE organization_id=:o AND id=:r FOR SHARE",
            o=s.organization_id,
            r=b["service_request_id"],
        )
        require(
            case and case["owner_membership_id"] == s.member_id,
            404,
            "NOT_FOUND",
            "Resource unavailable",
        )
        require(
            case["status"] in {"SERVICE_CLOSED", "CANCELLED"},
            409,
            "FEEDBACK_NOT_ELIGIBLE",
            "Service feedback requires a closed or cancelled case",
        )
    if b.get("complaint_id"):
        require(
            not b.get("service_request_id"), 422, "AMBIGUOUS_PARENT", "Choose one feedback parent"
        )
        s.complaint(b["complaint_id"], own=True)
    require(
        not b.get("service_rating") or b.get("service_request_id"),
        422,
        "RATING_REQUIRES_SERVICE",
        "A rating requires an eligible service",
    )
    return None, "feedback_items"


def mutate(s, b, parent, table):
    c, o, a = s.c, s.organization_id, s.member_id
    if s.op["id"] == "m07_n41":
        quiet = b["quiet_hours"]
        require(
            quiet is None or quiet["start_local"] != quiet["end_local"],
            422,
            "INVALID_QUIET_HOURS",
            "Quiet hours must have different boundaries",
        )
        result = one(
            c,
            "UPDATE notification_preferences SET in_app=:enabled,event_categories=CAST(:categories AS jsonb),quiet_hours=CAST(:quiet AS jsonb),version=version+1,updated_at=now() WHERE id=:i RETURNING *",
            enabled=b["channels"]["in_app"],
            categories=json.dumps(b["event_categories"]),
            quiet=json.dumps(quiet) if quiet else None,
            i=parent["id"],
        )
    elif table == "notifications":
        # Monotonic read; a second separately keyed command does not change the timestamp.
        result = (
            parent
            if parent["read_at"]
            else one(
                c,
                "UPDATE notifications SET read_at=now(),version=version+1,updated_at=now() WHERE id=:i RETURNING *",
                i=parent["id"],
            )
        )
    elif parent:
        general = parent["service_request_id"] is None and parent["complaint_id"] is None
        require(
            "SUPERVISOR" in s.roles or (general and "ADMIN" in s.roles),
            403,
            "FORBIDDEN",
            "Case feedback requires a supervisor",
        )
        require(
            b["linked_github_issue_url"] is None,
            422,
            "EXTERNAL_LINK_DISABLED",
            "External issue linkage is not activated",
        )
        require(
            b["resolution_note"].strip() and b["severity"].strip(),
            422,
            "REVIEW_REASON_REQUIRED",
            "Provide a public explanation and private severity",
        )
        if b["assignee_membership_id"]:
            member = s.row("organization_memberships", b["assignee_membership_id"])
            require(
                member["status"] == "ACTIVE",
                409,
                "MEMBERSHIP_INACTIVE",
                "Reviewer assignment requires active membership",
            )
        result = one(
            c,
            "UPDATE feedback_items SET status=:status,resolution_note=:note,severity=:severity,assignee_membership_id=:assignee,version=version+1,updated_at=now() WHERE id=:i RETURNING *",
            status=b["status"],
            note=b["resolution_note"],
            severity=b["severity"],
            assignee=b["assignee_membership_id"],
            i=parent["id"],
        )
    else:
        result = one(
            c,
            "INSERT INTO feedback_items(organization_id,owner_membership_id,summary,description,complaint_id,service_request_id,service_rating) VALUES(:o,:a,:summary,:description,:complaint,:service,:rating) RETURNING *",
            o=o,
            a=a,
            summary=b["summary"],
            description=b["description"],
            complaint=b["complaint_id"],
            service=b.get("service_request_id"),
            rating=b.get("service_rating"),
        )
    if table == "feedback_items":
        execute(
            c,
            "INSERT INTO feedback_events(organization_id,feedback_id,actor_id,resulting_version,status,public_note,private_severity) VALUES(:o,:f,:a,:v,:s,:n,:p)",
            o=o,
            f=result["id"],
            a=a,
            v=result["version"],
            s=result["status"],
            n=result["resolution_note"],
            p=result["severity"],
        )
    record(
        c,
        o,
        a,
        s.op["id"],
        table,
        result["id"],
        s.auth.request.state.request_id,
        s.op["permission"],
    )
    return result


def dispatch(app, request, op, value, params):
    response = Response()
    spec = DESIGN["paths"][op["path"]][op["method"]]
    status = min(int(x) for x in spec["responses"] if x.startswith("2"))
    with app.state.engine.begin() as c:
        require(
            principal_is_safe(c),
            503,
            "UNSAFE_DATABASE_PRINCIPAL",
            "Unsafe runtime database identity",
        )
        require(
            one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
            503,
            "MIGRATION_REQUIRED",
            "Database migration required",
        )
        auth = Auth(c, request, response, app)
        auth.identify()
        auth.authenticated()
        write = op["method"] != "get"
        if write:
            auth.csrf()
        try:
            params = {k: str(UUID(v)) for k, v in params.items()}
        except ValueError:
            require(False, 422, "INVALID_IDENTIFIER", "Invalid resource identifier")
        execute(
            c,
            "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
            key="hydro-dispatch:" + params["organization_id"],
        )
        s = Scope(auth, op, params)
        app.state.limits.hit("m07c-operation", str(s.member_id), 100, 60)
        schema = (
            spec.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
            .get("$ref")
        )
        if schema:
            require(
                not list(validator(schema.rsplit("/", 1)[1]).iter_errors(value))
                and "\\u0000" not in json.dumps(value),
                422,
                "INVALID_BODY",
                "Body does not match the operation contract",
            )
        else:
            require(value is None, 422, "UNEXPECTED_BODY", "This operation accepts no body")
        b = value or {}
        parent, table = parent_for(s, b, write)
        if not write:
            if op["id"] == "m07_n40":
                result = s.view(table, parent)
            elif op["id"] == "m07_n42":
                result = s.listing("notifications", "service_request_id=:r", r=params["request_id"])
            elif op["path"].endswith("/feedback"):
                result = s.listing("feedback_items")
            else:
                # Stale/reassigned resource links are filtered in SQL before pagination.
                from ..notification_worker import inbox_access_sql

                result = s.listing(
                    "notifications",
                    "recipient_id=:member AND state='DELIVERED' AND " + inbox_access_sql(),
                    member=s.member_id,
                )
        else:
            try:
                key = UUID(request.headers.get("idempotency-key", ""))
            except ValueError:
                require(False, 400, "IDEMPOTENCY_REQUIRED", "A UUID Idempotency-Key is required")
            fingerprint = hashlib.sha256(
                json.dumps({"body": b, "params": params}, sort_keys=True).encode()
            ).hexdigest()
            execute(
                c,
                "SELECT pg_advisory_xact_lock(hashtextextended(:k,0))",
                k=f"m07c:{s.organization_id}:{s.member_id}:{op['id']}:{key}",
            )
            prior = one(
                c,
                "SELECT * FROM idempotency_records WHERE organization_id=:o AND actor_scope=:a AND method=:m AND route_template=:r AND operation_key=:k AND expires_at>now()",
                o=s.organization_id,
                a=str(s.member_id),
                m=op["method"],
                r=op["path"],
                k=key,
            )
            if prior:
                require(
                    prior["request_hash"] == fingerprint,
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    "Key was used with different content",
                )
                item = (
                    s.feedback(prior["result_resource_id"])
                    if table == "feedback_items"
                    else s.notification(prior["result_resource_id"])
                    if table == "notifications"
                    else preferences(s)
                )
            else:
                if parent:
                    s.version(parent)
                item = mutate(s, b, parent, table)
                execute(c, "SELECT hydro_expire_receipts()")
                receipt_insert(
                    c,
                    "idempotency_records",
                    organization_id=s.organization_id,
                    actor_scope=str(s.member_id),
                    method=op["method"],
                    route_template=op["path"],
                    operation_key=key,
                    request_hash=fingerprint,
                    result_resource_id=item["id"],
                    result_status=status,
                    expires_at=now() + timedelta(days=7),
                )
            result = receipt(item) if table == "notifications" else s.view(table, item)
        if "version" in result:
            response.headers["ETag"] = f'"{result["version"]}"'
        wire = jsonable_encoder(
            result,
            custom_encoder={
                datetime: lambda d: d.astimezone(UTC).isoformat().replace("+00:00", "Z")
            },
        )
        output = spec["responses"][str(status)]["content"]["application/json"]["schema"][
            "$ref"
        ].rsplit("/", 1)[1]
        require(
            not list(validator(output).iter_errors(wire)),
            500,
            "RESPONSE_CONTRACT",
            "Server projection failed validation",
        )
    return wire, status, response
