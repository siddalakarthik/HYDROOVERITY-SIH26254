"""VerificationService persistent operations."""

from ..db import one
from ..errors import require
from ..repository import insert
from ..security import now
from .base import Service


class VerificationService(Service):
    def run(self, b, parent=None):
        s, c = self.s, self.c
        method = s.op["method"]
        if method == "get":
            return s.page(
                "verification_records",
                dict(s.auth.request.query_params),
                "repair_id=:r",
                {"r": parent["id"]},
            )
        require(
            parent["recorded_by_id"] != self.a,
            403,
            "INDEPENDENT_REVIEW_REQUIRED",
            "Repair actor cannot approve their own outcome",
        )
        require(
            b["outcome"] == "NOT_VERIFIABLE",
            422,
            "COMPARABLE_EVIDENCE_UNAVAILABLE",
            "M03 manual evidence cannot establish scientific PASSED or FAILED",
        )
        require(
            not any(v for k, v in b["comparability"].items() if k != "limitations"),
            422,
            "COMPARABLE_EVIDENCE_UNAVAILABLE",
            "Manual receipts cannot attest measured comparability",
        )
        require(
            b["comparability"]["limitations"].strip(),
            422,
            "LIMITATIONS_REQUIRED",
            "Explain missing measurement comparability",
        )
        previous = one(
            c,
            "SELECT id FROM verification_records WHERE repair_id=:r ORDER BY created_at DESC,id DESC LIMIT 1",
            r=parent["id"],
        )
        row = insert(
            c,
            "verification_records",
            organization_id=self.o,
            repair_id=parent["id"],
            reviewer_id=self.a,
            outcome="NOT_VERIFIABLE",
            comparability=b["comparability"],
            reason=b["reason"],
            reviewed_at=now(),
            supersedes_id=previous["id"] if previous else None,
        )
        for phase, key in [
            ("BEFORE", "before_evidence_record_ids"),
            ("AFTER", "after_evidence_record_ids"),
        ]:
            for eid in set(b[key]):
                insert(
                    c,
                    "verification_evidence",
                    organization_id=self.o,
                    verification_id=row["id"],
                    evidence_record_id=eid,
                    phase=phase,
                )
        return self.save("verification_records", row)
