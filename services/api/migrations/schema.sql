-- Static M03 operational schema. Future feature references are inaccessible.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE organizations (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  name text NOT NULL,
  public_slug text NOT NULL,
  status text NOT NULL,
  retention_policy jsonb NOT NULL,
  public_reporting_enabled boolean NOT NULL,
  UNIQUE(public_slug)
);

CREATE TABLE users (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  email_normalized text NOT NULL,
  display_name text NOT NULL,
  password_hash text NOT NULL,
  email_verified_at timestamptz,
  deactivated_at timestamptz,
  UNIQUE(email_normalized)
);

CREATE TABLE organization_memberships (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  user_id uuid NOT NULL,
  status text NOT NULL,
  suspended_at timestamptz,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,user_id)
);

CREATE TABLE roles (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  code text NOT NULL,
  description text NOT NULL,
  UNIQUE(code)
);

CREATE TABLE permissions (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  code text NOT NULL,
  description text NOT NULL,
  UNIQUE(code)
);

CREATE TABLE role_permissions (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  role_id uuid NOT NULL,
  permission_id uuid NOT NULL,
  UNIQUE(role_id,permission_id)
);

CREATE TABLE role_assignments (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  membership_id uuid NOT NULL,
  role_id uuid NOT NULL,
  granted_by_id uuid NOT NULL,
  revoked_at timestamptz,
  UNIQUE(organization_id,id)
);

CREATE TABLE sessions (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  user_id uuid,
  token_hash bytea NOT NULL,
  csrf_hash bytea NOT NULL,
  auth_level text NOT NULL,
  idle_expires_at timestamptz NOT NULL,
  absolute_expires_at timestamptz NOT NULL,
  reauthenticated_at timestamptz,
  revoked_at timestamptz,
  UNIQUE(token_hash)
);

CREATE TABLE invitations (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  email_normalized text NOT NULL,
  role_id uuid NOT NULL,
  invited_by_id uuid NOT NULL,
  token_hash bytea NOT NULL,
  expires_at timestamptz NOT NULL,
  accepted_at timestamptz,
  UNIQUE(organization_id,id),
  UNIQUE(token_hash)
);

CREATE TABLE account_recovery_tokens (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  user_id uuid NOT NULL,
  purpose text NOT NULL,
  token_hash bytea NOT NULL,
  expires_at timestamptz NOT NULL,
  used_at timestamptz,
  UNIQUE(token_hash)
);

CREATE TABLE water_zones (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  name text NOT NULL,
  boundary geometry(MultiPolygon,4326),
  demand_boundary_version text NOT NULL,
  demand_accounting jsonb NOT NULL,
  topology_quality text NOT NULL,
  UNIQUE(organization_id,id)
);

CREATE TABLE network_junctions (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  zone_id uuid NOT NULL,
  external_ref text NOT NULL,
  point geometry(Point,4326) NOT NULL,
  topology_quality text NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,external_ref)
);

CREATE TABLE pipe_segments (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  zone_id uuid NOT NULL,
  from_junction_id uuid NOT NULL,
  to_junction_id uuid NOT NULL,
  geometry geometry(LineString,4326) NOT NULL,
  material text NOT NULL,
  diameter_mm numeric NOT NULL,
  surveyed_length_m numeric,
  length_uncertainty_m numeric,
  geometry_length_m numeric NOT NULL,
  length_basis text NOT NULL,
  topology_quality text NOT NULL,
  retired_at timestamptz,
  UNIQUE(organization_id,id)
);

CREATE TABLE evidence_records (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  observation_id uuid,
  capture_id uuid,
  complaint_id uuid,
  repair_id uuid,
  manual_actor_id uuid,
  manual_note text,
  environment text NOT NULL CHECK (environment IN ('SIMULATION','LABORATORY','FIELD','MANUAL')),
  record_type text NOT NULL,
  supersedes_id uuid,
  UNIQUE(organization_id,id)
);

CREATE TABLE evidence_assessments (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  kind text NOT NULL CHECK (kind IN ('HYDRAULIC_ANOMALY','LOCAL_JOINT_SUSPICION','ENVIRONMENTAL_WETNESS','COLLECTION_FAILURE','SENSOR_FAILURE','ACOUSTIC_CANDIDATE','INSUFFICIENT_SIGNAL','UNRESOLVED_CAUSE')),
  disposition text NOT NULL CHECK (disposition IN ('OBSERVED','SUSPECTED','QUALIFIED_CANDIDATE','UNRESOLVED','FAULT')),
  reason_codes text[] NOT NULL,
  explanation text NOT NULL,
  algorithm_configuration_id uuid,
  reviewer_id uuid,
  acoustic_estimate_id uuid,
  workspace_mode text NOT NULL CHECK (workspace_mode IN ('SIMULATION','OPERATIONAL')),
  simulation_run_id uuid,
  supersedes_id uuid,
  UNIQUE(organization_id,id)
);

CREATE TABLE assessment_evidence (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  assessment_id uuid NOT NULL,
  evidence_record_id uuid NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,assessment_id,evidence_record_id)
);

CREATE TABLE incidents (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  zone_id uuid NOT NULL,
  status text NOT NULL CHECK (status IN ('NEW','UNDER_REVIEW','INVESTIGATION_REQUIRED','ACCEPTED','IN_PROGRESS','VERIFICATION_PENDING','RESOLVED','REOPENED','NOT_VERIFIABLE','DISMISSED')),
  severity text NOT NULL,
  title text NOT NULL,
  owner_id uuid,
  workspace_mode text NOT NULL CHECK (workspace_mode IN ('SIMULATION','OPERATIONAL')),
  simulation_run_id uuid,
  resolved_at timestamptz,
  UNIQUE(organization_id,id)
);

CREATE TABLE incident_events (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  incident_id uuid NOT NULL,
  actor_id uuid,
  event_type text NOT NULL,
  from_status text CHECK (from_status IN ('NEW','UNDER_REVIEW','INVESTIGATION_REQUIRED','ACCEPTED','IN_PROGRESS','VERIFICATION_PENDING','RESOLVED','REOPENED','NOT_VERIFIABLE','DISMISSED')),
  to_status text CHECK (to_status IN ('NEW','UNDER_REVIEW','INVESTIGATION_REQUIRED','ACCEPTED','IN_PROGRESS','VERIFICATION_PENDING','RESOLVED','REOPENED','NOT_VERIFIABLE','DISMISSED')),
  reason text NOT NULL,
  operation_id uuid NOT NULL,
  occurred_at timestamptz NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,incident_id,operation_id)
);

CREATE TABLE incident_evidence (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  incident_id uuid NOT NULL,
  assessment_id uuid NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,incident_id,assessment_id)
);

CREATE TABLE incident_links (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  source_incident_id uuid NOT NULL,
  target_incident_id uuid NOT NULL,
  relation text NOT NULL,
  actor_id uuid NOT NULL,
  reason text NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,source_incident_id,target_incident_id,relation)
);

CREATE TABLE work_orders (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  incident_id uuid NOT NULL,
  assignee_id uuid,
  status text NOT NULL CHECK (status IN ('CREATED','ASSIGNED','ACCEPTED','IN_PROGRESS','BLOCKED','SUBMITTED_FOR_REVIEW','COMPLETED','CANCELLED')),
  priority text NOT NULL,
  due_at timestamptz,
  instructions text NOT NULL,
  assignment_version bigint NOT NULL,
  workspace_mode text NOT NULL CHECK (workspace_mode IN ('SIMULATION','OPERATIONAL')),
  UNIQUE(organization_id,id)
);

CREATE TABLE work_order_actions (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  work_order_id uuid NOT NULL,
  actor_id uuid NOT NULL,
  action_type text NOT NULL,
  note text NOT NULL,
  materials jsonb NOT NULL,
  operation_id uuid NOT NULL,
  observed_at timestamptz NOT NULL,
  received_at timestamptz NOT NULL,
  base_version bigint NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,work_order_id,operation_id)
);

CREATE TABLE repair_records (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  work_order_id uuid NOT NULL,
  recorded_by_id uuid NOT NULL,
  performed_at timestamptz NOT NULL,
  description text NOT NULL,
  materials jsonb NOT NULL,
  environment text NOT NULL CHECK (environment IN ('SIMULATION','LABORATORY','FIELD','MANUAL')),
  supersedes_id uuid,
  UNIQUE(organization_id,id)
);

CREATE TABLE verification_records (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  repair_id uuid NOT NULL,
  reviewer_id uuid NOT NULL,
  outcome text NOT NULL CHECK (outcome IN ('VERIFICATION_PASSED','VERIFICATION_FAILED','NOT_VERIFIABLE')),
  comparability jsonb NOT NULL,
  reason text NOT NULL,
  reviewed_at timestamptz NOT NULL,
  supersedes_id uuid,
  UNIQUE(organization_id,id)
);

CREATE TABLE verification_evidence (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  verification_id uuid NOT NULL,
  evidence_record_id uuid NOT NULL,
  phase text NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,verification_id,evidence_record_id,phase)
);

CREATE TABLE citizen_complaints (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  version bigint DEFAULT 1 CHECK(version>0) NOT NULL,
  reporter_id uuid NOT NULL,
  tracking_number text NOT NULL,
  category text NOT NULL,
  description text NOT NULL,
  coarse_area text NOT NULL,
  coarse_point geometry(Point,4326),
  status text NOT NULL CHECK (status IN ('RECEIVED','UNDER_REVIEW','INVESTIGATING','ACTION_PLANNED','UPDATE_AVAILABLE','RESOLVED','CLOSED_NO_ACTION')),
  incident_id uuid,
  consent_at timestamptz,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,tracking_number)
);

CREATE TABLE complaint_status_events (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  complaint_id uuid NOT NULL,
  actor_id uuid,
  status text NOT NULL CHECK (status IN ('RECEIVED','UNDER_REVIEW','INVESTIGATING','ACTION_PLANNED','UPDATE_AVAILABLE','RESOLVED','CLOSED_NO_ACTION')),
  public_message text NOT NULL,
  occurred_at timestamptz NOT NULL,
  UNIQUE(organization_id,id)
);

CREATE TABLE audit_logs (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  actor_id uuid,
  action text NOT NULL,
  resource_type text NOT NULL,
  resource_id uuid,
  request_id uuid NOT NULL,
  safe_metadata jsonb NOT NULL,
  occurred_at timestamptz NOT NULL,
  UNIQUE(organization_id,id)
);

CREATE TABLE idempotency_records (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  actor_scope text NOT NULL,
  operation_key uuid NOT NULL,
  method text NOT NULL,
  route_template text NOT NULL,
  request_hash text NOT NULL,
  result_resource_id uuid,
  result_status integer,
  expires_at timestamptz NOT NULL,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,actor_scope,method,route_template,operation_key)
);

CREATE TABLE domain_events (
  id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  sequence bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  event_type text NOT NULL,
  resource_type text NOT NULL,
  resource_id uuid NOT NULL,
  workspace_mode text NOT NULL CHECK (workspace_mode IN ('SIMULATION','OPERATIONAL')),
  minimum_permission text NOT NULL,
  occurred_at timestamptz NOT NULL,
  safe_summary jsonb NOT NULL,
  published_at timestamptz,
  UNIQUE(organization_id,id),
  UNIQUE(organization_id,sequence)
);

ALTER TABLE organization_memberships ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE organization_memberships ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;

CREATE INDEX organization_memberships_idx0 ON organization_memberships (organization_id,status,user_id);

ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON organization_memberships USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE role_permissions ADD FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT;

ALTER TABLE role_permissions ADD FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE role_assignments ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE role_assignments ADD FOREIGN KEY (organization_id,membership_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE role_assignments ADD FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT;

ALTER TABLE role_assignments ADD FOREIGN KEY (organization_id,granted_by_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX role_assignments_idx0 ON role_assignments (organization_id,membership_id);

ALTER TABLE role_assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON role_assignments USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE sessions ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;

CREATE INDEX sessions_idx0 ON sessions (user_id,revoked_at);

CREATE INDEX sessions_idx1 ON sessions (absolute_expires_at);

ALTER TABLE invitations ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE invitations ADD FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT;

ALTER TABLE invitations ADD FOREIGN KEY (organization_id,invited_by_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE invitations ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON invitations USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE account_recovery_tokens ADD FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;

CREATE INDEX account_recovery_tokens_idx0 ON account_recovery_tokens (user_id,purpose);

ALTER TABLE water_zones ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

CREATE INDEX water_zones_idx0 ON water_zones USING GiST(boundary);

ALTER TABLE water_zones ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON water_zones USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE network_junctions ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE network_junctions ADD FOREIGN KEY (organization_id,zone_id) REFERENCES water_zones(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX network_junctions_idx0 ON network_junctions USING GiST(point);

CREATE INDEX network_junctions_idx1 ON network_junctions (organization_id,zone_id);

ALTER TABLE network_junctions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON network_junctions USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE pipe_segments ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE pipe_segments ADD FOREIGN KEY (organization_id,zone_id) REFERENCES water_zones(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE pipe_segments ADD FOREIGN KEY (organization_id,from_junction_id) REFERENCES network_junctions(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE pipe_segments ADD FOREIGN KEY (organization_id,to_junction_id) REFERENCES network_junctions(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX pipe_segments_idx0 ON pipe_segments USING GiST(geometry);

CREATE INDEX pipe_segments_idx1 ON pipe_segments (organization_id,zone_id);

ALTER TABLE pipe_segments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON pipe_segments USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE evidence_records ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE evidence_records ADD CONSTRAINT evidence_records_observation_id_deferred CHECK (observation_id IS NULL);

ALTER TABLE evidence_records ADD CONSTRAINT evidence_records_capture_id_deferred CHECK (capture_id IS NULL);

ALTER TABLE evidence_records ADD FOREIGN KEY (organization_id,complaint_id) REFERENCES citizen_complaints(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE evidence_records ADD FOREIGN KEY (organization_id,repair_id) REFERENCES repair_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE evidence_records ADD FOREIGN KEY (organization_id,manual_actor_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE evidence_records ADD FOREIGN KEY (organization_id,supersedes_id) REFERENCES evidence_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE evidence_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON evidence_records USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE evidence_assessments ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE evidence_assessments ADD CONSTRAINT evidence_assessments_algorithm_configuration_id_deferred CHECK (algorithm_configuration_id IS NULL);

ALTER TABLE evidence_assessments ADD FOREIGN KEY (organization_id,reviewer_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE evidence_assessments ADD CONSTRAINT evidence_assessments_acoustic_estimate_id_deferred CHECK (acoustic_estimate_id IS NULL);

ALTER TABLE evidence_assessments ADD CONSTRAINT evidence_assessments_simulation_run_id_deferred CHECK (simulation_run_id IS NULL);

ALTER TABLE evidence_assessments ADD FOREIGN KEY (organization_id,supersedes_id) REFERENCES evidence_assessments(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE evidence_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON evidence_assessments USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE assessment_evidence ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE assessment_evidence ADD FOREIGN KEY (organization_id,assessment_id) REFERENCES evidence_assessments(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE assessment_evidence ADD FOREIGN KEY (organization_id,evidence_record_id) REFERENCES evidence_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE assessment_evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON assessment_evidence USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE incidents ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE incidents ADD FOREIGN KEY (organization_id,zone_id) REFERENCES water_zones(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incidents ADD FOREIGN KEY (organization_id,owner_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incidents ADD CONSTRAINT incidents_simulation_run_id_deferred CHECK (simulation_run_id IS NULL);

CREATE INDEX incidents_idx0 ON incidents (organization_id,status,severity,created_at DESC);

ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON incidents USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE incident_events ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE incident_events ADD FOREIGN KEY (organization_id,incident_id) REFERENCES incidents(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incident_events ADD FOREIGN KEY (organization_id,actor_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX incident_events_idx0 ON incident_events (organization_id,incident_id,occurred_at,id);

ALTER TABLE incident_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON incident_events USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE incident_evidence ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE incident_evidence ADD FOREIGN KEY (organization_id,incident_id) REFERENCES incidents(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incident_evidence ADD FOREIGN KEY (organization_id,assessment_id) REFERENCES evidence_assessments(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incident_evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON incident_evidence USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE incident_links ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE incident_links ADD FOREIGN KEY (organization_id,source_incident_id) REFERENCES incidents(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incident_links ADD FOREIGN KEY (organization_id,target_incident_id) REFERENCES incidents(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incident_links ADD FOREIGN KEY (organization_id,actor_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE incident_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON incident_links USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE work_orders ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE work_orders ADD FOREIGN KEY (organization_id,incident_id) REFERENCES incidents(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE work_orders ADD FOREIGN KEY (organization_id,assignee_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX work_orders_idx0 ON work_orders (organization_id,assignee_id,status,due_at);

ALTER TABLE work_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON work_orders USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE work_order_actions ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE work_order_actions ADD FOREIGN KEY (organization_id,work_order_id) REFERENCES work_orders(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE work_order_actions ADD FOREIGN KEY (organization_id,actor_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE work_order_actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON work_order_actions USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE repair_records ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE repair_records ADD FOREIGN KEY (organization_id,work_order_id) REFERENCES work_orders(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE repair_records ADD FOREIGN KEY (organization_id,recorded_by_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE repair_records ADD FOREIGN KEY (organization_id,supersedes_id) REFERENCES repair_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE repair_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON repair_records USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE verification_records ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE verification_records ADD FOREIGN KEY (organization_id,repair_id) REFERENCES repair_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE verification_records ADD FOREIGN KEY (organization_id,reviewer_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE verification_records ADD FOREIGN KEY (organization_id,supersedes_id) REFERENCES verification_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE verification_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON verification_records USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE verification_evidence ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE verification_evidence ADD FOREIGN KEY (organization_id,verification_id) REFERENCES verification_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE verification_evidence ADD FOREIGN KEY (organization_id,evidence_record_id) REFERENCES evidence_records(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE verification_evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON verification_evidence USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE citizen_complaints ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE citizen_complaints ADD FOREIGN KEY (organization_id,reporter_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE citizen_complaints ADD FOREIGN KEY (organization_id,incident_id) REFERENCES incidents(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX citizen_complaints_idx0 ON citizen_complaints (organization_id,reporter_id,created_at DESC);

ALTER TABLE citizen_complaints ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON citizen_complaints USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE complaint_status_events ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE complaint_status_events ADD FOREIGN KEY (organization_id,complaint_id) REFERENCES citizen_complaints(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE complaint_status_events ADD FOREIGN KEY (organization_id,actor_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

ALTER TABLE complaint_status_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON complaint_status_events USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE audit_logs ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

ALTER TABLE audit_logs ADD FOREIGN KEY (organization_id,actor_id) REFERENCES organization_memberships(organization_id,id) ON DELETE RESTRICT;

CREATE INDEX audit_logs_idx0 ON audit_logs (organization_id,occurred_at DESC,id);

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON audit_logs USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE idempotency_records ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

CREATE INDEX idempotency_records_idx0 ON idempotency_records (expires_at);

ALTER TABLE idempotency_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON idempotency_records USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

ALTER TABLE domain_events ADD FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;

CREATE INDEX domain_events_idx0 ON domain_events (organization_id,sequence);

ALTER TABLE domain_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_scope ON domain_events USING (organization_id::text=current_setting('hydro.organization_id',true)) WITH CHECK (organization_id::text=current_setting('hydro.organization_id',true));

CREATE UNIQUE INDEX active_role_unique ON role_assignments(organization_id,membership_id,role_id) WHERE revoked_at IS NULL;

CREATE UNIQUE INDEX idem_operation_unique ON idempotency_records(organization_id,actor_scope,method,route_template,operation_key);

CREATE UNIQUE INDEX worker_operation_unique ON work_order_actions(organization_id,work_order_id,operation_id);

ALTER TABLE sessions ADD CHECK(auth_level IN ('PREAUTH','AUTHENTICATED')), ADD CHECK((auth_level='PREAUTH')=(user_id IS NULL)), ADD CHECK(idle_expires_at<=absolute_expires_at);

ALTER TABLE organizations ADD CHECK(status IN ('ACTIVE','SUSPENDED')), ADD CHECK(length(name) BETWEEN 1 AND 150), ADD CHECK(public_slug ~ '^[a-z0-9-]{1,80}$');

ALTER TABLE organization_memberships ADD CHECK(status IN ('PENDING','ACTIVE','SUSPENDED'));

ALTER TABLE users ADD CHECK(email_normalized=lower(btrim(email_normalized))), ADD CHECK(length(display_name) BETWEEN 1 AND 120);

ALTER TABLE account_recovery_tokens ADD CHECK(purpose IN ('VERIFY','RESET'));

ALTER TABLE evidence_records ADD CHECK(num_nonnulls(observation_id,capture_id,complaint_id,repair_id,manual_actor_id)=1), ADD CHECK((manual_actor_id IS NULL)=(manual_note IS NULL)), ADD CHECK(environment='MANUAL');

ALTER TABLE evidence_assessments ADD CHECK(workspace_mode='OPERATIONAL'), ADD CHECK(reviewer_id IS NOT NULL);

ALTER TABLE incidents ADD CHECK(workspace_mode='OPERATIONAL'), ADD CHECK(severity IN ('LOW','MEDIUM','HIGH','URGENT'));

ALTER TABLE work_orders ADD CHECK(workspace_mode='OPERATIONAL'), ADD CHECK(assignment_version>0), ADD CHECK(priority IN ('LOW','MEDIUM','HIGH','URGENT'));

ALTER TABLE incident_links ADD CHECK(source_incident_id<>target_incident_id), ADD CHECK(relation IN ('RELATED','DUPLICATE_OF'));

ALTER TABLE repair_records ADD CHECK(environment='MANUAL');

ALTER TABLE verification_records ADD CONSTRAINT m03_manual_verification_only CHECK(outcome='NOT_VERIFIABLE');

ALTER TABLE verification_evidence ADD CHECK(phase IN ('BEFORE','AFTER'));

ALTER TABLE citizen_complaints ADD CHECK(length(description) BETWEEN 10 AND 2000), ADD CHECK(length(coarse_area) BETWEEN 2 AND 200), ADD CHECK(coarse_point IS NULL);

ALTER TABLE water_zones ADD CHECK(boundary IS NULL OR ST_IsValid(boundary));

ALTER TABLE network_junctions ADD CHECK(ST_IsValid(point) AND ST_X(point) BETWEEN -180 AND 180 AND ST_Y(point) BETWEEN -90 AND 90);

ALTER TABLE pipe_segments ADD CHECK(ST_IsValid(geometry)), ADD CHECK(from_junction_id<>to_junction_id), ADD CHECK(diameter_mm>0 AND diameter_mm::text NOT IN ('NaN','Infinity','-Infinity')), ADD CHECK(geometry_length_m>0), ADD CHECK(surveyed_length_m IS NULL OR surveyed_length_m>0), ADD CHECK(length_uncertainty_m IS NULL OR length_uncertainty_m>=0), ADD CHECK(length_basis IN ('SURVEYED','GEODESIC'));

CREATE INDEX complaint_daily ON citizen_complaints(organization_id,reporter_id,created_at);

REVOKE ALL ON SCHEMA public FROM PUBLIC;

GRANT USAGE ON SCHEMA public TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON organizations TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON users TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON organization_memberships TO hydro_app;

GRANT SELECT ON roles TO hydro_app;

GRANT SELECT ON permissions TO hydro_app;

GRANT SELECT ON role_permissions TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON role_assignments TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON sessions TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON invitations TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON account_recovery_tokens TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON water_zones TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON network_junctions TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON pipe_segments TO hydro_app;

GRANT SELECT,INSERT ON evidence_records TO hydro_app;

GRANT SELECT,INSERT ON evidence_assessments TO hydro_app;

GRANT SELECT,INSERT ON assessment_evidence TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON incidents TO hydro_app;

GRANT SELECT,INSERT ON incident_events TO hydro_app;

GRANT SELECT,INSERT ON incident_evidence TO hydro_app;

GRANT SELECT,INSERT ON incident_links TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON work_orders TO hydro_app;

GRANT SELECT,INSERT ON work_order_actions TO hydro_app;

GRANT SELECT,INSERT ON repair_records TO hydro_app;

GRANT SELECT,INSERT ON verification_records TO hydro_app;

GRANT SELECT,INSERT ON verification_evidence TO hydro_app;

GRANT SELECT,INSERT,UPDATE ON citizen_complaints TO hydro_app;

GRANT SELECT,INSERT ON complaint_status_events TO hydro_app;

GRANT SELECT,INSERT ON audit_logs TO hydro_app;

GRANT SELECT,INSERT ON idempotency_records TO hydro_app;

GRANT SELECT,INSERT ON domain_events TO hydro_app;

GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO hydro_app;


-- Zone membership is part of each endpoint FK, not a service-only assertion.
ALTER TABLE network_junctions ADD UNIQUE(organization_id,zone_id,id);
ALTER TABLE pipe_segments ADD FOREIGN KEY(organization_id,zone_id,from_junction_id)
 REFERENCES network_junctions(organization_id,zone_id,id);
ALTER TABLE pipe_segments ADD FOREIGN KEY(organization_id,zone_id,to_junction_id)
 REFERENCES network_junctions(organization_id,zone_id,id);
ALTER TABLE pipe_segments ADD CHECK(ST_XMin(geometry)>=-180 AND ST_XMax(geometry)<=180
 AND ST_YMin(geometry)>=-90 AND ST_YMax(geometry)<=90);
CREATE FUNCTION hydro_pipe_endpoints() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM network_junctions a,network_junctions b
 WHERE a.id=NEW.from_junction_id AND b.id=NEW.to_junction_id
 AND a.organization_id=NEW.organization_id AND b.organization_id=NEW.organization_id
 AND ST_Equals(a.point,ST_StartPoint(NEW.geometry)) AND ST_Equals(b.point,ST_EndPoint(NEW.geometry)))
 THEN RAISE EXCEPTION 'endpoint geometry mismatch' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER consistent_pipe_endpoints BEFORE INSERT OR UPDATE ON pipe_segments
 FOR EACH ROW EXECUTE FUNCTION hydro_pipe_endpoints();
CREATE FUNCTION hydro_referenced_junction() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF (NOT ST_Equals(OLD.point,NEW.point) OR OLD.zone_id<>NEW.zone_id) AND EXISTS
 (SELECT 1 FROM pipe_segments WHERE from_junction_id=OLD.id OR to_junction_id=OLD.id)
 THEN RAISE EXCEPTION 'referenced junction requires reviewed graph edit' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER protect_referenced_junction BEFORE UPDATE ON network_junctions
 FOR EACH ROW EXECUTE FUNCTION hydro_referenced_junction();
