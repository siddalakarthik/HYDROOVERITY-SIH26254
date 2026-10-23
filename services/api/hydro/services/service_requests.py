"""Service-request foundation, in one authenticated PostgreSQL transaction per request."""

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from starlette.responses import Response

from ..auth import Auth
from ..config import ROOT
from ..db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from ..errors import require
from ..events import record
from ..repository import change as legacy_change
from ..security import now
from ..service_contracts import DESIGN, DISABLED, validator
from ..tenant import Tenant, receipt

TABLES = {
    "service_requests",
    "service_request_events",
    "service_public_updates",
    "service_work_order_links",
    "work_investigation_findings",
}
TERMINAL = {"SERVICE_CLOSED", "DECLINED", "WITHDRAWN", "CANCELLED"}
PRE_ACCEPT = {"SUBMITTED", "UNDER_REVIEW", "AWAITING_RESIDENT"}
TRIAGED = {"ACCEPTED", "IN_PROGRESS", "REOPENED", "INVESTIGATION_REQUIRED"}
STATES = json.loads((ROOT / "data/schemas/m07-state-machines.json").read_text())["service"]


def insert(c, table, **values):
    assert table in TABLES
    return one(
        c,
        f"INSERT INTO {table} ({','.join(values)}) VALUES ({','.join(':' + k for k in values)}) RETURNING *",
        **values,
    )


def change(c, table, identifier, **values):
    if table != "service_requests":
        return legacy_change(c, table, identifier, **values)
    return one(
        c,
        f"UPDATE service_requests SET {','.join(k + '=:' + k for k in values)},version=version+1,updated_at=now() WHERE id=:identifier RETURNING *",
        identifier=identifier,
        **values,
    )


def reference():
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    number = secrets.randbits(128)
    return "HYS-" + "".join(alphabet[(number >> (5 * n)) & 31] for n in reversed(range(26)))


def public_update(row):
    return {
        k: row[k]
        for k in "id sequence event_kind message occurred_at published_at appointment_id supersedes_id".split()
    }


def work_link(row):
    return {
        **{k: row[k] for k in "id work_order_id purpose created_at version".split()},
        "service_request_id": row["request_id"],
    }


def finding(row):
    return {
        **{
            k: row[k]
            for k in "id work_order_id observed_at received_at findings no_repair_reason supersedes_id".split()
        },
        "recorded_by_membership_id": row["recorded_by_id"],
        "attachment_ids": [],
        "provenance": "MANUAL",
    }


class Scope(Tenant):
    def row(self, table, resource_id, lock=False):
        if table not in TABLES:
            return super().row(table, resource_id, lock)
        row = one(
            self.c,
            f"SELECT * FROM {table} WHERE id=:i AND organization_id=:o"
            + (" FOR UPDATE" if lock else ""),
            i=resource_id,
            o=self.organization_id,
        )
        require(row, 404, "NOT_FOUND", "Resource unavailable")
        return row

    def case(self, identifier, lock=False, own=False):
        row = self.row("service_requests", identifier, lock)
        require(
            not own or row["owner_membership_id"] == self.member_id,
            404,
            "NOT_FOUND",
            "Resource unavailable",
        )
        return row

    def staff(self):
        return "SUPERVISOR" in self.roles and self.op["id"] not in {"m07_n01", "m07_n06"}

    def view(self, table, row):
        if table == "service_requests":
            latest = one(
                self.c,
                "SELECT * FROM service_public_updates WHERE request_id=:i ORDER BY sequence DESC LIMIT 1",
                i=row["id"],
            )
            actions = []
            if self.staff():
                if row["status"] in PRE_ACCEPT:
                    actions = ["TRIAGE", "PUBLIC_UPDATE"]
                elif row["status"] not in TERMINAL:
                    actions = ["PUBLIC_UPDATE", "LINK_WORK", "TRANSITION"]
            elif row["status"] in PRE_ACCEPT:
                actions = ["FOLLOW_UP", "WITHDRAW"]
            elif row["status"] not in TERMINAL:
                actions = ["FOLLOW_UP"] + (
                    [] if row["cancellation_pending"] else ["REQUEST_CANCELLATION"]
                )
            result = {
                k: row[k]
                for k in "id tracking_reference category description coarse_area status cancellation_pending service_outcome created_at updated_at accepted_at version".split()
            }
            result.update(
                verification_summary="NOT_VERIFIABLE"
                if row["service_outcome"] == "REPAIR_REPORTED"
                else "NOT_APPLICABLE",
                own_origin_complaint_id=row["origin_complaint_id"],
                own_follow_up_of_id=row["follow_up_of_id"],
                preferences=None,
                latest_public_update=public_update(latest) if latest else None,
                current_appointment=None,
                allowed_actions=actions,
            )
            if self.staff():
                links = query(
                    self.c,
                    "SELECT * FROM service_work_order_links WHERE request_id=:i ORDER BY id",
                    i=row["id"],
                )
                event = one(
                    self.c,
                    "SELECT internal_reason FROM service_request_events WHERE request_id=:i ORDER BY sequence DESC LIMIT 1",
                    i=row["id"],
                )
                result.update(
                    owner_membership_id=row["owner_membership_id"],
                    work_links=[work_link(x) for x in links],
                    dispatch_health="UNCONFIGURED",
                    internal_event_summary=event["internal_reason"] if event else "",
                )
            return result
        if table == "service_public_updates":
            return public_update(row)
        if table == "service_request_events":
            return {
                **{
                    k: row[k]
                    for k in "id sequence event_kind received_at observed_at internal_reason resource_type resource_id previous_version resulting_version supersedes_id".split()
                },
                "actor_membership_id": row["actor_id"],
            }
        if table == "service_work_order_links":
            return work_link(row)
        if table == "work_investigation_findings":
            return finding(row)
        return super().view(table, row)


class Foundation:
    def __init__(self, s):
        self.s, self.c, self.o, self.a = s, s.c, s.organization_id, s.member_id
        self.result = None
        self.result_table = None

    def save(self, table, row, result=None):
        self.result_table, self.result = table, row
        record(
            self.c,
            self.o,
            self.a,
            self.s.op["id"],
            table,
            row["id"],
            self.s.auth.request.state.request_id,
            self.s.op["permission"],
        )
        return result if result is not None else self.s.view(table, row)

    def history(
        self,
        row,
        kind,
        private,
        message,
        operation_id=None,
        public_kind="SERVICE",
        supersedes=None,
        resource=None,
    ):
        # Root row is locked. Version is an ordered sequence; never MAX+1 across unlocked writers.
        event_id = uuid4()
        execute(
            self.c,
            "INSERT INTO service_request_events(id,organization_id,request_id,sequence,event_kind,actor_id,internal_reason,resource_type,resource_id,previous_version,resulting_version,operation_id) VALUES(:id,:o,:r,:v,:kind,:a,:reason,'SERVICE',:r,:prev,:v,:operation)",
            id=event_id,
            o=self.o,
            r=row["id"],
            v=row["version"],
            kind=kind,
            a=self.a,
            reason=private,
            prev=row["version"] - 1 or None,
            operation=operation_id,
        )
        return insert(
            self.c,
            "service_public_updates",
            organization_id=self.o,
            request_id=row["id"],
            sequence=row["version"],
            origin_event_id=event_id,
            actor_id=self.a,
            event_kind=public_kind,
            message=message,
            supersedes_id=supersedes,
        )

    def owned_references(self, b, check_version=True):
        if b["origin_complaint_id"]:
            row = self.s.complaint(b["origin_complaint_id"], True, True)
            require(
                not check_version or row["version"] == b["expected_complaint_version"],
                412,
                "VERSION_CONFLICT",
                "Report changed; refetch",
            )
        if b["follow_up_of_id"]:
            row = self.s.case(b["follow_up_of_id"], True, True)
            require(
                row["status"] in TERMINAL, 409, "CASE_ACTIVE", "Use a follow-up on the active case"
            )

    def replay(self, op, row):
        if op == "m07_n06":
            return receipt(row)
        if op == "m07_n43":
            return {
                "receipt": receipt(row),
                "resource": finding(row),
                "work_version": row["work_version"],
            }
        return self.s.view(self.result_table, row)

    def run(self, b, parent):
        s, c, n = self.s, self.c, self.s.op["id"]
        if s.op["method"] == "get":
            if n == "m07_n03":
                return s.view("service_requests", parent)
            if n == "m07_n44":
                require(
                    parent["task_purpose"] != "REPAIR",
                    409,
                    "FINDINGS_PURPOSE",
                    "Repair work uses repair receipts",
                )
                return self.page(
                    "work_investigation_findings", "work_order_id=:root", {"root": parent["id"]}
                )
            if n == "m07_n04":
                audience = s.auth.request.query_params.get("audience", "PUBLIC")
                require(
                    audience in {"PUBLIC", "INTERNAL"},
                    422,
                    "INVALID_FILTER",
                    "Unsupported audience",
                )
                require(
                    audience != "INTERNAL" or s.staff(),
                    403,
                    "FORBIDDEN",
                    "Internal timeline requires supervisor",
                )
                return {
                    **self.page(
                        "service_request_events"
                        if audience == "INTERNAL"
                        else "service_public_updates",
                        "request_id=:root",
                        {"root": parent["id"]},
                    ),
                    "audience": audience,
                }
            return self.page("service_requests")
        if n == "m07_n05":
            row = one(
                c,
                "SELECT id,tracking_reference FROM service_requests WHERE tracking_reference=:r AND organization_id=:o",
                r=b["tracking_reference"],
                o=self.o,
            )
            require(row, 404, "NOT_FOUND", "Resource unavailable")
            return row
        if n == "m07_n01":
            self.owned_references(b)
            row = insert(
                c,
                "service_requests",
                organization_id=self.o,
                owner_membership_id=self.a,
                tracking_reference=reference(),
                category=b["category"],
                description=b["description"],
                coarse_area=b["coarse_area"],
                origin_complaint_id=b["origin_complaint_id"],
                follow_up_of_id=b["follow_up_of_id"],
            )
            self.history(
                row,
                "SUBMITTED",
                "Resident requested utility review",
                "Your request was received for utility review. It is not yet accepted and no visit is booked.",
            )
            return self.save("service_requests", row)
        if n == "m07_n43":
            require(
                parent["task_purpose"] in {"INVESTIGATION", "INSPECTION"},
                409,
                "FINDINGS_PURPOSE",
                "Findings require investigation or inspection work",
            )
            require(
                parent["status"] in {"IN_PROGRESS", "BLOCKED"},
                409,
                "INVALID_STATE",
                "Record findings during active work",
            )
            require(
                b["assignment_version"] == parent["assignment_version"],
                409,
                "ASSIGNMENT_CHANGED",
                "Refetch assigned work",
            )
            require(not b["attachment_ids"], 422, "ATTACHMENTS_DISABLED", "Media remains disabled")
            observed = datetime.fromisoformat(b["observed_at"].replace("Z", "+00:00"))
            require(
                observed <= now() + timedelta(minutes=5),
                422,
                "INVALID_TIME",
                "Observed time is in the future",
            )
            if b["supersedes_id"]:
                prior = s.row("work_investigation_findings", b["supersedes_id"])
                require(
                    prior["work_order_id"] == parent["id"], 404, "NOT_FOUND", "Resource unavailable"
                )
                require(
                    prior["recorded_by_id"] == self.a,
                    403,
                    "FORBIDDEN",
                    "Only the author may correct findings",
                )
            updated = change(c, "work_orders", parent["id"], status=parent["status"])
            row = insert(
                c,
                "work_investigation_findings",
                organization_id=self.o,
                work_order_id=parent["id"],
                recorded_by_id=self.a,
                assignment_version=b["assignment_version"],
                work_version=updated["version"],
                operation_id=b["operation_id"],
                observed_at=observed,
                findings=b["findings"],
                no_repair_reason=b["no_repair_reason"],
                supersedes_id=b["supersedes_id"],
            )
            return self.save(
                "work_investigation_findings",
                row,
                {
                    "receipt": receipt(row),
                    "resource": finding(row),
                    "work_version": updated["version"],
                },
            )
        require(
            parent["status"] not in TERMINAL,
            409,
            "FINAL_SERVICE",
            "Final service history cannot be changed; submit a linked new request",
        )
        if n == "m07_n06":
            row = change(
                c,
                "service_requests",
                parent["id"],
                status="UNDER_REVIEW"
                if parent["status"] == "AWAITING_RESIDENT"
                else parent["status"],
            )
            update = self.history(
                row,
                "FOLLOW_UP",
                "Resident supplied a follow-up",
                b["message"],
                operation_id=b["operation_id"],
                public_kind="INFORMATION",
            )
            return self.save("service_public_updates", update, receipt(update))
        if n == "m07_n07":
            require(
                b["target"] in STATES[parent["status"]] and parent["status"] in PRE_ACCEPT,
                409,
                "INVALID_TRANSITION",
                "Triage transition is not allowed",
            )
            values = {"status": b["target"]}
            if b["target"] == "ACCEPTED":
                values.update(accepted_at=now(), accepted_by_id=self.a)
            row = change(c, "service_requests", parent["id"], **values)
            self.history(row, b["target"], b["internal_reason"], b["public_message"])
            return self.save("service_requests", row)
        if n == "m07_n09":
            correction = b["event_kind"] == "CORRECTION"
            require(
                correction == bool(b["supersedes_update_id"]),
                422,
                "CORRECTION_REFERENCE",
                "A correction must identify its prior update",
            )
            if correction:
                prior = s.row("service_public_updates", b["supersedes_update_id"])
                require(
                    prior["request_id"] == parent["id"], 404, "NOT_FOUND", "Resource unavailable"
                )
            row = change(c, "service_requests", parent["id"], status=parent["status"])
            update = self.history(
                row,
                "PUBLIC_UPDATE",
                "Supervisor published a customer-safe update",
                b["message"],
                public_kind=b["event_kind"],
                supersedes=b["supersedes_update_id"],
            )
            return self.save("service_public_updates", update)
        if n == "m07_n13":
            require(
                parent["status"] in {"ACCEPTED", "SERVICE_IN_PROGRESS", "SERVICE_REVIEW_PENDING"},
                409,
                "ACCEPTANCE_REQUIRED",
                "Accept service before linking work",
            )
            work = s.row("work_orders", b["work_order_id"], True)
            require(
                work["version"] == b["expected_work_version"],
                412,
                "VERSION_CONFLICT",
                "Work changed; refetch",
            )
            incident = s.row("incidents", work["incident_id"])
            require(
                incident["status"] in TRIAGED and work["status"] not in {"CANCELLED", "COMPLETED"},
                409,
                "TRIAGE_REQUIRED",
                "Link active work from a triaged incident",
            )
            require(
                work["workspace_mode"] == incident["workspace_mode"] == "OPERATIONAL"
                and b["purpose"] == work["task_purpose"],
                422,
                "PURPOSE_CONFLICT",
                "Purpose must match authorized operational work",
            )
            require(
                one(
                    c,
                    "SELECT count(*) AS n FROM service_work_order_links WHERE request_id=:r",
                    r=parent["id"],
                )["n"]
                < 20,
                409,
                "LINK_LIMIT",
                "At most twenty work links",
            )
            row = change(c, "service_requests", parent["id"], status=parent["status"])
            self.history(
                row,
                "WORK_LINKED",
                b["internal_reason"],
                "The utility linked authorized work to your request. No visit is confirmed.",
            )
            link = insert(
                c,
                "service_work_order_links",
                organization_id=self.o,
                request_id=parent["id"],
                work_order_id=work["id"],
                linked_by_id=self.a,
                purpose=b["purpose"],
            )
            return self.save("service_work_order_links", link)
        action = b["action"]
        citizen_action = action in {"WITHDRAW", "REQUEST_CANCELLATION"}
        require(
            "CITIZEN" in s.roles and parent["owner_membership_id"] == self.a
            if citizen_action
            else s.staff(),
            403,
            "FORBIDDEN",
            "Action exceeds current role or ownership",
        )
        if action == "REQUEST_CANCELLATION":
            require(
                parent["status"] not in PRE_ACCEPT and not parent["cancellation_pending"],
                409,
                "INVALID_TRANSITION",
                "Cancellation request is not available",
            )
            row = change(c, "service_requests", parent["id"], cancellation_pending=True)
        else:
            target = {
                "WITHDRAW": "WITHDRAWN",
                "CANCEL": "CANCELLED",
                "START_SERVICE": "SERVICE_IN_PROGRESS",
                "REQUEST_REVIEW": "SERVICE_REVIEW_PENDING",
                "RETURN_TO_WORK": "SERVICE_IN_PROGRESS",
                "CLOSE": "SERVICE_CLOSED",
            }[action]
            require(
                target in STATES[parent["status"]],
                409,
                "INVALID_TRANSITION",
                "Service transition is not allowed",
            )
            if action in {"CLOSE", "CANCEL"}:
                links = query(
                    c,
                    "SELECT w.* FROM work_orders w JOIN service_work_order_links l ON l.work_order_id=w.id AND l.organization_id=w.organization_id WHERE l.request_id=:r ORDER BY w.id FOR UPDATE OF w",
                    r=parent["id"],
                )
                expected = b["expected_work_versions"]
                require(
                    len({x["work_order_id"] for x in expected}) == len(expected)
                    and {str(x["id"]): x["version"] for x in links}
                    == {x["work_order_id"]: x["version"] for x in expected},
                    412,
                    "VERSION_CONFLICT",
                    "Supply exactly all current linked work versions",
                )
                require(
                    not b["child_dispositions"],
                    422,
                    "SCHEDULING_DISABLED",
                    "No appointment dispositions are enabled",
                )
                require(
                    all(x["status"] in {"COMPLETED", "CANCELLED"} for x in links),
                    409,
                    "LINKED_WORK_ACTIVE",
                    "Review or cancel linked work before final service disposition",
                )
                if action == "CLOSE" and b["service_outcome"] == "REPAIR_REPORTED":
                    require(
                        any(
                            one(
                                c,
                                "SELECT id FROM repair_records WHERE work_order_id=:w LIMIT 1",
                                w=x["id"],
                            )
                            for x in links
                        ),
                        409,
                        "REPAIR_REQUIRED",
                        "A real repair receipt is required for this operational outcome",
                    )
                require(
                    action != "CLOSE" or b["service_outcome"] != "VISIT_COMPLETED",
                    409,
                    "VISITS_DISABLED",
                    "Visit confirmation belongs to M07-B",
                )
            values = {"status": target}
            if action in {"CLOSE", "CANCEL"}:
                values["cancellation_pending"] = False
            if action == "CLOSE":
                values["service_outcome"] = b["service_outcome"]
            row = change(c, "service_requests", parent["id"], **values)
        self.history(
            row,
            action,
            b.get("internal_reason", "Resident requested " + action),
            b["public_message"],
        )
        return self.save("service_requests", row)

    def page(self, table, extra="", values=None):
        s = self.s
        filters = dict(s.auth.request.query_params)
        cursor = filters.pop("cursor", None)
        try:
            limit = int(filters.pop("limit", "50"))
        except ValueError:
            require(False, 422, "INVALID_FILTER", "Invalid page limit")
        require(1 <= limit <= 100, 422, "INVALID_FILTER", "Invalid page limit")
        clauses, params = ["organization_id=:org"], {"org": self.o, **(values or {})}
        if extra:
            clauses.append(extra)
        scope = hashlib.sha256(
            json.dumps(
                [
                    str(self.o),
                    str(self.a),
                    sorted(s.roles),
                    s.op["path"],
                    {k: str(v) for k, v in (values or {}).items()},
                    filters,
                ],
                sort_keys=True,
            ).encode()
        ).hexdigest()[:24]
        secret_key = s.auth.app.state.settings.hmac_key.get_secret_value().encode()
        stamp = now()
        if cursor:
            try:
                payload, signature = cursor.split(".")
                require(
                    hmac.compare_digest(
                        signature, hmac.new(secret_key, payload.encode(), "sha256").hexdigest()
                    )
                )
                data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
                require(data["scope"] == scope)
                params.update(
                    after_time=datetime.fromisoformat(data["time"]), after_id=UUID(data["id"])
                )
                stamp = datetime.fromisoformat(data["as_of"])
                clauses.append("(created_at,id)<(:after_time,:after_id)")
            except Exception:
                require(False, 422, "INVALID_CURSOR", "Cursor is invalid for the current scope")
        require(
            ("from" in filters) == ("to" in filters),
            422,
            "INVALID_TIME_RANGE",
            "Supply both time boundaries",
        )
        if "from" in filters:
            try:
                start = datetime.fromisoformat(filters["from"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(filters["to"].replace("Z", "+00:00"))
                require(
                    start.tzinfo and end.tzinfo and 0 < (end - start).total_seconds() <= 31 * 86400,
                    422,
                    "INVALID_TIME_RANGE",
                    "Use an ordered timezone-aware range up to 31 days",
                )
            except ValueError:
                require(False, 422, "INVALID_TIME_RANGE", "Invalid timestamps")
            params.update(start=start, end=end)
            clauses.append("created_at>=:start AND created_at<:end")
        for name in ("status", "category"):
            if name in filters:
                enum = "M07ServiceStatus" if name == "status" else "M07ServiceCategory"
                require(
                    filters[name] in DESIGN["components"]["schemas"][enum]["enum"],
                    422,
                    "INVALID_FILTER",
                    "Unsupported filter",
                )
                clauses.append(name + "=:" + name)
                params[name] = filters[name]
        params.update(stamp=stamp, limit=limit + 1)
        rows = query(
            self.c,
            f"SELECT * FROM {table} WHERE {' AND '.join(clauses)} AND created_at<=:stamp ORDER BY created_at DESC,id DESC LIMIT :limit",
            **params,
        )
        next_cursor = None
        if len(rows) > limit:
            last = rows[limit - 1]
            payload = (
                base64.urlsafe_b64encode(
                    json.dumps(
                        {
                            "scope": scope,
                            "time": last["created_at"].isoformat(),
                            "id": str(last["id"]),
                            "as_of": stamp.isoformat(),
                        },
                        separators=(",", ":"),
                    ).encode()
                )
                .decode()
                .rstrip("=")
            )
            next_cursor = (
                payload + "." + hmac.new(secret_key, payload.encode(), "sha256").hexdigest()
            )
        return {
            "items": [s.view(table, row) for row in rows[:limit]],
            "next_cursor": next_cursor,
            "as_of": stamp,
        }


def dispatch(app, request, op, value, params):
    response = Response()
    spec = DESIGN["paths"][op["path"]][op["method"]]
    status = min(int(x) for x in spec["responses"] if x.startswith("2"))
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
        auth.identify()
        auth.authenticated()
        if op["method"] != "get":
            auth.csrf()
        for k, v in params.items():
            try:
                params[k] = str(UUID(v))
            except ValueError:
                require(False, 422, "INVALID_IDENTIFIER", "Invalid resource identifier")
        s = Scope(auth, op, params)
        service = Foundation(s)
        if "request_id" in params:
            parent = s.case(params["request_id"], op["method"] != "get", op["id"] == "m07_n06")
        elif "work_order_id" in params:
            parent = s.work(
                params["work_order_id"], op["method"] != "get", assigned=op["id"] == "m07_n43"
            )
        else:
            parent = None
        require(
            op["id"] not in DISABLED,
            503,
            "PRIVACY_REVIEW_REQUIRED",
            "Visit preferences/access are disabled pending independent privacy and encryption review",
        )
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
        auth.app.state.limits.hit(
            "m07-lookup" if op["id"] == "m07_n05" else "m07-operation",
            str(s.member_id),
            30 if op["id"] == "m07_n05" else 100,
            60,
        )
        readonly = op["method"] == "get" or op["id"] == "m07_n05"
        if readonly:
            if op["id"] == "m07_n05":
                require(
                    not request.headers.get("idempotency-key"),
                    400,
                    "IDEMPOTENCY_NOT_ALLOWED",
                    "Reference lookup is read-only",
                )
            result = service.run(b, parent)
        else:
            if op["id"] == "m07_n01":
                service.owned_references(b, False)
            if op["id"] == "m07_n43":
                require(
                    b["assignment_version"] == parent["assignment_version"],
                    409,
                    "ASSIGNMENT_CHANGED",
                    "Refetch current assignment before retry",
                )
            if op["id"] == "m07_n13":
                s.row("work_orders", b["work_order_id"], True)
            if op["id"] in {"m07_n08"} and b["action"] in {"CLOSE", "CANCEL"}:
                query(
                    c,
                    "SELECT w.id FROM work_orders w JOIN service_work_order_links l ON l.work_order_id=w.id WHERE l.request_id=:r ORDER BY w.id FOR UPDATE OF w",
                    r=parent["id"],
                )
            raw = request.headers.get("idempotency-key", "")
            try:
                key = UUID(raw)
            except ValueError:
                require(False, 400, "IDEMPOTENCY_REQUIRED", "A UUID Idempotency-Key is required")
            fingerprint = hashlib.sha256(
                json.dumps(
                    {"body": b, "path": params}, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest()
            execute(
                c,
                "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
                key="m07:" + str(s.organization_id) + str(s.member_id) + op["id"] + str(key),
            )
            execute(c, "SELECT hydro_expire_receipts()")
            prior = one(
                c,
                "SELECT * FROM idempotency_records WHERE organization_id=:o AND actor_scope=:a AND method=:m AND route_template=:r AND operation_key=:k",
                o=s.organization_id,
                a=str(s.member_id),
                m=op["method"],
                r=op["path"],
                k=key,
            )
            tables = {
                "m07_n01": "service_requests",
                "m07_n06": "service_public_updates",
                "m07_n07": "service_requests",
                "m07_n08": "service_requests",
                "m07_n09": "service_public_updates",
                "m07_n13": "service_work_order_links",
                "m07_n43": "work_investigation_findings",
            }
            if prior:
                require(
                    prior["request_hash"] == fingerprint,
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    "Key was used with different content",
                )
                service.result_table = tables[op["id"]]
                row = s.row(service.result_table, prior["result_resource_id"])
                result = service.replay(op["id"], row)
                status = prior["result_status"]
            else:
                if spec.get("x-version-target"):
                    s.version(parent)
                result = service.run(b, parent)
                from ..repository import insert as legacy_insert

                legacy_insert(
                    c,
                    "idempotency_records",
                    organization_id=s.organization_id,
                    actor_scope=str(s.member_id),
                    operation_key=key,
                    method=op["method"],
                    route_template=op["path"],
                    request_hash=fingerprint,
                    result_resource_id=service.result["id"],
                    result_status=status,
                    expires_at=now() + timedelta(days=7),
                )
        if isinstance(result, dict) and "version" in result:
            response.headers["ETag"] = f'"{result["version"]}"'
        wire = jsonable_encoder(
            result,
            custom_encoder={
                datetime: lambda d: d.astimezone(UTC).isoformat().replace("+00:00", "Z")
            },
        )
        response_schema = spec["responses"][str(status)]["content"]["application/json"]["schema"][
            "$ref"
        ].rsplit("/", 1)[1]
        if op["id"] in {"m07_n02", "m07_n03", "m07_n08"}:
            response_schema = ("M07Page_" if op["id"] == "m07_n02" else "M07") + (
                "ServiceCaseStaff" if s.staff() else "ServiceCaseCitizen"
            )
        elif op["id"] == "m07_n04":
            response_schema = (
                "M07InternalTimelinePage"
                if wire["audience"] == "INTERNAL"
                else "M07PublicTimelinePage"
            )
        require(
            not list(validator(response_schema).iter_errors(wire)),
            500,
            "RESPONSE_CONTRACT",
            "Server projection failed contract validation",
        )
    return wire, status, response
