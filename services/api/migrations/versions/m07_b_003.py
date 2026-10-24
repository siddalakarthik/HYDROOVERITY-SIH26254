"""Narrow dispatch identity discovery and resident scheduler scope."""

from alembic import op

revision = "m07_b_003"
down_revision = "m07_b_002"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE appointments ADD CONSTRAINT dispatch_appointment_binding UNIQUE(organization_id,id,work_order_id,subject_id)"
    )
    op.execute(
        "ALTER TABLE dispatch_allocations ADD CONSTRAINT dispatch_allocation_binding FOREIGN KEY(organization_id,appointment_id,work_order_id,subject_id) REFERENCES appointments(organization_id,id,work_order_id,subject_id)"
    )
    op.execute("""
    CREATE FUNCTION hydro_dispatch_roster() RETURNS TABLE(id uuid,display_name text,status text,version bigint,enrollment_available boolean)
    LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
     SELECT m.id,left(u.display_name,100),m.status,m.version,
       NOT EXISTS(SELECT 1 FROM public.dispatch_calendar_subjects s WHERE s.user_id=m.user_id AND s.exclusive_dispatch_organization_id<>m.organization_id)
     FROM public.organization_memberships m JOIN public.users u ON u.id=m.user_id
     WHERE m.organization_id::text=current_setting('hydro.organization_id',true)
     AND public.hydro_m07_role(ARRAY['ADMIN','SUPERVISOR'])
     AND (EXISTS(SELECT 1 FROM public.role_assignments a JOIN public.roles r ON r.id=a.role_id WHERE a.membership_id=m.id AND a.revoked_at IS NULL AND r.code='TECHNICIAN')
       OR EXISTS(SELECT 1 FROM public.dispatch_technician_profiles p WHERE p.membership_id=m.id))
    $$;
    REVOKE ALL ON FUNCTION hydro_dispatch_roster() FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION hydro_dispatch_roster() TO hydro_app;

    CREATE FUNCTION hydro_dispatch_resident_scope() RETURNS boolean
    LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
      SELECT public.hydro_m07_role(ARRAY['CITIZEN']) AND public.hydro_dispatch_service_visible(nullif(current_setting('hydro.dispatch_service',true),'')::uuid)
    $$;
    REVOKE ALL ON FUNCTION hydro_dispatch_resident_scope() FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION hydro_dispatch_resident_scope() TO hydro_app;
    """)
    for table in (
        "dispatch_technician_profiles",
        "dispatch_allocations",
        "dispatch_policy",
        "dispatch_shifts",
    ):
        op.execute(f"DROP POLICY resident_scheduler_read ON {table}")
        op.execute(
            f"CREATE POLICY resident_scheduler_read ON {table} FOR SELECT USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_dispatch_resident_scope())"
        )
    for table in ("dispatch_technician_profiles", "dispatch_allocations"):
        op.execute(f"DROP POLICY resident_scheduler_write ON {table}")
        op.execute(
            f"CREATE POLICY resident_scheduler_write ON {table} FOR ALL USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_dispatch_resident_scope()) WITH CHECK(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_dispatch_resident_scope())"
        )
    op.execute("""
    CREATE FUNCTION hydro_dispatch_visit_update(visit uuid) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
    DECLARE a public.appointments; s public.service_requests; event uuid:=gen_random_uuid(); actor uuid; message text;
    BEGIN
      SELECT * INTO a FROM public.appointments WHERE id=visit AND organization_id::text=current_setting('hydro.organization_id',true);
      IF a.id IS NULL OR NOT public.hydro_m07_role(ARRAY['TECHNICIAN']) OR NOT public.hydro_m07_own(a.assignee_id)
      THEN RAISE EXCEPTION 'forbidden visit' USING ERRCODE='42501'; END IF;
      IF NOT EXISTS(SELECT 1 FROM public.work_orders w WHERE w.id=a.work_order_id AND w.assignee_id=a.assignee_id AND w.assignment_version=a.assignment_version)
      THEN RAISE EXCEPTION 'assignment changed' USING ERRCODE='23514'; END IF;
      actor:=a.assignee_id;
      UPDATE public.dispatch_technician_profiles SET calendar_version=calendar_version+1,version=version+1,updated_at=now() WHERE membership_id=a.assignee_id AND organization_id=a.organization_id;
      IF a.status NOT IN ('CONFIRMED','CHECKED_IN') THEN
       UPDATE public.dispatch_allocations SET active=false,released_at=now(),version=version+1,updated_at=now() WHERE appointment_id=a.id AND active;
      END IF;
      message:=CASE a.status WHEN 'CHECKED_IN' THEN 'The assigned technician recorded check-in.' WHEN 'VISIT_FINISHED' THEN 'The visit was recorded as finished. This does not establish repair completion or scientific verification.' WHEN 'NO_ACCESS' THEN 'The technician reported that the visit could not proceed.' WHEN 'ABORTED' THEN 'The technician reported that the visit was stopped.' ELSE 'A visit update was recorded for utility review.' END;
      UPDATE public.service_requests SET version=version+1,updated_at=now() WHERE id=a.request_id RETURNING * INTO s;
      INSERT INTO public.service_request_events(id,organization_id,request_id,sequence,event_kind,actor_id,internal_reason,resource_type,resource_id,previous_version,resulting_version)
      VALUES(event,s.organization_id,s.id,s.version,'VISIT_EVENT',actor,'Visit event recorded; see restricted appointment history','SERVICE',s.id,s.version-1,s.version);
      INSERT INTO public.service_public_updates(organization_id,request_id,sequence,origin_event_id,actor_id,event_kind,message)
      VALUES(s.organization_id,s.id,s.version,event,actor,'PROGRESS',message);
    END $$;
    REVOKE ALL ON FUNCTION hydro_dispatch_visit_update(uuid) FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION hydro_dispatch_visit_update(uuid) TO hydro_app;
    """)


def downgrade():
    op.execute(
        "ALTER TABLE dispatch_allocations DROP CONSTRAINT IF EXISTS dispatch_allocation_binding"
    )
    op.execute("ALTER TABLE appointments DROP CONSTRAINT IF EXISTS dispatch_appointment_binding")
    op.execute("DROP FUNCTION hydro_dispatch_visit_update(uuid),hydro_dispatch_roster()")
    for table in (
        "dispatch_technician_profiles",
        "dispatch_allocations",
        "dispatch_policy",
        "dispatch_shifts",
    ):
        op.execute(f"DROP POLICY resident_scheduler_read ON {table}")
        op.execute(
            f"CREATE POLICY resident_scheduler_read ON {table} FOR SELECT USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['CITIZEN']))"
        )
    for table in ("dispatch_technician_profiles", "dispatch_allocations"):
        op.execute(f"DROP POLICY resident_scheduler_write ON {table}")
        op.execute(
            f"CREATE POLICY resident_scheduler_write ON {table} FOR ALL USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['CITIZEN'])) WITH CHECK(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['CITIZEN']))"
        )
    op.execute("DROP FUNCTION hydro_dispatch_resident_scope()")
