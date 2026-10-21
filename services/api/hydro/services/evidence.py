"""EvidenceService persistent operations."""

from ..errors import require
from ..repository import insert
from .base import Service


class EvidenceService(Service):
    def run(self, b, parent=None):
        s, c = self.s, self.c
        method = s.op["method"]
        if method == "get":
            return (
                s.view("evidence_assessments", parent)
                if parent
                else s.page("evidence_assessments", dict(s.auth.request.query_params))
            )
        require(
            b["evidence_record_ids"],
            422,
            "EVIDENCE_REQUIRED",
            "Assessment requires authorized evidence",
        )
        require(
            b["disposition"] != "QUALIFIED_CANDIDATE" and b["kind"] != "ACOUSTIC_CANDIDATE",
            422,
            "SCIENTIFIC_QUALIFICATION_DISABLED",
            "Manual evidence cannot qualify an acoustic candidate",
        )
        row = insert(
            c,
            "evidence_assessments",
            organization_id=self.o,
            kind=b["kind"],
            disposition=b["disposition"],
            reason_codes=["MANUAL_EVIDENCE_ONLY"],
            explanation=b["reason"],
            reviewer_id=self.a,
            workspace_mode="OPERATIONAL",
        )
        for eid in set(b["evidence_record_ids"]):
            insert(
                c,
                "assessment_evidence",
                organization_id=self.o,
                assessment_id=row["id"],
                evidence_record_id=eid,
            )
        return self.save("evidence_assessments", row)
