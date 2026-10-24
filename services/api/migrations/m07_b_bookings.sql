CREATE TABLE appointment_windows(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id), profile_id uuid NOT NULL,
 arrival_start timestamptz NOT NULL, arrival_end timestamptz NOT NULL,
 service_duration_minutes integer NOT NULL CHECK(service_duration_minutes BETWEEN 1 AND 480),
 before_buffer_minutes integer NOT NULL CHECK(before_buffer_minutes BETWEEN 0 AND 240), after_buffer_minutes integer NOT NULL CHECK(after_buffer_minutes BETWEEN 0 AND 240),
 category_codes jsonb NOT NULL, service_area_codes jsonb NOT NULL, policy_version bigint NOT NULL, calendar_version bigint NOT NULL,
 state text NOT NULL CHECK(state IN ('PUBLISHED','WITHDRAWN')), reason text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK(isfinite(arrival_start) AND isfinite(arrival_end) AND arrival_start<arrival_end AND arrival_end<=arrival_start+interval '8 hours'),
 UNIQUE(organization_id,id), FOREIGN KEY(organization_id,profile_id) REFERENCES dispatch_technician_profiles(organization_id,id)
);
CREATE TABLE appointment_requests(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id), request_id uuid NOT NULL,
 kind text NOT NULL CHECK(kind IN ('INITIAL','RESCHEDULE')), selected_window_id uuid NOT NULL, replaces_appointment_id uuid,
 alternative_window_id uuid, proposal_revision bigint, reviewed_expectations jsonb, offer_expires_at timestamptz,
 expires_at timestamptz NOT NULL, confirmed_appointment_id uuid,
 status text NOT NULL CHECK(status IN ('PENDING','ALTERNATIVE_OFFERED','CONFIRMED','DECLINED','WITHDRAWN','EXPIRED')),
 public_message text, internal_reason text NOT NULL DEFAULT '',
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 CHECK((kind='INITIAL')=(replaces_appointment_id IS NULL)),
 UNIQUE(organization_id,id), UNIQUE(organization_id,request_id,id),
 FOREIGN KEY(organization_id,request_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,selected_window_id) REFERENCES appointment_windows(organization_id,id),
 FOREIGN KEY(organization_id,alternative_window_id) REFERENCES appointment_windows(organization_id,id)
);
CREATE UNIQUE INDEX appointment_request_live ON appointment_requests(organization_id,request_id) WHERE status IN ('PENDING','ALTERNATIVE_OFFERED');
CREATE TABLE appointments(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id), request_id uuid NOT NULL,
 appointment_request_id uuid NOT NULL, window_id uuid NOT NULL, work_order_id uuid NOT NULL, assignee_id uuid NOT NULL, subject_id uuid NOT NULL,
 assignment_version bigint NOT NULL, arrival_start timestamptz NOT NULL, arrival_end timestamptz NOT NULL,
 service_duration_minutes integer NOT NULL, occupied_range tstzrange NOT NULL, policy_version bigint NOT NULL,
 status text NOT NULL CHECK(status IN ('CONFIRMED','CHECKED_IN','VISIT_FINISHED','NO_ACCESS','ABORTED','NO_SHOW','CANCELLED','SUPERSEDED')),
 replaces_id uuid, cancellation_pending boolean NOT NULL DEFAULT false, public_visit_message text, internal_reason text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 UNIQUE(organization_id,id), UNIQUE(organization_id,request_id,id), UNIQUE(organization_id,appointment_request_id),
 FOREIGN KEY(organization_id,request_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,request_id,appointment_request_id) REFERENCES appointment_requests(organization_id,request_id,id),
 FOREIGN KEY(organization_id,window_id) REFERENCES appointment_windows(organization_id,id),
 FOREIGN KEY(organization_id,work_order_id) REFERENCES work_orders(organization_id,id),
 FOREIGN KEY(organization_id,assignee_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,subject_id) REFERENCES dispatch_calendar_subjects(exclusive_dispatch_organization_id,id),
 FOREIGN KEY(organization_id,request_id,replaces_id) REFERENCES appointments(organization_id,request_id,id)
);
CREATE UNIQUE INDEX appointment_one_case ON appointments(organization_id,request_id) WHERE status IN ('CONFIRMED','CHECKED_IN');
CREATE UNIQUE INDEX appointment_one_work ON appointments(organization_id,work_order_id) WHERE status IN ('CONFIRMED','CHECKED_IN');
CREATE UNIQUE INDEX appointment_one_checkin ON appointments(subject_id) WHERE status='CHECKED_IN';
ALTER TABLE appointment_requests ADD FOREIGN KEY(organization_id,request_id,replaces_appointment_id) REFERENCES appointments(organization_id,request_id,id);
ALTER TABLE appointment_requests ADD FOREIGN KEY(organization_id,confirmed_appointment_id) REFERENCES appointments(organization_id,id);
ALTER TABLE dispatch_allocations ADD CONSTRAINT dispatch_appointment_fk FOREIGN KEY(organization_id,appointment_id) REFERENCES appointments(organization_id,id);
CREATE TABLE appointment_events(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id), appointment_id uuid NOT NULL,
 actor_id uuid NOT NULL, operation_id uuid NOT NULL, event_type text NOT NULL, note text NOT NULL CHECK(length(note) BETWEEN 1 AND 2000),
 observed_at timestamptz NOT NULL, received_at timestamptz NOT NULL DEFAULT now(), created_at timestamptz NOT NULL DEFAULT now(),
 assignment_version bigint NOT NULL, supersedes_event_id uuid,
 UNIQUE(organization_id,id), UNIQUE(organization_id,appointment_id,id), UNIQUE(organization_id,actor_id,operation_id),
 FOREIGN KEY(organization_id,appointment_id) REFERENCES appointments(organization_id,id),
 FOREIGN KEY(organization_id,actor_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,appointment_id,supersedes_event_id) REFERENCES appointment_events(organization_id,appointment_id,id)
);
CREATE TRIGGER immutable_appointment_event BEFORE UPDATE OR DELETE ON appointment_events FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();

-- Owner-approved explicit eligibility review; null historical links are not schedulable.
ALTER TABLE service_work_order_links ADD COLUMN dispatch_service_area_code text CHECK(length(dispatch_service_area_code) BETWEEN 1 AND 40);
ALTER TABLE service_work_order_links ADD COLUMN dispatch_required_skill_codes jsonb;
ALTER TABLE service_work_order_links ADD CHECK((dispatch_service_area_code IS NULL)=(dispatch_required_skill_codes IS NULL));
ALTER TABLE service_work_order_links ADD CHECK(dispatch_required_skill_codes IS NULL OR (jsonb_typeof(dispatch_required_skill_codes)='array' AND jsonb_array_length(dispatch_required_skill_codes) BETWEEN 1 AND 20));

-- Narrow functions expose neither a roster nor an internal calendar to residents.
CREATE FUNCTION hydro_dispatch_service_visible(service uuid) RETURNS boolean LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
 SELECT EXISTS(SELECT 1 FROM public.service_requests s JOIN public.organization_memberships m ON m.id=s.owner_membership_id
 WHERE s.id=service AND s.organization_id::text=current_setting('hydro.organization_id',true)
 AND m.user_id::text=current_setting('hydro.user_id',true) AND m.status='ACTIVE')
$$;
CREATE FUNCTION hydro_dispatch_case_links(service uuid) RETURNS TABLE(work_order_id uuid,dispatch_service_area_code text,dispatch_required_skill_codes jsonb)
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public AS $$
 SELECT l.work_order_id,l.dispatch_service_area_code,l.dispatch_required_skill_codes FROM public.service_work_order_links l
 WHERE l.request_id=service AND l.organization_id::text=current_setting('hydro.organization_id',true)
 AND (public.hydro_m07_role(ARRAY['SUPERVISOR']) OR public.hydro_dispatch_service_visible(service))
$$;
REVOKE ALL ON FUNCTION hydro_dispatch_service_visible(uuid),hydro_dispatch_case_links(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_dispatch_service_visible(uuid),hydro_dispatch_case_links(uuid) TO hydro_app;
