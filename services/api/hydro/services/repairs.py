"""RepairService persistent operations."""

from datetime import timedelta

from ..errors import require
from ..repository import change, insert
from ..security import now
from .base import Service


class RepairService(Service):
    def run(self, b, parent=None):
        s, c = self.s, self.c
        method = s.op["method"]
        if method == "get":
            return s.page(
                "repair_records",
                dict(s.auth.request.query_params),
                "work_order_id=:w",
                {"w": parent["id"]},
            )
        require(
            parent["status"] in {"IN_PROGRESS", "BLOCKED"},
            409,
            "INVALID_STATE",
            "Record repair during current assigned investigation",
        )
        require(
            not b["attachment_ids"],
            422,
            "ATTACHMENTS_DISABLED",
            "Attachments require the future validated upload lifecycle",
        )
        from datetime import datetime

        require(
            datetime.fromisoformat(b["performed_at"].replace("Z", "+00:00"))
            <= now() + timedelta(minutes=5),
            422,
            "INVALID_TIME",
            "Performed time is in the future",
        )
        row = insert(
            c,
            "repair_records",
            organization_id=self.o,
            work_order_id=parent["id"],
            recorded_by_id=self.a,
            performed_at=b["performed_at"],
            description=b["description"],
            materials=b["materials"],
            environment="MANUAL",
        )
        self.evidence(repair_id=row["id"], record_type="REPAIR_RECEIPT")
        change(c, "work_orders", parent["id"], status=parent["status"])
        return self.save("repair_records", row)
