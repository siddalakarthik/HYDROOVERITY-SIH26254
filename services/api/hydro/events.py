"""Minimal safe audit/outbox records in the caller's business transaction."""

import json

from .db import execute, one


def record(
    c, organization_id, actor_id, action, table, resource_id, request_id, permission, reason=None
):
    metadata = {"governance_reason": reason} if reason is not None else {}
    execute(
        c,
        "INSERT INTO audit_logs(organization_id,actor_id,action,resource_type,resource_id,request_id,safe_metadata,occurred_at) VALUES(:o,:a,:x,:t,:i,:q,CAST(:metadata AS jsonb),now())",
        o=organization_id,
        a=actor_id,
        x=action,
        t=table,
        i=resource_id,
        q=request_id,
        metadata=json.dumps(metadata),
    )
    event = one(
        c,
        "INSERT INTO domain_events(organization_id,event_type,resource_type,resource_id,workspace_mode,minimum_permission,occurred_at,safe_summary) VALUES(:o,:x,:t,:i,'OPERATIONAL',:p,now(),'{}') RETURNING id",
        o=organization_id,
        x=action,
        t=table,
        i=resource_id,
        p=permission,
    )

    from .notification_worker import enqueue

    enqueue(c, organization_id, event["id"], table, resource_id, action)
