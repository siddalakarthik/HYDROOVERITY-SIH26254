"""ComplaintService persistent operations and permission-aware projections."""

from uuid import uuid4

from ..db import one
from ..errors import require
from ..repository import change, insert
from ..security import now
from .base import Service


class ComplaintService(Service):
    def run(self, b, parent):
        s, c = self.s, self.c
        method = s.op["method"]
        path = s.op["path"]
        if method == "get":
            return (
                s.view("citizen_complaints", parent)
                if parent
                else s.page(
                    "citizen_complaints",
                    dict(s.auth.request.query_params),
                    "" if "SUPERVISOR" in s.roles else "reporter_id=:member",
                    {"member": self.a},
                )
            )
        require(
            not b.get("attachment_ids"),
            422,
            "ATTACHMENTS_DISABLED",
            "Photo intake is disabled until its secure lifecycle exists",
        )
        if not parent:
            org = one(c, "SELECT public_reporting_enabled FROM organizations WHERE id=:o", o=self.o)
            require(
                org["public_reporting_enabled"],
                403,
                "REPORTING_DISABLED",
                "Utility reporting is disabled",
            )
            require(
                one(
                    c,
                    "SELECT count(*) AS n FROM citizen_complaints WHERE reporter_id=:m AND created_at>now()-interval '1 day'",
                    m=self.a,
                )["n"]
                < 10,
                429,
                "RATE_LIMITED",
                "Daily complaint allowance reached",
            )
            row = insert(
                c,
                "citizen_complaints",
                organization_id=self.o,
                reporter_id=self.a,
                tracking_number="HYD-" + uuid4().hex[:20].upper(),
                category=b["category"],
                description=b["description"],
                coarse_area=b["coarse_area"],
                status="RECEIVED",
                consent_at=now() if b["photo_consent"] else None,
            )
            insert(
                c,
                "complaint_status_events",
                organization_id=self.o,
                complaint_id=row["id"],
                actor_id=self.a,
                status="RECEIVED",
                public_message="Report received for review",
                occurred_at=now(),
            )
            self.evidence(complaint_id=row["id"], record_type="CITIZEN_REPORT")
            return self.save("citizen_complaints", row)
        if path.endswith("/follow-ups"):
            require(
                parent["status"] not in {"RESOLVED", "CLOSED_NO_ACTION"},
                409,
                "CLOSED_REPORT",
                "Closed reports require a new report",
            )
            self.evidence(
                complaint_id=parent["id"],
                record_type="COMPLAINT_FOLLOWUP",
            )
            row = insert(
                c,
                "complaint_status_events",
                organization_id=self.o,
                complaint_id=parent["id"],
                actor_id=self.a,
                status=parent["status"],
                public_message=b["description"],
                occurred_at=now(),
            )
            change(c, "citizen_complaints", parent["id"], status=parent["status"])
            return self.save("complaint_status_events", row)
        if b["incident_id"]:
            incident = s.row("incidents", b["incident_id"])
            require(
                incident["workspace_mode"] == "OPERATIONAL",
                422,
                "MODE_CONFLICT",
                "Operational report requires operational incident",
            )
            self.event(incident, "COMPLAINT_REVIEW", b["internal_reason"])
        change(
            c,
            "citizen_complaints",
            parent["id"],
            status=b["public_status"],
            incident_id=b["incident_id"],
        )
        row = insert(
            c,
            "complaint_status_events",
            organization_id=self.o,
            complaint_id=parent["id"],
            actor_id=self.a,
            status=b["public_status"],
            public_message=b["public_message"],
            internal_reason=b["internal_reason"],
            occurred_at=now(),
        )
        return self.save("complaint_status_events", row)
