# Database design

M02 design for issue #2; **not a deployed migration**. PostgreSQL 17 + PostGIS 3.5 is the conservative pilot version-family recommendation, subject to maintained patch/image selection and integration checks in M03. No database is installed here. This document and the machine-readable field catalogue describe the same reviewed design; the catalogue enables consistency checks, not runtime ORM generation.

## Global invariants

`id uuid PRIMARY KEY`, `created_at timestamptz NOT NULL` apply to every table. Mutable rows also have `updated_at timestamptz NOT NULL` and `version bigint NOT NULL DEFAULT 1 CHECK(version>0)`. UUIDs are opaque, server-generated; timestamps are UTC. No API exposes storage secrets, password hashes or token verifiers. Table-specific columns below are NOT NULL unless marked `?` in the catalogue / nullable in the field listing.

Every tenant table has `organization_id uuid NOT NULL REFERENCES organizations(id)` and `UNIQUE(organization_id,id)`. Each tenant-to-tenant FK is **(organization_id,foreign_id) -> parent(organization_id,id)**, including join/event/attachment rows. User FKs are global only where explicitly named; actions reference tenant memberships. API scope always starts from an active session membership. No frontend filtering substitutes for authorization. Staff membership/role grants are invite/admin controlled; public registration creates CITIZEN only for an enabled utility slug.

FK policy is ON DELETE RESTRICT unless a token/ephemeral-row cleanup procedure explicitly reviews its references. Append-only records cannot UPDATE/DELETE through the application DB role; corrections use supersedes links and new events. All mutable transitions use expected version and transactionally write history, safe audit and outbox rows. UUID existence does not confer permission.

Role and permission catalogs are global immutable reference data; role_assignments are tenant-scoped. Five human roles are ADMIN, ENGINEER, SUPERVISOR, TECHNICIAN, CITIZEN. EVALUATOR is an additional explicit evaluation capability, not a universal administrator or extra portal. An ADMIN does not inherit engineering or evaluator access.

## Spatial and graph rules

Internal junctions are Point(4326); pipe edges LineString(4326), zones optional MultiPolygon(4326), with GiST indexes. Store coordinate geometry as WGS84 longitude/latitude, validate ranges and ST_IsValid; use geography/geodesic ST_Length for metre distances rather than degrees. from/to junctions must belong to the same organization and zone; edge endpoints must be spatially consistent with their junctions using a declared survey tolerance. Do not snap unknown topology into certainty. Positive diameter/length and unequal endpoint IDs are required.

Surveyed path length and geometry-derived length remain separate, with length_basis and uncertainty. A discrepancy requires review, not silent overwrite; the tolerance is survey/configuration data decided later, not an invented physical fact. Access offsets satisfy 0 <= offset_m <= selected path length. Eligible acoustics needs a surveyed simple path, accessible bracketing endpoints and valid pressure/signal/clock metadata. Candidate interval distances are along the path from endpoint A, never arbitrary latitude pins or a radius falsely called accuracy. Branched/mixed/uncertain paths remain ambiguous. Public complaint location is a coarse locality or server-quantized approximately 250 m cell chosen explicitly by the citizen; raw GPS is neither requested nor persisted. No public topology endpoint exists.

## Integrity checks required in M03

- Observation numeric value XOR immutable artifact reference; nonfinite values rejected. Allowed units depend on channel quantity. Receipt time is server time; future-time tolerance/late-arrival classification is configuration, not hardcoded sensor truth.
- Source category and environment combinations: SIMULATION/SIMULATION with run+virtual channel; HARDWARE/LABORATORY or HARDWARE/FIELD with provisioned hardware/config; MANUAL/MANUAL with actor. Payloads cannot choose a credential's source class. Matching device/channel/calibration validity and ownership checked transactionally.
- An event is unique by tenant/channel/event UUID. Exact retry returns original receipt; same ID/different content returns conflict. Source observations are immutable.
- GUARD-5 configuration has exactly one of each A/B/C/EXT/BYPASS and distinct channel identities. Wetness and probe-supervision outcomes are separate; unsupported disconnect supervision remains UNKNOWN.
- Acoustic candidate intervals are empty for abstentions. Qualified candidates require lag/speed/length assumptions, shared-clock metadata, quality reasons and at least one in-bounds interval; interval arrays use start_m <= end_m <= path_length_m. No calibrated probability without calibration reference.
- Typed evidence_records choose exactly one observation/capture/complaint/repair/manual-note source. attachment_links chooses exactly one target FK. Every target is same-tenant and caller-authorized.
- Simulation-mode incidents/work orders cannot link operational observations, and operational reports exclude simulation by default. A manual note does not relabel any linked measurement. SIMULATION assessment requires run reference; all science result environments inherit their inputs.
- Verification PASSED requires before+after evidence and a positive comparability decision; FAILED also requires interpretable comparable evidence, otherwise NOT_VERIFIABLE. Closing work never writes a scientific PASSED result.
- Work-order assignee must be an active TECHNICIAN membership; offline sync rechecks current assignment_version. Incident duplicate links cannot self-link or form redirect cycles; retain both histories.
- One active role assignment per membership/role; last active tenant ADMIN cannot be removed without transferring administration. No public staff/evaluator self-registration.

Some checks span rows and require transaction-safe service validation / deferred triggers in M03. They are not claimed to be enforced by an unexecuted SQL snippet.

## Isolation and scaling

Use application authorization plus PostgreSQL RLS on tenant tables as defense in depth, with `USING` and `WITH CHECK`, non-owner non-BYPASSRLS runtime roles and transaction-local validated tenant/user context. Background jobs establish tenant context explicitly; connection pools must reset context. Global identity tables need separate restricted repositories, not a fake organization column. FORCE RLS where the runtime would otherwise own tables; migration owner remains separate. RLS alone does not express all own/assigned/evaluator checks. Test direct SQL and pooled cross-tenant requests before enabling production traffic. Restricted truth uses a separate schema/object namespace and evaluator/generator DB principals; ordinary API and detector principals have no SELECT/credentials. Operators/backup administrators remain trusted security principals.

Begin with one database and tenant-leading B-tree/GiST indexes listed below. Stable cursor pagination uses (timestamp,id), limit 50/max 100. No Timescale, Kafka, Redis cluster or sharding now. Measure observation volume/EXPLAIN plans before partitioning by time; preserve global event-id uniqueness if partitioning is later introduced. Backups include PostGIS metadata and private objects, encrypted with restore tests. Retention defaults below are proposed pilot policy, not a claim of legal compliance; owner review precedes a real deployment.

## Entity catalogue — 56 retained tables

### organizations

Utility tenant and safe public slug

- Ownership/classification: global / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `name text NOT NULL`; `public_slug text NOT NULL`; `status text NOT NULL`; `retention_policy jsonb NOT NULL`; `public_reporting_enabled boolean NOT NULL`.
- Foreign keys: None.
- Uniqueness beyond PK/tenant identity: public_slug
- Indexes: PK plus listed uniqueness
- Retention: Archive by owner-approved offboarding; no cascade deletion of tenant history. Hold/export/purge checklist before deletion.
- Evidence relationship: No direct scientific source; operational metadata only.

### users

Global human identity; never implicitly an employee

- Ownership/classification: global / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `email_normalized text NOT NULL`; `display_name text NOT NULL`; `password_hash text NOT NULL`; `email_verified_at timestamptz NULL`; `deactivated_at timestamptz NULL`.
- Foreign keys: None.
- Uniqueness beyond PK/tenant identity: email_normalized
- Indexes: PK plus listed uniqueness
- Retention: Deactivate immediately/revoke sessions; minimize or pseudonymize personal fields after 30 days of approved erasure when no required evidence/hold. Retain nonidentifying references.
- Evidence relationship: No direct scientific source; operational metadata only.

### organization_memberships

Identity-to-tenant binding and suspension

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `user_id uuid NOT NULL`; `status text NOT NULL`; `suspended_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); user_id -> users (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,user_id
- Indexes: organization_id,status,user_id
- Retention: Deactivate immediately/revoke sessions; minimize or pseudonymize personal fields after 30 days of approved erasure when no required evidence/hold. Retain nonidentifying references.
- Evidence relationship: No direct scientific source; operational metadata only.

### roles

Fixed role catalogue; EVALUATOR is an extra grant, not another portal

- Ownership/classification: global / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `code text NOT NULL`; `description text NOT NULL`.
- Foreign keys: None.
- Uniqueness beyond PK/tenant identity: code
- Indexes: PK plus listed uniqueness
- Retention: Version-controlled reference catalogue; retire entries instead of deleting grants/history.
- Evidence relationship: No direct scientific source; operational metadata only.

### permissions

Versioned allow-listed action catalogue

- Ownership/classification: global / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `code text NOT NULL`; `description text NOT NULL`.
- Foreign keys: None.
- Uniqueness beyond PK/tenant identity: code
- Indexes: PK plus listed uniqueness
- Retention: Version-controlled reference catalogue; retire entries instead of deleting grants/history.
- Evidence relationship: No direct scientific source; operational metadata only.

### role_permissions

Role-to-action catalogue; no wildcard permissions

- Ownership/classification: global / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `role_id uuid NOT NULL`; `permission_id uuid NOT NULL`.
- Foreign keys: role_id -> roles (global reference); permission_id -> permissions (global reference).
- Uniqueness beyond PK/tenant identity: role_id,permission_id
- Indexes: PK plus listed uniqueness
- Retention: Version-controlled reference catalogue; retire entries instead of deleting grants/history.
- Evidence relationship: No direct scientific source; operational metadata only.

### role_assignments

Scoped membership grants, including explicit evaluation authorization

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `membership_id uuid NOT NULL`; `role_id uuid NOT NULL`; `granted_by_id uuid NOT NULL`; `revoked_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); membership_id -> organization_memberships (composite same-tenant); role_id -> roles (global reference); granted_by_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: active membership_id,role_id (partial revoked_at IS NULL)
- Indexes: organization_id,membership_id
- Retention: 1 year append-only security audit by pilot default; redact accidental personal payloads through controlled auditable procedure.
- Evidence relationship: No direct scientific source; operational metadata only.

### sessions

One FastAPI-owned opaque session and preauth CSRF bootstrap

- Ownership/classification: global / SECRET_VERIFIER. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `user_id uuid NULL`; `token_hash bytea NOT NULL`; `csrf_hash bytea NOT NULL`; `auth_level text NOT NULL`; `idle_expires_at timestamptz NOT NULL`; `absolute_expires_at timestamptz NOT NULL`; `reauthenticated_at timestamptz NULL`; `revoked_at timestamptz NULL`.
- Foreign keys: user_id -> users (global reference).
- Uniqueness beyond PK/tenant identity: token_hash
- Indexes: user_id,revoked_at; absolute_expires_at
- Retention: Preauth 10 min; authenticated idle 30 min / absolute 12 h; purge expired/revoked verifier rows after 30 days.
- Evidence relationship: No direct scientific source; operational metadata only.

### invitations

Single-use staff invitation, never a self-selected staff role

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `email_normalized text NOT NULL`; `role_id uuid NOT NULL`; `invited_by_id uuid NOT NULL`; `token_hash bytea NOT NULL`; `expires_at timestamptz NOT NULL`; `accepted_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); role_id -> roles (global reference); invited_by_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: token_hash
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Reset 30 min, verification 24 h, invitation 7 days; single-use verifier; purge expired/used token material after 24 h (audit receipt kept).
- Evidence relationship: No direct scientific source; operational metadata only.

### account_recovery_tokens

Hashed one-use verify-email and password-reset tokens

- Ownership/classification: global / SECRET_VERIFIER. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `user_id uuid NOT NULL`; `purpose text NOT NULL`; `token_hash bytea NOT NULL`; `expires_at timestamptz NOT NULL`; `used_at timestamptz NULL`.
- Foreign keys: user_id -> users (global reference).
- Uniqueness beyond PK/tenant identity: token_hash
- Indexes: user_id,purpose
- Retention: Reset 30 min, verification 24 h, invitation 7 days; single-use verifier; purge expired/used token material after 24 h (audit receipt kept).
- Evidence relationship: No direct scientific source; operational metadata only.

### water_zones

Tenant water-sector boundary and demand accounting definition

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `name text NOT NULL`; `boundary geometry(MultiPolygon,4326) NULL`; `demand_boundary_version text NOT NULL`; `demand_accounting jsonb NOT NULL`; `topology_quality text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: GiST(boundary)
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### network_junctions

Real graph vertices with confidence/access metadata

- Ownership/classification: tenant / SENSITIVE_INFRASTRUCTURE. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `zone_id uuid NOT NULL`; `external_ref text NOT NULL`; `point geometry(Point,4326) NOT NULL`; `topology_quality text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); zone_id -> water_zones (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,external_ref
- Indexes: GiST(point); organization_id,zone_id
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### pipe_segments

Directed surveyed graph edges and independent length estimate

- Ownership/classification: tenant / SENSITIVE_INFRASTRUCTURE. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `zone_id uuid NOT NULL`; `from_junction_id uuid NOT NULL`; `to_junction_id uuid NOT NULL`; `geometry geometry(LineString,4326) NOT NULL`; `material text NOT NULL`; `diameter_mm numeric NOT NULL`; `surveyed_length_m numeric NULL`; `length_uncertainty_m numeric NULL`; `geometry_length_m numeric NOT NULL`; `length_basis text NOT NULL`; `topology_quality text NOT NULL`; `retired_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); zone_id -> water_zones (composite same-tenant); from_junction_id -> network_junctions (composite same-tenant); to_junction_id -> network_junctions (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: GiST(geometry); organization_id,zone_id
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### supply_windows

Observed state intervals, not fictional scheduled pressure

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `zone_id uuid NOT NULL`; `state SupplyState NOT NULL`; `starts_at timestamptz NOT NULL`; `ends_at timestamptz NULL`; `algorithm_configuration_id uuid NOT NULL`; `reason_codes text[] NOT NULL`; `observation_start_at timestamptz NOT NULL`; `observation_end_at timestamptz NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); zone_id -> water_zones (composite same-tenant); algorithm_configuration_id -> algorithm_configurations (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,zone_id,starts_at DESC
- Retention: 2 years after closure; minimize personal content, retain event provenance. Reopened case resets retention clock.
- Evidence relationship: Assessment links source observations through evidence records; corrections append superseding intervals.

### pipe_access_points

Accessible fittings and allowed external pickup positions

- Ownership/classification: tenant / SENSITIVE_INFRASTRUCTURE. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `segment_id uuid NOT NULL`; `offset_m numeric NOT NULL`; `point geometry(Point,4326) NOT NULL`; `access_kind text NOT NULL`; `accessibility text NOT NULL`; `surveyed_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); segment_id -> pipe_segments (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,segment_id; GiST(point)
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### device_installations

Time-bounded device-to-access-point installation history

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `device_id uuid NOT NULL`; `access_point_id uuid NOT NULL`; `installed_at timestamptz NOT NULL`; `removed_at timestamptz NULL`; `orientation_notes text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); device_id -> devices (composite same-tenant); access_point_id -> pipe_access_points (composite same-tenant).
- Uniqueness beyond PK/tenant identity: one active installation per device (partial removed_at IS NULL)
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### devices

Physical or virtual device identity and fixed acquisition profile

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `serial_ref text NOT NULL`; `device_kind text NOT NULL`; `origin_profile AcquisitionEnvironment NOT NULL`; `supervision_capabilities jsonb NOT NULL`; `retired_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,serial_ref
- Indexes: organization_id,device_kind
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: SIMULATION devices cannot become field hardware through ingest payloads; profile changes require new version/identity.

### sensor_channels

Independent wetness/pressure/flow/context channels

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `device_id uuid NOT NULL`; `channel_code text NOT NULL`; `quantity text NOT NULL`; `canonical_unit text NOT NULL`; `electrical_supervision boolean NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); device_id -> devices (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,device_id,channel_code
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### device_configuration_versions

Immutable wiring, source profile and capture configuration

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `device_id uuid NOT NULL`; `version_number integer NOT NULL`; `configuration jsonb NOT NULL`; `configuration_hash text NOT NULL`; `effective_at timestamptz NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); device_id -> devices (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,device_id,version_number
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Retire/version assets; preserve referenced topology/config metadata for evidence lifespan. No hard delete while referenced.
- Evidence relationship: No direct scientific source; operational metadata only.

### calibration_records

Calibration provenance, uncertainty and validity

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `channel_id uuid NOT NULL`; `method text NOT NULL`; `valid_from timestamptz NOT NULL`; `valid_until timestamptz NULL`; `parameters jsonb NOT NULL`; `uncertainty jsonb NOT NULL`; `artifact_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); channel_id -> sensor_channels (composite same-tenant); artifact_id -> observation_artifacts (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,channel_id,valid_from DESC
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Calibration environment and reference measurements recorded in artifact metadata; no invented numeric calibration.

### device_health_events

Health transitions and channel supervision evidence

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `device_id uuid NOT NULL`; `channel_id uuid NULL`; `state DeviceHealth NOT NULL`; `fault_code text NULL`; `observed_at timestamptz NOT NULL`; `reason text NOT NULL`; `observation_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); device_id -> devices (composite same-tenant); channel_id -> sensor_channels (composite same-tenant); observation_id -> sensor_observations (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,device_id,observed_at DESC
- Retention: 30 days raw pilot default; source records/artifacts referenced by evidence pinned for 2 years after case closure; raw payload may redact to immutable hash/tombstone after approved retention.
- Evidence relationship: No direct scientific source; operational metadata only.

### device_credentials

Hashed scoped device/simulator credentials; no human sessions

- Ownership/classification: tenant / SECRET_VERIFIER. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `device_id uuid NOT NULL`; `token_hash bytea NOT NULL`; `allowed_environment AcquisitionEnvironment NOT NULL`; `scope text NOT NULL`; `expires_at timestamptz NOT NULL`; `revoked_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); device_id -> devices (composite same-tenant).
- Uniqueness beyond PK/tenant identity: token_hash
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Preauth 10 min; authenticated idle 30 min / absolute 12 h; purge expired/revoked verifier rows after 30 days.
- Evidence relationship: No direct scientific source; operational metadata only.

### collar_service_tests

External-only service challenge receipt, no drinking-line injection

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `device_id uuid NOT NULL`; `work_order_id uuid NOT NULL`; `performed_by_id uuid NOT NULL`; `channel_code CollarChannel NOT NULL`; `nominal_volume_ml numeric NULL`; `started_at timestamptz NOT NULL`; `response_delay_s numeric NULL`; `response_notes text NOT NULL`; `cross_talk jsonb NOT NULL`; `drain_outcome text NOT NULL`; `source_category SourceCategory NOT NULL`; `environment AcquisitionEnvironment NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); device_id -> devices (composite same-tenant); work_order_id -> work_orders (composite same-tenant); performed_by_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Manual procedure report is distinct from sensor measurements; source context is retained.

### observation_artifacts

Immutable private acoustic/scientific binary object metadata

- Ownership/classification: tenant / RESTRICTED_ARTIFACT. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `storage_key text NOT NULL`; `sha256 text NOT NULL`; `size_bytes bigint NOT NULL`; `media_type text NOT NULL`; `environment AcquisitionEnvironment NOT NULL`; `access_class text NOT NULL`; `deleted_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,storage_key
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 30 days unreferenced raw captures; evidence pins override to 2 years; truth namespace never public; secure purge by policy.
- Evidence relationship: No direct scientific source; operational metadata only.

### sensor_observations

Immutable accepted scalar or artifact-backed observation

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `channel_id uuid NOT NULL`; `collection_time timestamptz NOT NULL`; `receipt_time timestamptz NOT NULL`; `unit text NOT NULL`; `value double precision NULL`; `artifact_id uuid NULL`; `quality text NOT NULL`; `fresh_until timestamptz NOT NULL`; `source_category SourceCategory NOT NULL`; `environment AcquisitionEnvironment NOT NULL`; `device_configuration_id uuid NULL`; `calibration_id uuid NULL`; `simulation_run_id uuid NULL`; `manual_actor_id uuid NULL`; `event_id uuid NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); channel_id -> sensor_channels (composite same-tenant); artifact_id -> observation_artifacts (composite same-tenant); device_configuration_id -> device_configuration_versions (composite same-tenant); calibration_id -> calibration_records (composite same-tenant); simulation_run_id -> simulation_runs (composite same-tenant); manual_actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,channel_id,event_id
- Indexes: organization_id,channel_id,collection_time DESC,id; organization_id,simulation_run_id
- Retention: 30 days raw pilot default; source records/artifacts referenced by evidence pinned for 2 years after case closure; raw payload may redact to immutable hash/tombstone after approved retention.
- Evidence relationship: Canonical source; value XOR artifact, valid category/environment/config combinations; quality flags never omitted.

### acoustic_captures

Paired waveform provenance on a surveyed eligible span

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `endpoint_a_id uuid NOT NULL`; `endpoint_b_id uuid NOT NULL`; `artifact_id uuid NOT NULL`; `sample_rate_hz integer NOT NULL`; `sample_count bigint NOT NULL`; `clock_id text NOT NULL`; `shared_clock boolean NOT NULL`; `captured_at timestamptz NOT NULL`; `pressure_context jsonb NOT NULL`; `channel_quality jsonb NOT NULL`; `environment AcquisitionEnvironment NOT NULL`; `simulation_run_id uuid NULL`; `device_configuration_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); endpoint_a_id -> pipe_access_points (composite same-tenant); endpoint_b_id -> pipe_access_points (composite same-tenant); artifact_id -> observation_artifacts (composite same-tenant); simulation_run_id -> simulation_runs (composite same-tenant); device_configuration_id -> device_configuration_versions (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,captured_at DESC
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Two-channel artifact and shared physical clock required for qualified capture; no arbitrary independent clock equivalence.

### acoustic_location_estimates

Candidate interval(s) or explicit abstention on a captured path

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `capture_id uuid NOT NULL`; `segment_id uuid NOT NULL`; `algorithm_configuration_id uuid NOT NULL`; `outcome AcousticOutcome NOT NULL`; `path_length_m numeric NOT NULL`; `path_length_uncertainty_m numeric NOT NULL`; `effective_speed_m_s numeric NULL`; `speed_uncertainty_m_s numeric NULL`; `lag_s numeric NULL`; `lag_uncertainty_s numeric NULL`; `candidate_intervals jsonb NOT NULL`; `quality_reasons text[] NOT NULL`; `confidence_calibration_ref text NULL`.
- Foreign keys: organization_id -> organizations (global reference); capture_id -> acoustic_captures (composite same-tenant); segment_id -> pipe_segments (composite same-tenant); algorithm_configuration_id -> algorithm_configurations (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,capture_id
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Intervals from endpoint A; no coordinate when unresolved; speed is measured/assumed with uncertainty, not frozen hardware fact.

### evidence_records

Typed source receipt; confirmed wetness is a measurement, not leak origin

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `observation_id uuid NULL`; `capture_id uuid NULL`; `complaint_id uuid NULL`; `repair_id uuid NULL`; `manual_actor_id uuid NULL`; `manual_note text NULL`; `environment AcquisitionEnvironment NOT NULL`; `record_type text NOT NULL`; `supersedes_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); observation_id -> sensor_observations (composite same-tenant); capture_id -> acoustic_captures (composite same-tenant); complaint_id -> citizen_complaints (composite same-tenant); repair_id -> repair_records (composite same-tenant); manual_actor_id -> organization_memberships (composite same-tenant); supersedes_id -> evidence_records (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Exactly one source variant; manual source includes actor+note; explicit environment survives exports.

### evidence_assessments

Versioned interpretations with competing explanations

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `kind EvidenceKind NOT NULL`; `disposition EvidenceDisposition NOT NULL`; `reason_codes text[] NOT NULL`; `explanation text NOT NULL`; `algorithm_configuration_id uuid NULL`; `reviewer_id uuid NULL`; `acoustic_estimate_id uuid NULL`; `workspace_mode WorkspaceMode NOT NULL`; `simulation_run_id uuid NULL`; `supersedes_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); algorithm_configuration_id -> algorithm_configurations (composite same-tenant); reviewer_id -> organization_memberships (composite same-tenant); acoustic_estimate_id -> acoustic_location_estimates (composite same-tenant); simulation_run_id -> simulation_runs (composite same-tenant); supersedes_id -> evidence_assessments (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Links restricted to same dataset mode; assessment_evidence joins source receipts; no physical leak confirmation inferred.

### assessment_evidence

Many-to-many assessment-to-source linkage

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `assessment_id uuid NOT NULL`; `evidence_record_id uuid NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); assessment_id -> evidence_assessments (composite same-tenant); evidence_record_id -> evidence_records (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,assessment_id,evidence_record_id
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Preserves every input receipt without embedding hidden truth.

### incidents

Reviewed operational concern separate from evidence certainty

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `zone_id uuid NOT NULL`; `status IncidentStatus NOT NULL`; `severity text NOT NULL`; `title text NOT NULL`; `owner_id uuid NULL`; `workspace_mode WorkspaceMode NOT NULL`; `simulation_run_id uuid NULL`; `resolved_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); zone_id -> water_zones (composite same-tenant); owner_id -> organization_memberships (composite same-tenant); simulation_run_id -> simulation_runs (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,status,severity,created_at DESC (partial active)
- Retention: 2 years after closure; minimize personal content, retain event provenance. Reopened case resets retention clock.
- Evidence relationship: No direct scientific source; operational metadata only.

### incident_events

Append-only lifecycle/ownership/priority history

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `incident_id uuid NOT NULL`; `actor_id uuid NULL`; `event_type text NOT NULL`; `from_status IncidentStatus NULL`; `to_status IncidentStatus NULL`; `reason text NOT NULL`; `operation_id uuid NOT NULL`; `occurred_at timestamptz NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); incident_id -> incidents (composite same-tenant); actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,incident_id,operation_id
- Indexes: organization_id,incident_id,occurred_at,id
- Retention: 2 years after closure; minimize personal content, retain event provenance. Reopened case resets retention clock.
- Evidence relationship: No direct scientific source; operational metadata only.

### incident_evidence

Traceable incident assessments without editing source evidence

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `incident_id uuid NOT NULL`; `assessment_id uuid NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); incident_id -> incidents (composite same-tenant); assessment_id -> evidence_assessments (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,incident_id,assessment_id
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Cannot mix simulation evidence into an operational incident.

### incident_links

Reconciled duplicate/related incidents; no destructive merge

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `source_incident_id uuid NOT NULL`; `target_incident_id uuid NOT NULL`; `relation text NOT NULL`; `actor_id uuid NOT NULL`; `reason text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); source_incident_id -> incidents (composite same-tenant); target_incident_id -> incidents (composite same-tenant); actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,source_incident_id,target_incident_id,relation
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after closure; minimize personal content, retain event provenance. Reopened case resets retention clock.
- Evidence relationship: No direct scientific source; operational metadata only.

### work_orders

Assignable task and operational completion state

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `incident_id uuid NOT NULL`; `assignee_id uuid NULL`; `status WorkOrderStatus NOT NULL`; `priority text NOT NULL`; `due_at timestamptz NULL`; `instructions text NOT NULL`; `assignment_version bigint NOT NULL`; `workspace_mode WorkspaceMode NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); incident_id -> incidents (composite same-tenant); assignee_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,assignee_id,status,due_at
- Retention: 2 years after closure; minimize personal content, retain event provenance. Reopened case resets retention clock.
- Evidence relationship: No direct scientific source; operational metadata only.

### work_order_actions

Append-only worker notes, transitions and material-use actions

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `work_order_id uuid NOT NULL`; `actor_id uuid NOT NULL`; `action_type text NOT NULL`; `note text NOT NULL`; `materials jsonb NOT NULL`; `operation_id uuid NOT NULL`; `observed_at timestamptz NOT NULL`; `received_at timestamptz NOT NULL`; `base_version bigint NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); work_order_id -> work_orders (composite same-tenant); actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,work_order_id,operation_id
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after closure; minimize personal content, retain event provenance. Reopened case resets retention clock.
- Evidence relationship: No direct scientific source; operational metadata only.

### repair_records

Reported physical work, distinct from verified success

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `work_order_id uuid NOT NULL`; `recorded_by_id uuid NOT NULL`; `performed_at timestamptz NOT NULL`; `description text NOT NULL`; `materials jsonb NOT NULL`; `environment AcquisitionEnvironment NOT NULL`; `supersedes_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); work_order_id -> work_orders (composite same-tenant); recorded_by_id -> organization_memberships (composite same-tenant); supersedes_id -> repair_records (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Worker report cannot by itself claim recovered water or passed verification.

### verification_records

Reviewed before/after comparability and explicit outcome

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `repair_id uuid NOT NULL`; `reviewer_id uuid NOT NULL`; `outcome VerificationOutcome NOT NULL`; `comparability jsonb NOT NULL`; `reason text NOT NULL`; `reviewed_at timestamptz NOT NULL`; `supersedes_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); repair_id -> repair_records (composite same-tenant); reviewer_id -> organization_memberships (composite same-tenant); supersedes_id -> verification_records (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: Requires verification_evidence references and operating-state/quality/unit/calibration checks; NOT_VERIFIABLE is legitimate.

### verification_evidence

Typed before/after observation/assessment linkage

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `verification_id uuid NOT NULL`; `evidence_record_id uuid NOT NULL`; `phase text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); verification_id -> verification_records (composite same-tenant); evidence_record_id -> evidence_records (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,verification_id,evidence_record_id,phase
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: phase BEFORE/AFTER/CONTEXT; reject incompatible environment and incomparable windows for PASSED.

### citizen_complaints

Citizen-owned coarse report and safe public status

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `reporter_id uuid NOT NULL`; `tracking_number text NOT NULL`; `category text NOT NULL`; `description text NOT NULL`; `coarse_area text NOT NULL`; `coarse_point geometry(Point,4326) NULL`; `status ComplaintStatus NOT NULL`; `incident_id uuid NULL`; `consent_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); reporter_id -> organization_memberships (composite same-tenant); incident_id -> incidents (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,tracking_number
- Indexes: organization_id,reporter_id,created_at DESC
- Retention: Personal descriptions/contact-linked content 1 year after closure; anonymize aggregate records, honor holds and approved erasure.
- Evidence relationship: No direct scientific source; operational metadata only.

### complaint_status_events

Public-safe updates separate from internal technician notes

- Ownership/classification: tenant / PERSONAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `complaint_id uuid NOT NULL`; `actor_id uuid NULL`; `status ComplaintStatus NOT NULL`; `public_message text NOT NULL`; `occurred_at timestamptz NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); complaint_id -> citizen_complaints (composite same-tenant); actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Personal descriptions/contact-linked content 1 year after closure; anonymize aggregate records, honor holds and approved erasure.
- Evidence relationship: No direct scientific source; operational metadata only.

### feedback_items

User feedback linked to owned complaint or internal improvement

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `author_id uuid NOT NULL`; `complaint_id uuid NULL`; `summary text NOT NULL`; `description text NOT NULL`; `severity text NOT NULL`; `status text NOT NULL`; `assignee_id uuid NULL`; `github_issue_url text NULL`; `release_ref text NULL`.
- Foreign keys: organization_id -> organizations (global reference); author_id -> organization_memberships (composite same-tenant); complaint_id -> citizen_complaints (composite same-tenant); assignee_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Personal descriptions/contact-linked content 1 year after closure; anonymize aggregate records, honor holds and approved erasure.
- Evidence relationship: No direct scientific source; operational metadata only.

### feedback_events

Traceable triage and resolution of feedback

- Ownership/classification: tenant / PERSONAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `feedback_id uuid NOT NULL`; `actor_id uuid NOT NULL`; `status text NOT NULL`; `resolution_note text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); feedback_id -> feedback_items (composite same-tenant); actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Personal descriptions/contact-linked content 1 year after closure; anonymize aggregate records, honor holds and approved erasure.
- Evidence relationship: No direct scientific source; operational metadata only.

### attachments

Private consented user upload; not raw scientific telemetry

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `owner_id uuid NOT NULL`; `storage_key text NOT NULL`; `sha256 text NOT NULL`; `size_bytes bigint NOT NULL`; `media_type text NOT NULL`; `status AttachmentStatus NOT NULL`; `consent_at timestamptz NOT NULL`; `exif_stripped boolean NOT NULL`; `scan_result text NULL`; `expires_at timestamptz NOT NULL`; `deleted_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference); owner_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,storage_key
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Unattached/quarantine uploads 24 h; clean user photos 90 days after case closure unless explicitly evidence-pinned; delete binaries and retain safe tombstone/digest.
- Evidence relationship: No direct scientific source; operational metadata only.

### attachment_links

FK-safe upload links without arbitrary polymorphic object IDs

- Ownership/classification: tenant / PERSONAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `attachment_id uuid NOT NULL`; `complaint_id uuid NULL`; `work_order_id uuid NULL`; `repair_id uuid NULL`; `service_test_id uuid NULL`; `feedback_id uuid NULL`.
- Foreign keys: organization_id -> organizations (global reference); attachment_id -> attachments (composite same-tenant); complaint_id -> citizen_complaints (composite same-tenant); work_order_id -> work_orders (composite same-tenant); repair_id -> repair_records (composite same-tenant); service_test_id -> collar_service_tests (composite same-tenant); feedback_id -> feedback_items (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: Unattached/quarantine uploads 24 h; clean user photos 90 days after case closure unless explicitly evidence-pinned; delete binaries and retain safe tombstone/digest.
- Evidence relationship: No direct scientific source; operational metadata only.

### notifications

Tenant/user-scoped safe messages and delivery deduplication

- Ownership/classification: tenant / PERSONAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `recipient_id uuid NOT NULL`; `event_id uuid NOT NULL`; `template_code text NOT NULL`; `safe_payload jsonb NOT NULL`; `read_at timestamptz NULL`; `channel text NOT NULL`; `status text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); recipient_id -> organization_memberships (composite same-tenant); event_id -> domain_events (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,recipient_id,event_id,template_code,channel
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: In-app messages/delivery metadata 90 days; no full complaint/photo content in external messages.
- Evidence relationship: No direct scientific source; operational metadata only.

### simulation_scenarios

Immutable published scenario versions and permitted parameter schema

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `name text NOT NULL`; `scenario_version text NOT NULL`; `engine text NOT NULL`; `parameter_schema jsonb NOT NULL`; `assumptions text NOT NULL`; `holdout_class text NOT NULL`; `definition_hash text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,name,scenario_version
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 90 days bulk outputs by default, configs/manifests and curated reproducibility summaries 2 years; holdout truth always restricted.
- Evidence relationship: No ground truth values in operational scenario catalogue; private generator definitions stay restricted.

### simulation_runs

Durable leased job, config/seed and output provenance

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `scenario_id uuid NOT NULL`; `requested_by_id uuid NOT NULL`; `algorithm_configuration_id uuid NOT NULL`; `seed bigint NOT NULL`; `allowed_parameters jsonb NOT NULL`; `configuration_hash text NOT NULL`; `source_commit text NOT NULL`; `started_at timestamptz NULL`; `finished_at timestamptz NULL`; `error_code text NULL`; `evaluation_locked_at timestamptz NULL`; `job_id uuid NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); scenario_id -> simulation_scenarios (composite same-tenant); requested_by_id -> organization_memberships (composite same-tenant); algorithm_configuration_id -> algorithm_configurations (composite same-tenant); job_id -> background_jobs (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,created_at DESC; organization_id,job_id
- Retention: 90 days bulk outputs by default, configs/manifests and curated reproducibility summaries 2 years; holdout truth always restricted.
- Evidence relationship: Parameters shown to user exclude held-out actual positions/labels; separate truth-generation authorization.

### simulation_outputs

Reproducibility manifests and explicitly synthetic artifacts

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `run_id uuid NOT NULL`; `artifact_id uuid NOT NULL`; `output_kind text NOT NULL`; `manifest jsonb NOT NULL`; `complete boolean NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); run_id -> simulation_runs (composite same-tenant); artifact_id -> observation_artifacts (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,run_id,artifact_id
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 90 days bulk outputs by default, configs/manifests and curated reproducibility summaries 2 years; holdout truth always restricted.
- Evidence relationship: Partial/cancelled outputs never masquerade as completed evaluation.

### restricted_simulation_truth

Restricted evaluation schema; no application DB-role SELECT

- Ownership/classification: tenant / RESTRICTED_TRUTH. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `run_id uuid NOT NULL`; `truth_artifact_id uuid NOT NULL`; `truth_hash text NOT NULL`; `sealed_at timestamptz NOT NULL`; `evaluation_release_at timestamptz NULL`; `truth_generation_seed bigint NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); run_id -> simulation_runs (composite same-tenant); truth_artifact_id -> observation_artifacts (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,run_id
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 90 days bulk outputs by default, configs/manifests and curated reproducibility summaries 2 years; holdout truth always restricted.
- Evidence relationship: Detector DB role cannot read this table, object namespace or generator job; evaluator connection separately authorized/audited.

### algorithm_configurations

Immutable method parameters, units and model validity

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `name text NOT NULL`; `algorithm_version text NOT NULL`; `parameters jsonb NOT NULL`; `configuration_hash text NOT NULL`; `validity_notes text NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,configuration_hash
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: 2 years after related incident closure, or longer explicit hold; append-only receipts, corrections supersede. No cascade removal of source evidence.
- Evidence relationship: No direct scientific source; operational metadata only.

### audit_logs

Append-only safe security/administration audit

- Ownership/classification: tenant / SECURITY. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `actor_id uuid NULL`; `action text NOT NULL`; `resource_type text NOT NULL`; `resource_id uuid NULL`; `request_id uuid NOT NULL`; `safe_metadata jsonb NOT NULL`; `occurred_at timestamptz NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference); actor_id -> organization_memberships (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,occurred_at DESC,id
- Retention: 1 year append-only security audit by pilot default; redact accidental personal payloads through controlled auditable procedure.
- Evidence relationship: No direct scientific source; operational metadata only.

### idempotency_records

Scoped request fingerprint and stable result reference

- Ownership/classification: tenant / SECURITY. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `actor_scope text NOT NULL`; `operation_key uuid NOT NULL`; `method text NOT NULL`; `route_template text NOT NULL`; `request_hash text NOT NULL`; `result_resource_id uuid NULL`; `result_status integer NULL`; `expires_at timestamptz NOT NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,actor_scope,method,route_template,operation_key
- Indexes: expires_at
- Retention: 7 days server receipts; offline drafts expire at 72 h, so retries are covered. Tombstone keys without personal request bodies.
- Evidence relationship: No direct scientific source; operational metadata only.

### notification_delivery_attempts

Bounded delivery retries and safe provider outcomes

- Ownership/classification: tenant / SECURITY. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `notification_id uuid NOT NULL`; `attempt_number integer NOT NULL`; `attempted_at timestamptz NOT NULL`; `outcome text NOT NULL`; `next_attempt_at timestamptz NULL`; `provider_reference text NULL`.
- Foreign keys: organization_id -> organizations (global reference); notification_id -> notifications (composite same-tenant).
- Uniqueness beyond PK/tenant identity: organization_id,notification_id,attempt_number
- Indexes: organization_id,id via tenant uniqueness; referenced FKs indexed as needed
- Retention: In-app messages/delivery metadata 90 days; no full complaint/photo content in external messages.
- Evidence relationship: No direct scientific source; operational metadata only.

### domain_events

Transactional outbox and authorized SSE replay cursor

- Ownership/classification: tenant / INTERNAL. Lifecycle: append_only.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `sequence bigint NOT NULL`; `event_type text NOT NULL`; `resource_type text NOT NULL`; `resource_id uuid NOT NULL`; `workspace_mode WorkspaceMode NOT NULL`; `minimum_permission text NOT NULL`; `occurred_at timestamptz NOT NULL`; `safe_summary jsonb NOT NULL`; `published_at timestamptz NULL`.
- Foreign keys: organization_id -> organizations (global reference).
- Uniqueness beyond PK/tenant identity: organization_id,sequence
- Indexes: organization_id,sequence
- Retention: 7 days replay outbox; business history remains in incident/work-order/audit tables beyond replay retention.
- Evidence relationship: Summary carries acquisition context/run reference, no waveform, private contact or truth.

### background_jobs

One durable bounded job queue for reports, acoustic analysis and simulation orchestration

- Ownership/classification: tenant / INTERNAL. Lifecycle: mutable.
- Columns: `id uuid NOT NULL`; `organization_id uuid NOT NULL`; `created_at timestamptz NOT NULL`; `updated_at timestamptz NOT NULL`; `version bigint NOT NULL`; `kind text NOT NULL`; `requested_by_id uuid NOT NULL`; `status RunStatus NOT NULL`; `request_payload jsonb NOT NULL`; `result_artifact_id uuid NULL`; `lease_until timestamptz NULL`; `attempt integer NOT NULL`; `progress numeric NOT NULL`; `cancel_requested_at timestamptz NULL`; `expires_at timestamptz NOT NULL`; `safe_error_code text NULL`.
- Foreign keys: organization_id -> organizations (global reference); requested_by_id -> organization_memberships (composite same-tenant); result_artifact_id -> observation_artifacts (composite same-tenant).
- Uniqueness beyond PK/tenant identity: None; immutable IDs distinguish events.
- Indexes: organization_id,status,created_at (partial queued); lease_until (partial running)
- Retention: 90 days bulk outputs by default, configs/manifests and curated reproducibility summaries 2 years; holdout truth always restricted.
- Evidence relationship: Payload is typed by REPORT/ACOUSTIC_ANALYSIS/SIMULATION; no hidden truth in general queue payload. Creator and current role checks govern downloads.

## Normalization choices

All retained entities serve listed identity, graph, evidence, operations or delivery boundaries. Added joins assessment_evidence, incident_evidence and verification_evidence preserve multiple immutable inputs; attachment_links avoids an unconstrained target ID. A single account_recovery_tokens table handles reset/verification purposes; pipe material is validated reference text until an actual material catalogue is needed. Event histories are distinct because own/public disclosure and lifecycle permissions differ. Domain events provide one durable outbox for SSE and notifications; background_jobs is the one leased queue for reports/analysis/simulation, with no separate queue database. simulation_runs joins its job rather than duplicating job state. The run seed is observation-noise seed only; a separately sealed private truth_generation_seed preserves blind reproducibility without giving detectors reconstructable truth. Future schema migrations must implement and test these constraints, not copy this design as if already deployed.

## Retention policies

All purge operations honor evidence pins and explicit holds, operate in bounded tenant-scoped batches and write safe audit receipts. Ordinary APIs retire/redact records instead of destructive cascade deletion. Personal erasure and evidence preservation may conflict: escalate a documented policy decision rather than claiming universal retention compliance.

Primary references: [PostgreSQL row security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html), [PostGIS installation requirements](https://postgis.net/docs/manual-3.5/postgis_installation.html). Related: [provenance contracts](DATA_CONTRACTS_AND_PROVENANCE.md), [security](AUTH_SECURITY_AND_PRIVACY.md), [state machines](DOMAIN_STATE_MACHINES.md).
