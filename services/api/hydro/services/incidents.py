"""IncidentService persistent operations and permission-aware projections."""

from ..db import one
from ..errors import require
from ..repository import change, insert
from ..security import now
from .base import Service

INCIDENT_EDGES = {
    "NEW": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"INVESTIGATION_REQUIRED", "ACCEPTED", "DISMISSED"},
    "INVESTIGATION_REQUIRED": {"ACCEPTED", "DISMISSED"},
    "ACCEPTED": {"IN_PROGRESS"},
    "IN_PROGRESS": {"VERIFICATION_PENDING"},
    "VERIFICATION_PENDING": {"RESOLVED", "REOPENED", "NOT_VERIFIABLE"},
    "REOPENED": {"UNDER_REVIEW", "IN_PROGRESS"},
    "NOT_VERIFIABLE": {"UNDER_REVIEW"},
    "RESOLVED": {"REOPENED"},
    "DISMISSED": {"UNDER_REVIEW"},
}


class IncidentService(Service):
    def run(self, b, parent):
        s, c = self.s, self.c
        path = s.op["path"]
        method = s.op["method"]
        if method == "get":
            if path.endswith("/timeline"):
                return s.page(
                    "incident_events",
                    dict(s.auth.request.query_params),
                    "incident_id=:incident",
                    {"incident": parent["id"]},
                )
            return (
                s.view("incidents", parent)
                if parent
                else s.page("incidents", dict(s.auth.request.query_params))
            )
        if parent is None:
            require(
                b["workspace_mode"] == "OPERATIONAL" and b["simulation_run_id"] is None,
                422,
                "SIMULATION_DISABLED",
                "Simulation integration is deferred to M06",
            )
            row = insert(
                c,
                "incidents",
                organization_id=self.o,
                zone_id=b["zone_id"],
                status="NEW",
                severity=b["severity"],
                title=b["title"],
                workspace_mode="OPERATIONAL",
                owner_id=self.a,
            )
            for aid in set(b["assessment_ids"]):
                assessment = s.row("evidence_assessments", aid)
                require(
                    assessment["workspace_mode"] == "OPERATIONAL",
                    422,
                    "MODE_CONFLICT",
                    "Evidence mode mismatch",
                )
                insert(
                    c,
                    "incident_evidence",
                    organization_id=self.o,
                    incident_id=row["id"],
                    assessment_id=aid,
                )
            self.event(row, "CREATED", "Concern created for review")
            return self.save("incidents", row)
        if path.endswith("/links"):
            require(
                str(parent["id"]) != b["target_incident_id"],
                422,
                "SELF_LINK",
                "Incident cannot link to itself",
            )
            if b["relation"] == "DUPLICATE_OF":
                cycle = one(
                    c,
                    "WITH RECURSIVE chain(id) AS (SELECT CAST(:target AS uuid) UNION SELECT l.target_incident_id FROM incident_links l JOIN chain x ON l.source_incident_id=x.id WHERE l.relation='DUPLICATE_OF') SELECT id FROM chain WHERE id=:source LIMIT 1",
                    target=b["target_incident_id"],
                    source=parent["id"],
                )
                require(not cycle, 409, "REDIRECT_CYCLE", "Duplicate link would create a cycle")
            target = s.row("incidents", b["target_incident_id"])
            require(
                target["workspace_mode"] == parent["workspace_mode"],
                422,
                "MODE_CONFLICT",
                "Incident modes differ",
            )
            row = insert(
                c,
                "incident_links",
                organization_id=self.o,
                source_incident_id=parent["id"],
                target_incident_id=target["id"],
                relation=b["relation"],
                actor_id=self.a,
                reason=b["reason"],
            )
            return self.save("incident_links", row)
        target = b["target"]
        require(
            target in INCIDENT_EDGES[parent["status"]],
            409,
            "INVALID_TRANSITION",
            "Incident transition is not allowed",
        )
        if target == "IN_PROGRESS":
            require(
                one(
                    c,
                    "SELECT id FROM work_orders WHERE incident_id=:i AND assignee_id IS NOT NULL AND status NOT IN ('CREATED','CANCELLED') LIMIT 1",
                    i=parent["id"],
                ),
                409,
                "WORK_REQUIRED",
                "Assigned work required",
            )
        if target == "VERIFICATION_PENDING":
            require(
                one(
                    c,
                    "SELECT r.id FROM repair_records r JOIN work_orders w ON w.id=r.work_order_id WHERE w.incident_id=:i AND w.status IN ('SUBMITTED_FOR_REVIEW','COMPLETED') LIMIT 1",
                    i=parent["id"],
                ),
                409,
                "REPAIR_REQUIRED",
                "Submitted repair receipt required",
            )
        if (
            target in {"RESOLVED", "REOPENED", "NOT_VERIFIABLE"}
            and parent["status"] == "VERIFICATION_PENDING"
        ):
            expected = {
                "RESOLVED": "VERIFICATION_PASSED",
                "REOPENED": "VERIFICATION_FAILED",
                "NOT_VERIFIABLE": "NOT_VERIFIABLE",
            }[target]
            latest = one(
                c,
                "SELECT v.outcome FROM verification_records v JOIN repair_records r ON r.id=v.repair_id JOIN work_orders w ON w.id=r.work_order_id WHERE w.incident_id=:i ORDER BY v.created_at DESC,v.id DESC LIMIT 1",
                i=parent["id"],
            )
            require(
                latest and latest["outcome"] == expected,
                409,
                "VERIFICATION_REQUIRED",
                "Authorized matching verification is required",
            )
        row = change(
            c,
            "incidents",
            parent["id"],
            status=target,
            resolved_at=now() if target == "RESOLVED" else None,
        )
        self.event(row, "TRANSITION", b["reason"], parent["status"])
        return self.save("incidents", row)
