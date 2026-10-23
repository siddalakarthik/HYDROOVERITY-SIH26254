-- Additive service foundation. No visit access, scheduling, media or jobs.
ALTER TABLE work_orders ADD COLUMN task_purpose text NOT NULL DEFAULT 'REPAIR'
 CHECK(task_purpose IN ('REPAIR','INVESTIGATION','INSPECTION'));

CREATE FUNCTION hydro_m07_role(codes text[]) RETURNS boolean LANGUAGE sql STABLE AS $$
 SELECT EXISTS(SELECT 1 FROM organization_memberships m JOIN organizations o ON o.id=m.organization_id
 JOIN role_assignments a ON a.membership_id=m.id AND a.organization_id=m.organization_id
 JOIN roles r ON r.id=a.role_id WHERE m.user_id::text=current_setting('hydro.user_id',true)
 AND m.organization_id::text=current_setting('hydro.organization_id',true)
 AND m.status='ACTIVE' AND o.status='ACTIVE' AND a.revoked_at IS NULL AND r.code=ANY(codes))
$$;
CREATE FUNCTION hydro_m07_own(member uuid) RETURNS boolean LANGUAGE sql STABLE AS $$
 SELECT EXISTS(SELECT 1 FROM organization_memberships m WHERE m.id=member
 AND m.user_id::text=current_setting('hydro.user_id',true) AND m.status='ACTIVE'
 AND m.organization_id::text=current_setting('hydro.organization_id',true))
$$;
REVOKE ALL ON FUNCTION hydro_m07_role(text[]),hydro_m07_own(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION hydro_m07_role(text[]),hydro_m07_own(uuid) TO hydro_app;

CREATE TABLE service_requests(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version BETWEEN 1 AND 2147483647),
 owner_membership_id uuid NOT NULL, tracking_reference text NOT NULL CHECK(tracking_reference ~ '^HYS-[0-9A-HJKMNP-TV-Z]{26}$'),
 origin_complaint_id uuid, follow_up_of_id uuid,
 category text NOT NULL CHECK(category IN ('VISIBLE_LEAK','LOW_PRESSURE','SERVICE_INTERRUPTION')),
 description text NOT NULL CHECK(length(description) BETWEEN 10 AND 2000),
 coarse_area text NOT NULL CHECK(length(coarse_area) BETWEEN 2 AND 200),
 status text NOT NULL DEFAULT 'SUBMITTED' CHECK(status IN ('SUBMITTED','UNDER_REVIEW','AWAITING_RESIDENT','ACCEPTED','SERVICE_IN_PROGRESS','SERVICE_REVIEW_PENDING','SERVICE_CLOSED','DECLINED','WITHDRAWN','CANCELLED')),
 cancellation_pending boolean NOT NULL DEFAULT false,
 service_outcome text CHECK(service_outcome IN ('ADVICE_PROVIDED','VISIT_COMPLETED','REPAIR_REPORTED','REFERRED','NO_ACTION_WITH_REASON')),
 accepted_at timestamptz, accepted_by_id uuid,
 CHECK((accepted_at IS NULL)=(accepted_by_id IS NULL)),
 CHECK((status='SERVICE_CLOSED')=(service_outcome IS NOT NULL)),
 CHECK(origin_complaint_id IS NULL OR follow_up_of_id IS NULL),
 CHECK(follow_up_of_id IS NULL OR follow_up_of_id<>id),
 UNIQUE(organization_id,id), UNIQUE(organization_id,tracking_reference),
 FOREIGN KEY(organization_id,owner_membership_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,origin_complaint_id) REFERENCES citizen_complaints(organization_id,id),
 FOREIGN KEY(organization_id,follow_up_of_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,accepted_by_id) REFERENCES organization_memberships(organization_id,id)
);
CREATE UNIQUE INDEX service_origin_once ON service_requests(organization_id,origin_complaint_id) WHERE origin_complaint_id IS NOT NULL;
CREATE INDEX service_owner_list ON service_requests(organization_id,owner_membership_id,created_at DESC,id DESC);
CREATE INDEX service_triage_queue ON service_requests(organization_id,status,created_at DESC,id DESC);

CREATE TABLE service_request_events(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), request_id uuid NOT NULL,
 sequence bigint NOT NULL CHECK(sequence>0), event_kind text NOT NULL CHECK(length(event_kind) BETWEEN 1 AND 40),
 actor_id uuid, received_at timestamptz NOT NULL DEFAULT now(), observed_at timestamptz,
 internal_reason text NOT NULL CHECK(length(internal_reason)<=2000),
 resource_type text NOT NULL CHECK(resource_type IN ('SERVICE','WORK')), resource_id uuid,
 previous_version bigint, resulting_version bigint NOT NULL CHECK(resulting_version>0), supersedes_id uuid,
 operation_id uuid,
 UNIQUE(organization_id,id), UNIQUE(organization_id,request_id,id), UNIQUE(organization_id,request_id,sequence),
 UNIQUE(organization_id,actor_id,operation_id),
 FOREIGN KEY(organization_id,request_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,actor_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,request_id,supersedes_id) REFERENCES service_request_events(organization_id,request_id,id)
);
CREATE TABLE service_public_updates(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), request_id uuid NOT NULL, sequence bigint NOT NULL CHECK(sequence>0),
 origin_event_id uuid NOT NULL, actor_id uuid, event_kind text NOT NULL CHECK(event_kind IN ('INFORMATION','PROGRESS','CORRECTION','SERVICE')),
 message text NOT NULL CHECK(length(message)<=2000), template_code text,
 occurred_at timestamptz NOT NULL DEFAULT now(), published_at timestamptz NOT NULL DEFAULT now(),
 appointment_id uuid CHECK(appointment_id IS NULL), supersedes_id uuid,
 UNIQUE(organization_id,id), UNIQUE(organization_id,request_id,id), UNIQUE(organization_id,request_id,sequence),
 UNIQUE(organization_id,origin_event_id,template_code),
 FOREIGN KEY(organization_id,request_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,request_id,origin_event_id) REFERENCES service_request_events(organization_id,request_id,id),
 FOREIGN KEY(organization_id,actor_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,request_id,supersedes_id) REFERENCES service_public_updates(organization_id,request_id,id)
);
CREATE TABLE service_work_order_links(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0), request_id uuid NOT NULL, work_order_id uuid NOT NULL,
 linked_by_id uuid NOT NULL, purpose text NOT NULL CHECK(purpose IN ('REPAIR','INVESTIGATION','INSPECTION')), ended_at timestamptz,
 UNIQUE(organization_id,id), UNIQUE(organization_id,request_id,work_order_id),
 FOREIGN KEY(organization_id,request_id) REFERENCES service_requests(organization_id,id),
 FOREIGN KEY(organization_id,work_order_id) REFERENCES work_orders(organization_id,id),
 FOREIGN KEY(organization_id,linked_by_id) REFERENCES organization_memberships(organization_id,id)
);
CREATE TABLE work_investigation_findings(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), organization_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(), work_order_id uuid NOT NULL, recorded_by_id uuid NOT NULL,
 assignment_version bigint NOT NULL CHECK(assignment_version>0), work_version bigint NOT NULL CHECK(work_version>0),
 operation_id uuid NOT NULL, observed_at timestamptz NOT NULL, received_at timestamptz NOT NULL DEFAULT now(),
 findings text NOT NULL CHECK(length(findings) BETWEEN 10 AND 4000),
 no_repair_reason text NOT NULL CHECK(length(no_repair_reason) BETWEEN 5 AND 2000), supersedes_id uuid,
 UNIQUE(organization_id,id), UNIQUE(organization_id,work_order_id,id), UNIQUE(organization_id,recorded_by_id,operation_id),
 UNIQUE(organization_id,supersedes_id),
 FOREIGN KEY(organization_id,work_order_id) REFERENCES work_orders(organization_id,id),
 FOREIGN KEY(organization_id,recorded_by_id) REFERENCES organization_memberships(organization_id,id),
 FOREIGN KEY(organization_id,work_order_id,supersedes_id) REFERENCES work_investigation_findings(organization_id,work_order_id,id)
);

ALTER TABLE service_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_requests FORCE ROW LEVEL SECURITY;
CREATE POLICY service_scope ON service_requests USING (
 organization_id::text=current_setting('hydro.organization_id',true) AND
 (hydro_m07_role(ARRAY['SUPERVISOR']) OR (hydro_m07_role(ARRAY['CITIZEN']) AND hydro_m07_own(owner_membership_id))))
 WITH CHECK(organization_id::text=current_setting('hydro.organization_id',true) AND
 (hydro_m07_role(ARRAY['SUPERVISOR']) OR (hydro_m07_role(ARRAY['CITIZEN']) AND hydro_m07_own(owner_membership_id))));

-- Owner/migrator retains operational ownership, runtime remains non-owner and RLS-bound.
-- Migrator needs explicit access for controlled acceptance/reset; runtime cannot SET ROLE.
CREATE POLICY migration_service_scope ON service_requests TO hydro_migrator USING(true) WITH CHECK(true);
GRANT SELECT,INSERT,UPDATE ON service_requests TO hydro_app;
GRANT SELECT,INSERT ON service_request_events,service_public_updates,service_work_order_links,work_investigation_findings TO hydro_app;
