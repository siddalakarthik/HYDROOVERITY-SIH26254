"""Current membership, explicit permissions, ownership and safe projections."""

import base64
import hashlib
import hmac
import json
from datetime import datetime
from uuid import UUID

from .db import context, one, query
from .errors import Problem, require
from .security import now


def receipt(row):
    return {"id": row["id"], "version": row.get("version", 1), "received_at": row["created_at"]}


class Tenant:
    def __init__(self, auth, op, params):
        self.auth, self.c, self.op, self.params = auth, auth.c, op, params
        self.organization_id = UUID(params["organization_id"])
        context(self.c, auth.user["id"], self.organization_id)
        self.membership = one(
            self.c,
            "SELECT m.* FROM organization_memberships m JOIN organizations o ON o.id=m.organization_id WHERE m.organization_id=:o AND m.user_id=:u AND m.status='ACTIVE' AND o.status='ACTIVE' FOR SHARE OF m",
            o=self.organization_id,
            u=auth.user["id"],
        )
        require(self.membership, 404, "NOT_FOUND", "Resource unavailable")
        rows = query(
            self.c,
            "SELECT r.code,p.code AS permission FROM role_assignments a JOIN roles r ON r.id=a.role_id JOIN role_permissions rp ON rp.role_id=r.id JOIN permissions p ON p.id=rp.permission_id WHERE a.membership_id=:m AND a.revoked_at IS NULL FOR SHARE OF a",
            m=self.membership["id"],
        )
        self.roles = {r["code"] for r in rows}
        allowed = op["roles"]
        require(
            ("ALL" in allowed or self.roles.intersection(allowed))
            and any(r["permission"] == op["permission"] for r in rows),
            403,
            "FORBIDDEN",
            "Operation is not permitted",
        )
        if op["group"] == "Administration" and op["method"] != "get":
            require(
                auth.session["reauthenticated_at"]
                and (now() - auth.session["reauthenticated_at"]).total_seconds() <= 600,
                403,
                "REAUTHENTICATE",
                "Authenticate again before governance changes",
            )

    @property
    def member_id(self):
        return self.membership["id"]

    def row(self, table, resource_id, lock=False):
        from .repository import TABLES

        require(table in TABLES)
        row = one(
            self.c,
            f"SELECT * FROM {table} WHERE id=:i AND organization_id=:o"
            + (" FOR UPDATE" if lock else ""),
            i=resource_id,
            o=self.organization_id,
        )
        require(row, 404, "NOT_FOUND", "Resource unavailable")
        return row

    def work(self, resource_id, lock=False, assigned=False):
        row = self.row("work_orders", resource_id, lock)
        if assigned or not self.roles.intersection({"SUPERVISOR", "ENGINEER"}):
            require(row["assignee_id"] == self.member_id, 404, "NOT_FOUND", "Resource unavailable")
        return row

    def complaint(self, resource_id, lock=False, own=False):
        row = self.row("citizen_complaints", resource_id, lock)
        if own or "SUPERVISOR" not in self.roles:
            require(row["reporter_id"] == self.member_id, 404, "NOT_FOUND", "Resource unavailable")
        return row

    def preauthorize(self, b):
        """Reauthorize every resource reference before checking a business receipt."""
        p = self.params
        parent = None
        if "complaint_id" in p:
            parent = self.complaint(
                p["complaint_id"],
                self.op["method"] != "get",
                self.op["path"].endswith("follow-ups"),
            )
        elif "work_order_id" in p:
            parent = self.work(
                p["work_order_id"],
                self.op["method"] != "get",
                self.op["path"].endswith("/brief")
                or (
                    self.op["path"].endswith(("/actions", "/repairs"))
                    and self.op["method"] == "post"
                ),
            )
        elif "repair_id" in p:
            parent = self.row("repair_records", p["repair_id"])
            self.work(parent["work_order_id"], self.op["method"] != "get")
        elif "incident_id" in p:
            parent = self.row("incidents", p["incident_id"], self.op["method"] != "get")
        elif "membership_id" in p:
            parent = self.row(
                "organization_memberships", p["membership_id"], self.op["method"] != "get"
            )
        elif "assessment_id" in p:
            parent = self.row("evidence_assessments", p["assessment_id"])
        elif "resource_id" in p:
            table = {
                "Water zones": "water_zones",
                "Pipeline assets": "network_junctions"
                if "/junctions" in self.op["path"]
                else "pipe_segments",
            }[self.op["group"]]
            parent = self.row(table, p["resource_id"], self.op["method"] != "get")
        for key, table in {
            "zone_id": "water_zones",
            "incident_id": "incidents",
            "target_incident_id": "incidents",
            "assignee_membership_id": "organization_memberships",
            "from_junction_id": "network_junctions",
            "to_junction_id": "network_junctions",
        }.items():
            if b.get(key):
                self.row(table, b[key])
        for key, table in {
            "assessment_ids": "evidence_assessments",
            "evidence_record_ids": "evidence_records",
            "before_evidence_record_ids": "evidence_records",
            "after_evidence_record_ids": "evidence_records",
        }.items():
            for identifier in b.get(key, []):
                self.row(table, identifier)
        return parent

    def version(self, parent):
        expected = self.auth.request.headers.get("if-match")
        require(
            expected is not None, 428, "PRECONDITION_REQUIRED", "If-Match resource version required"
        )
        require(
            expected == f'"{parent.get("version", 1)}"',
            412,
            "VERSION_CONFLICT",
            "Resource changed; refetch before updating",
        )

    def view(self, table, row):
        if table == "organizations":
            return {k: row[k] for k in ("id", "name", "public_slug")}
        if table == "water_zones":
            return {
                "id": row["id"],
                "name": row["name"],
                "topology_quality": row["topology_quality"],
                "supply_state": "UNKNOWN",
            }
        if table == "organization_memberships":
            roles = query(
                self.c,
                "SELECT r.code FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL ORDER BY r.code",
                m=row["id"],
            )
            org = one(self.c, "SELECT name FROM organizations WHERE id=:o", o=self.organization_id)
            return {
                "id": row["id"],
                "organization_id": self.organization_id,
                "organization_name": org["name"],
                "roles": [x["code"] for x in roles],
                "status": row["status"],
                "version": row["version"],
            }
        if table == "citizen_complaints":
            updates = query(
                self.c,
                "SELECT status,public_message AS message,occurred_at FROM complaint_status_events WHERE complaint_id=:i ORDER BY occurred_at DESC,id DESC LIMIT 100",
                i=row["id"],
            )
            return {
                **{
                    k: row[k]
                    for k in (
                        "id",
                        "tracking_number",
                        "category",
                        "description",
                        "coarse_area",
                        "status",
                        "version",
                    )
                },
                "public_updates": updates,
            }
        if table == "work_orders":
            return {
                **{
                    k: row[k]
                    for k in (
                        "id",
                        "incident_id",
                        "status",
                        "priority",
                        "due_at",
                        "instructions",
                        "version",
                        "assignment_version",
                        "workspace_mode",
                    )
                },
                "assignee_membership_id": row["assignee_id"],
            }
        fields = {
            "incidents": "id zone_id title status severity workspace_mode version",
            "repair_records": "id work_order_id performed_at description environment",
            "verification_records": "id repair_id outcome comparability reviewed_at reason",
            "audit_logs": "id action resource_type resource_id occurred_at request_id",
        }
        if table in fields:
            return {k: row[k] for k in fields[table].split()}
        if table == "evidence_assessments":
            ids = query(
                self.c,
                "SELECT evidence_record_id FROM assessment_evidence WHERE assessment_id=:i ORDER BY evidence_record_id",
                i=row["id"],
            )
            return {
                **{
                    k: row[k]
                    for k in (
                        "id",
                        "kind",
                        "disposition",
                        "reason_codes",
                        "explanation",
                        "workspace_mode",
                    )
                },
                "evidence_record_ids": [x["evidence_record_id"] for x in ids],
            }
        if table == "incident_events":
            incident = self.row("incidents", row["incident_id"])
            return {
                "id": row["id"],
                "event_type": row["event_type"],
                "occurred_at": row["occurred_at"],
                "actor_display": "Authorized utility member" if row["actor_id"] else "System",
                "safe_description": row["reason"],
                "workspace_mode": incident["workspace_mode"],
            }
        if table in {"network_junctions", "pipe_segments"}:
            geo = one(
                self.c,
                f"SELECT ST_AsGeoJSON({'point' if table == 'network_junctions' else 'geometry'})::json AS geometry FROM {table} WHERE id=:i",
                i=row["id"],
            )["geometry"]
            keys = (
                "id zone_id external_ref topology_quality"
                if table == "network_junctions"
                else "id zone_id from_junction_id to_junction_id material diameter_mm topology_quality"
            )
            result = {**{k: row[k] for k in keys.split()}, "geometry": geo}
            if table == "pipe_segments":
                result["path_length_m"] = row["surveyed_length_m"]
            return result
        return receipt(row)

    def page(self, table, parameters, extra_sql="", extra_values=None):
        c = self.c
        filters = dict(parameters)
        try:
            limit = int(filters.pop("limit", 50))
            require(1 <= limit <= 100)
        except (ValueError, TypeError):
            raise Problem(422, "INVALID_FILTER", "Invalid page limit")
        cursor = filters.pop("cursor", None)
        clauses = ["organization_id=:org"]
        values = {"org": self.organization_id, **(extra_values or {})}
        if extra_sql:
            clauses.append(extra_sql)
        time_keys = {"from_time", "to_time"} & set(filters)
        if time_keys:
            require(
                time_keys == {"from_time", "to_time"},
                422,
                "INVALID_TIME_RANGE",
                "Supply both time boundaries",
            )
            try:
                start = datetime.fromisoformat(filters["from_time"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(filters["to_time"].replace("Z", "+00:00"))
                require(
                    start.tzinfo and end.tzinfo and 0 < (end - start).total_seconds() <= 31 * 86400
                )
            except (ValueError, TypeError):
                raise Problem(
                    422, "INVALID_TIME_RANGE", "Use an ordered UTC range of at most 31 days"
                )
        scope = hashlib.sha256(
            json.dumps(
                [
                    str(self.organization_id),
                    str(self.member_id),
                    sorted(self.roles),
                    self.op["path"],
                    filters,
                ],
                sort_keys=True,
            ).encode()
        ).hexdigest()[:24]
        stamp = now()
        if cursor:
            try:
                payload, signature = cursor.split(".")
                expected = hmac.new(
                    self.auth.app.state.settings.hmac_key.get_secret_value().encode(),
                    payload.encode(),
                    "sha256",
                ).hexdigest()
                require(hmac.compare_digest(expected, signature))
                decoded = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
                require(decoded["scope"] == scope)
                stamp = datetime.fromisoformat(decoded["as_of"])
                values.update(
                    after_time=datetime.fromisoformat(decoded["time"]), after_id=UUID(decoded["id"])
                )
                clauses.append("(created_at,id)<(:after_time,:after_id)")
            except Exception:
                raise Problem(422, "INVALID_CURSOR", "Cursor is invalid for the current scope")
        allowed = {
            p["name"]: p
            for p in __import__("hydro.contracts", fromlist=["DESIGN"])
            .DESIGN["paths"][self.op["path"]][self.op["method"]]
            .get("parameters", [])
            if p["in"] == "query"
        }
        for key, value in filters.items():
            require(key in allowed, 422, "INVALID_FILTER", "Unknown or unauthorized filter")
            if key in {"from_time", "to_time", "due_before"}:
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    require(value.tzinfo)
                except (ValueError, TypeError):
                    raise Problem(422, "INVALID_TIME_RANGE", "Timezone-aware timestamp required")
                column = "due_at" if key == "due_before" else "occurred_at"
                clauses.append(column + (">=:from_time" if key == "from_time" else "<:" + key))
                values[key] = value
                continue
            if key == "action":
                require(0 < len(value) <= 100)
                clauses.append("action=:action")
                values[key] = value
                continue
            if key == "incident_id":
                self.row("incidents", value)
                clauses.append(
                    "id IN (SELECT assessment_id FROM incident_evidence WHERE incident_id=:incident_filter)"
                )
                values["incident_filter"] = value
                continue
            if key == "assignee_id":
                try:
                    value = UUID(value)
                except ValueError:
                    raise Problem(422, "INVALID_FILTER", "Invalid assignee identifier")
                self.row("organization_memberships", value)
                require(
                    self.roles.intersection({"ENGINEER", "SUPERVISOR"}) or value == self.member_id,
                    403,
                    "FORBIDDEN",
                    "Assignee filter exceeds current scope",
                )
                clauses.append("assignee_id=:assignee_filter")
                values["assignee_filter"] = value
                continue
            if key == "bbox":
                import math

                try:
                    west, south, east, north = map(float, value.split(","))
                    require(
                        all(math.isfinite(v) for v in [west, south, east, north])
                        and -180 <= west < east <= 180
                        and -90 <= south < north <= 90
                    )
                except (ValueError, TypeError):
                    raise Problem(422, "INVALID_BBOX", "Use west,south,east,north in WGS84 bounds")
                column = {
                    "water_zones": "boundary",
                    "network_junctions": "point",
                    "pipe_segments": "geometry",
                }[table]
                clauses.append(
                    f"ST_Intersects({column},ST_MakeEnvelope(:west,:south,:east,:north,4326))"
                )
                values.update(west=west, south=south, east=east, north=north)
                continue
            if key in {
                "status",
                "severity",
                "zone_id",
                "workspace_mode",
                "priority",
                "outcome",
                "kind",
                "disposition",
            }:
                from .contracts import DESIGN

                enum_name = {
                    "incidents": "IncidentStatus",
                    "work_orders": "WorkOrderStatus",
                    "citizen_complaints": "ComplaintStatus",
                }.get(table)
                choices = (
                    DESIGN["components"]["schemas"].get(enum_name, {}).get("enum", [])
                    if key == "status"
                    else {
                        "workspace_mode": ["OPERATIONAL"],
                        "severity": ["LOW", "MEDIUM", "HIGH", "URGENT"],
                        "priority": ["LOW", "MEDIUM", "HIGH", "URGENT"],
                    }.get(key)
                )
                if choices:
                    require(value in choices, 422, "INVALID_FILTER", "Unsupported filter value")
                if key.endswith("_id"):
                    try:
                        value = UUID(value)
                    except ValueError:
                        raise Problem(422, "INVALID_FILTER", "Invalid identifier filter")
                    self.row("water_zones", value)
                column = "id" if table == "water_zones" and key == "zone_id" else key
                clauses.append(f"{column}=:{key}")
                values[key] = value
            else:
                raise Problem(422, "DEFERRED_FILTER", "This filter is not enabled in M03")
        if (
            table in {"incidents", "work_orders", "evidence_assessments"}
            and "workspace_mode" not in filters
        ):
            clauses.append("workspace_mode='OPERATIONAL'")
        values.update(as_of=stamp, n=limit + 1)
        rows = query(
            c,
            f"SELECT * FROM {table} WHERE {' AND '.join(clauses)} AND created_at<=:as_of ORDER BY created_at DESC,id DESC LIMIT :n",
            **values,
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
            signature = hmac.new(
                self.auth.app.state.settings.hmac_key.get_secret_value().encode(),
                payload.encode(),
                "sha256",
            ).hexdigest()
            next_cursor = payload + "." + signature
        return {
            "items": [self.view(table, x) for x in rows[:limit]],
            "next_cursor": next_cursor,
            "as_of": stamp,
        }
