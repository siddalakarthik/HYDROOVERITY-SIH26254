-- Narrow global-identity discovery. The API first authenticates the opaque session.
CREATE FUNCTION hydro_memberships() RETURNS TABLE
 (id uuid, organization_id uuid, organization_name text, roles jsonb, status text)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
 SELECT m.id,m.organization_id,o.name,
 coalesce((SELECT jsonb_agg(r.code ORDER BY r.code) FROM public.role_assignments a
 JOIN public.roles r ON r.id=a.role_id WHERE a.membership_id=m.id
 AND a.organization_id=m.organization_id AND a.revoked_at IS NULL),'[]'::jsonb),m.status
 FROM public.organization_memberships m JOIN public.organizations o ON o.id=m.organization_id
 WHERE m.user_id::text=current_setting('hydro.user_id',true)
$$;
REVOKE ALL ON FUNCTION hydro_memberships() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_memberships() TO hydro_app;

CREATE FUNCTION hydro_invitation(verifier bytea) RETURNS TABLE(id uuid,organization_id uuid)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
 SELECT i.id,i.organization_id FROM public.invitations i JOIN public.users u
 ON u.email_normalized=i.email_normalized WHERE u.id::text=current_setting('hydro.user_id',true)
 AND u.email_verified_at IS NOT NULL AND u.deactivated_at IS NULL
 AND i.token_hash=verifier AND i.accepted_at IS NULL AND i.expires_at>now()
$$;
REVOKE ALL ON FUNCTION hydro_invitation(bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_invitation(bytea) TO hydro_app;

-- Expired receipt cleanup is the only runtime deletion capability. Cannot delete live receipts.
CREATE FUNCTION hydro_expire_receipts() RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
 DELETE FROM public.idempotency_records WHERE expires_at<=now()
 AND organization_id::text=current_setting('hydro.organization_id',true)
$$;
REVOKE ALL ON FUNCTION hydro_expire_receipts() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_expire_receipts() TO hydro_app;

CREATE FUNCTION hydro_expire_sessions() RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
 DELETE FROM public.sessions WHERE absolute_expires_at<now()-interval '30 days'
$$;
REVOKE ALL ON FUNCTION hydro_expire_sessions() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_expire_sessions() TO hydro_app;

-- Reject history mutation even if an application code path accidentally attempts it.
CREATE FUNCTION hydro_history_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'append-only history' USING ERRCODE='42501'; END $$;
CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
CREATE TRIGGER immutable_incident_events BEFORE UPDATE OR DELETE ON incident_events
FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
CREATE TRIGGER immutable_worker_actions BEFORE UPDATE OR DELETE ON work_order_actions
FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
CREATE TRIGGER immutable_repairs BEFORE UPDATE OR DELETE ON repair_records
FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
CREATE TRIGGER immutable_verifications BEFORE UPDATE OR DELETE ON verification_records
FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
