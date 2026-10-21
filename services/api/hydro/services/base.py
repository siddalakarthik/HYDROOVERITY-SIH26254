"""Shared transaction-bound operational helpers; no network or commit here."""

from uuid import uuid4

from ..events import record
from ..repository import insert
from ..security import now


class Service:
    def __init__(self, scope):
        self.s = scope
        self.c = scope.c
        self.o = scope.organization_id
        self.a = scope.member_id
        self.table = None
        self.result = None
        self.governance_reason = None

    def save(self, table, row, action=None):
        self.table, self.result = table, row
        record(
            self.c,
            self.o,
            self.a,
            action or self.s.op["id"],
            table,
            row["id"],
            self.s.auth.request.state.request_id,
            self.s.op["permission"],
            reason=self.governance_reason,
        )
        return self.s.view(table, row)

    def evidence(self, **source):
        return insert(
            self.c, "evidence_records", organization_id=self.o, environment="MANUAL", **source
        )

    def event(self, row, kind, reason, previous=None):
        insert(
            self.c,
            "incident_events",
            organization_id=self.o,
            incident_id=row["id"],
            actor_id=self.a,
            event_type=kind,
            from_status=previous,
            to_status=row["status"],
            reason=reason,
            operation_id=uuid4(),
            occurred_at=now(),
        )
