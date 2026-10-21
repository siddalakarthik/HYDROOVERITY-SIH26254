"""Small internal DML helpers: identifiers originate in reviewed service source."""

import json
import re

from .db import one

TABLES = set(
    "organizations users organization_memberships roles permissions role_permissions role_assignments sessions invitations account_recovery_tokens audit_logs idempotency_records domain_events water_zones citizen_complaints complaint_status_events incidents incident_events incident_links incident_evidence work_orders work_order_actions repair_records verification_records verification_evidence evidence_records evidence_assessments assessment_evidence network_junctions pipe_segments".split()
)
JSON_FIELDS = {
    "retention_policy",
    "demand_accounting",
    "materials",
    "comparability",
    "safe_metadata",
    "safe_summary",
}


def insert(c, table, **values):
    assert table in TABLES and all(re.fullmatch(r"[a-z_]+", k) for k in values)
    expressions = [f"CAST(:{k} AS jsonb)" if k in JSON_FIELDS else f":{k}" for k in values]
    params = {k: json.dumps(v) if k in JSON_FIELDS else v for k, v in values.items()}
    return one(
        c,
        f"INSERT INTO {table} ({','.join(values)}) VALUES ({','.join(expressions)}) RETURNING *",
        **params,
    )


def change(c, table, resource_id, **values):
    assert table in TABLES and all(re.fullmatch(r"[a-z_]+", k) for k in values)
    assignments = [
        k + "=" + (f"CAST(:{k} AS jsonb)" if k in JSON_FIELDS else f":{k}") for k in values
    ]
    params = {k: json.dumps(v) if k in JSON_FIELDS else v for k, v in values.items()}
    return one(
        c,
        f"UPDATE {table} SET {','.join(assignments)},version=version+1,updated_at=now() WHERE id=:row_id RETURNING *",
        row_id=resource_id,
        **params,
    )
