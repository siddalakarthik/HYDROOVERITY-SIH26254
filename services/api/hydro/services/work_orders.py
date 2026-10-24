"""WorkOrderService persistent operations and permission-aware projections."""

from datetime import timedelta
from uuid import uuid4

from ..db import one
from ..errors import require
from ..repository import change, insert
from ..security import now
from .base import Service

WORK_EDGES = {
    "CREATED": {"ASSIGNED"},
    "ASSIGNED": {"ACCEPTED"},
    "ACCEPTED": {"IN_PROGRESS"},
    "IN_PROGRESS": {"BLOCKED", "SUBMITTED_FOR_REVIEW"},
    "BLOCKED": {"IN_PROGRESS"},
    "SUBMITTED_FOR_REVIEW": {"COMPLETED", "IN_PROGRESS"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


class WorkOrderService(Service):
    def run(self, b, parent):
        s, c = self.s, self.c
        path = s.op["path"]
        method = s.op["method"]
        if method == "get":
            if path.endswith("/brief"):
                return {
                    "work_order": s.view("work_orders", parent),
                    "approximate_site": "Refer to authorized visit instructions",
                    "safe_evidence_summary": "Manual investigation; no validated sensor result supplied",
                    "safety_instructions": [
                        "No infrastructure actuation is authorized by this software"
                    ],
                    "lease_expires_at": now() + timedelta(minutes=15),
                }
            return (
                s.view("work_orders", parent)
                if parent
                else s.page(
                    "work_orders",
                    dict(s.auth.request.query_params),
                    ""
                    if s.roles.intersection({"ENGINEER", "SUPERVISOR"})
                    else "assignee_id=:member",
                    {"member": self.a},
                )
            )
        if parent is None:
            incident = s.row("incidents", b["incident_id"], True)
            require(
                incident["status"]
                in {"ACCEPTED", "IN_PROGRESS", "REOPENED", "INVESTIGATION_REQUIRED"},
                409,
                "TRIAGE_REQUIRED",
                "Review incident before ordering work",
            )
            row = insert(
                c,
                "work_orders",
                organization_id=self.o,
                incident_id=incident["id"],
                status="CREATED",
                priority=b["priority"],
                instructions=b["instructions"],
                assignment_version=1,
                workspace_mode=incident["workspace_mode"],
                task_purpose=b.get("task_purpose", "REPAIR"),
            )
            return self.save("work_orders", row)
        require(
            parent["status"] not in {"COMPLETED", "CANCELLED"},
            409,
            "FINAL_WORK",
            "Final work history cannot be modified",
        )
        from .scheduling_guards import guard_work_change

        guard_work_change(s, parent, b)
        if path.endswith("/assignment"):
            member = s.row("organization_memberships", b["assignee_membership_id"], True)
            tech = one(
                c,
                "SELECT a.id FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE a.membership_id=:m AND a.revoked_at IS NULL AND r.code='TECHNICIAN' FOR SHARE OF a",
                m=member["id"],
            )
            require(
                member["status"] == "ACTIVE" and tech,
                422,
                "INVALID_ASSIGNEE",
                "Assignee must be an active technician",
            )
            row = change(
                c,
                "work_orders",
                parent["id"],
                assignee_id=member["id"],
                due_at=b["due_at"],
                status="ASSIGNED",
                assignment_version=parent["assignment_version"] + 1,
            )
            insert(
                c,
                "work_order_actions",
                organization_id=self.o,
                work_order_id=parent["id"],
                actor_id=self.a,
                action_type="ASSIGNMENT",
                note=b["reason"],
                materials=[],
                operation_id=uuid4(),
                observed_at=now(),
                received_at=now(),
                base_version=parent["version"],
            )
            return self.save("work_orders", row)
        if path.endswith("/actions"):
            require(
                b["assignment_version"] == parent["assignment_version"],
                409,
                "ASSIGNMENT_CHANGED",
                "Assignment changed; refetch current task",
            )
            require(
                b["base_version"] == parent["version"],
                412,
                "VERSION_CONFLICT",
                "Task changed; refetch before recording",
            )
            require(
                parent["status"] in {"ACCEPTED", "IN_PROGRESS", "BLOCKED"},
                409,
                "INVALID_STATE",
                "Accept assigned work before recording actions",
            )
            require(
                not b["attachment_ids"], 422, "ATTACHMENTS_DISABLED", "Attachments are disabled"
            )
            from datetime import datetime

            require(
                datetime.fromisoformat(b["observed_at"].replace("Z", "+00:00"))
                <= now() + timedelta(minutes=5),
                422,
                "INVALID_TIME",
                "Observed time is in the future",
            )
            row = insert(
                c,
                "work_order_actions",
                organization_id=self.o,
                work_order_id=parent["id"],
                actor_id=self.a,
                action_type="NOTE",
                note=b["note"],
                materials=b["materials"],
                operation_id=b["operation_id"],
                observed_at=b["observed_at"],
                received_at=now(),
                base_version=b["base_version"],
            )
            self.evidence(manual_actor_id=self.a, manual_note=b["note"], record_type="WORKER_NOTE")
            change(c, "work_orders", parent["id"], status=parent["status"])
            return self.save("work_order_actions", row)
        target = b["target"]
        if "SUPERVISOR" in s.roles and target in {"COMPLETED", "CANCELLED"}:
            require(
                target == "CANCELLED" or parent["status"] == "SUBMITTED_FOR_REVIEW",
                409,
                "INVALID_TRANSITION",
                "Review submission is required",
            )
        elif (
            "SUPERVISOR" in s.roles
            and parent["status"] == "SUBMITTED_FOR_REVIEW"
            and target == "IN_PROGRESS"
        ):
            pass
        else:
            require(
                "TECHNICIAN" in s.roles and parent["assignee_id"] == self.a,
                403,
                "FORBIDDEN",
                "Current assigned technician required",
            )
            require(
                target in WORK_EDGES[parent["status"]]
                and target not in {"COMPLETED", "CANCELLED", "ASSIGNED"},
                409,
                "INVALID_TRANSITION",
                "Technician transition is not allowed",
            )
        if target == "SUBMITTED_FOR_REVIEW":
            investigation = parent["task_purpose"] != "REPAIR"
            require(
                one(
                    c,
                    (
                        "SELECT id FROM work_investigation_findings WHERE work_order_id=:w AND assignment_version=:av LIMIT 1"
                        if investigation
                        else "SELECT id FROM repair_records WHERE work_order_id=:w LIMIT 1"
                    ),
                    w=parent["id"],
                    av=parent["assignment_version"],
                ),
                409,
                "FINDINGS_REQUIRED" if investigation else "REPAIR_REQUIRED",
                "Current-assignment findings required before submission"
                if investigation
                else "Repair receipt required before submission",
            )
        row = change(c, "work_orders", parent["id"], status=target)
        insert(
            c,
            "work_order_actions",
            organization_id=self.o,
            work_order_id=parent["id"],
            actor_id=self.a,
            action_type="TRANSITION_" + target,
            note=b["reason"],
            materials=[],
            operation_id=uuid4(),
            observed_at=now(),
            received_at=now(),
            base_version=parent["version"],
        )
        return self.save("work_orders", row)
