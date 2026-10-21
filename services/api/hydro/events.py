"""Minimal safe audit/outbox records in the caller's business transaction."""
from .db import execute


def record(c, organization_id, actor_id, action, table, resource_id, request_id, permission):
    execute(c,"INSERT INTO audit_logs(organization_id,actor_id,action,resource_type,resource_id,request_id,safe_metadata,occurred_at) VALUES(:o,:a,:x,:t,:i,:q,'{}',now())",
            o=organization_id,a=actor_id,x=action,t=table,i=resource_id,q=request_id)
    execute(c,"INSERT INTO domain_events(organization_id,event_type,resource_type,resource_id,workspace_mode,minimum_permission,occurred_at,safe_summary) VALUES(:o,:x,:t,:i,'OPERATIONAL',:p,now(),'{}')",
            o=organization_id,x=action,t=table,i=resource_id,p=permission)
