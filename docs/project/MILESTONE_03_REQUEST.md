# HYDROOVERITY — M03 COMPLETE BACKEND FOUNDATION IMPLEMENTATION

## ROLE AND ENGINEERING AUTHORITY

You are joining HYDROOVERITY as its:

- Principal Backend Engineer
- Senior Python/FastAPI Engineer
- PostgreSQL Database Architect
- Application Security Engineer
- Authentication and Authorization Engineer
- API Contract Engineer
- Distributed Transaction and Data Integrity Engineer
- Automated Testing Engineer
- DevOps and Development Environment Engineer
- Technical Code Reviewer

You are responsible for designing, implementing, executing, testing and documenting the M03 backend milestone to professional engineering standards.

Do not produce a theoretical report instead of working application code.

Do not build superficial placeholders that appear functional but do not persist or enforce real behavior.

Your objective is a secure, usable and reproducible backend foundation for a serious water-infrastructure operations application.

---

# 1. PROJECT IDENTITY AND CURRENT STATE

**Project:** HYDROOVERITY

**Team:** TARK

**Problem:** SIH26254 — Development of Indigenous Leak Detection Sensor Systems for Operation & Maintenance of Water Supply Pipelines

**Ministry:** Ministry of Jal Shakti

**Category:** Hardware

**Mission:** Find the leak. Understand the evidence. Verify the repair.

**Repository:**

https://github.com/siddalakarthik/HYDROOVERITY-SIH26254

**Default branch:** main

**GitHub issue:** #3 — M03 Backend Foundation

The following milestones are already completed and merged:

- M01 — GitHub Foundation
- M02 — Website Architecture
- M05 — Scientific Simulations
- M08 — Digital Hardware Engineering

The SIH online-screening PPT has already been submitted.

The explanation video is paused.

No physical hardware, public infrastructure actuation, paid cloud deployment or hardware purchase is authorized.

Do not modify approved simulation results, engineering CAD or component-cost evidence.

M03 is now explicitly authorized.

## Existing architecture

The system contains:

**HYDRO-WATCH**

Hydraulic pressure/flow monitoring and intermittent-supply state qualification.

**GUARD-5**

A proposed non-pressure-bearing external joint collar with exactly five independent wetness channels:

- COLLAR_A
- COLLAR_B
- COLLAR_C
- COLLAR_EXT
- COLLAR_BYPASS

**HYDRO-EAR**

Two pipe-contact acoustic channels acquired using one physical stereo sampling clock.

**Evidence qualification**

Records observations, fault states, uncertainty, candidate interpretations and unresolved outcomes.

**HYDRO-VERIFY**

Tracks incidents, field investigations, repairs and evidence-based verification.

M03 implements the persistent application and identity foundation supporting these subsystems.

It does NOT fabricate sensor readings or automatically claim physical leak detection.

---

# 2. MANDATORY REPOSITORY INSPECTION

Before implementation, read the existing approved files.

At minimum:

```text
AGENTS.md

docs/project/HYDROOVERITY_MASTER_CONTEXT.md
docs/project/ROADMAP.md
docs/project/M03_M04_IMPLEMENTATION_SEQUENCE.md

docs/architecture/SYSTEM_ARCHITECTURE.md
docs/architecture/DATABASE_DESIGN.md
docs/architecture/API_CONTRACTS.md
docs/architecture/openapi-design.json
docs/architecture/AUTH_SECURITY_AND_PRIVACY.md
docs/architecture/ROLE_PERMISSION_MATRIX.md
docs/architecture/DOMAIN_STATE_MACHINES.md
docs/architecture/DATA_CONTRACTS_AND_PROVENANCE.md

data/schemas/m02-database-design.json
data/schemas/m02-api-inventory.json

docs/deployment/DEPLOYMENT_AND_STACK_DECISIONS.md
docs/testing/M02_ACCEPTANCE_AND_TEST_PLAN.md
docs/decisions/DECISION_LOG.md

docs/requirements/SYSTEM_REQUIREMENTS.md
docs/requirements/WEBSITE_REQUIREMENTS.md
```

Inspect repository layout, Git status, current main commit, CI workflow and existing Python tooling.

Follow the authoritative M02 contracts rather than creating a new incompatible architecture.

**Important:** M02's 57 proposed database tables and 117 API operations describe the full target system. They do not authorize implementing every operation during M03.

Create a traceability matrix showing which canonical contracts M03 implements and which remain intentionally deferred.

Do not create duplicate routes, parallel schemas, inconsistent role definitions or undocumented status values.

Where a genuine contract inconsistency blocks implementation, document it, propose the smallest safe correction, update canonical sources and regression checks together, and make the change reviewable.

Do not silently change the approved security model.

---

# 3. GIT AND WORKSPACE SAFETY

Create a dedicated feature branch:

`feature/m03-backend-foundation`

Use current remote main as the starting point.

Before branching:

1. Inspect `git status`.
2. Inspect local and remote branch names.
3. Fetch remote updates.
4. Confirm the latest approved main is available.
5. Preserve any uncommitted work.
6. Create an isolated worktree if the current checkout contains another milestone's changes.

Never force-push main.

Never reset or discard another milestone's files.

Keep M03 code separate from M05 simulations and M08 engineering work.

Reference issue #3.

Commit tested implementation checkpoints with clear messages.

---

# 4. CHOOSE AND LOCK THE TECHNOLOGY STACK

Use the approved technical architecture.

## Backend

- Python 3.12
- FastAPI
- Pydantic 2
- SQLAlchemy 2
- Alembic
- psycopg 3
- PostgreSQL 17
- Compatible PostGIS extension
- Argon2id password hashing
- Pytest
- HTTPX or a suitable FastAPI test client
- Docker Compose
- Local HTTPS reverse proxy

Use async database access if the selected driver/session architecture supports it reliably. Otherwise choose a correctly managed synchronous implementation rather than mixing both unsafely.

Avoid unnecessary microservices.

Do not use Firebase or Supabase Auth to replace the frozen authentication design.

Do not implement a second identity system in Next.js.

Do not introduce MongoDB or SQLite as the production datastore.

SQLite must not substitute for PostgreSQL in tenant-isolation and migration acceptance tests.

## Environment setup

Inspect installed:

- Python interpreters
- Docker Engine / Docker Desktop
- Docker Compose
- PostgreSQL client tools
- Existing project environments
- Available ports
- Existing requirements or lockfiles

Previous milestones encountered binary compatibility problems when Python 3.14 used Python 3.12 scientific packages.

Use a **fresh Python 3.12 backend virtual environment**.

Never copy compiled binary packages from another interpreter version.

Select maintained, mutually compatible dependency versions.

Pin reproducible dependencies and record versions.

Use separate environments for:

- M03 backend
- M05 scientific simulation
- M08 CAD generation
- M02 isolated OpenAPI validation

Do not install the scientific or CAD stack into the backend unnecessarily.

If Docker is unavailable, investigate supported installation or documented native alternatives. Do not claim container checks passed unless Docker actually ran.

---

# 5. REPOSITORY STRUCTURE

Use the existing repository conventions.

Create a maintainable backend structure, adapting to existing directories rather than duplicating them.

Suggested internal organization:

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      errors.py
      logging.py
      lifespan.py
    db/
      base.py
      session.py
      models/
      migrations/
    schemas/
    api/
      v1/
    services/
      authentication/
      authorization/
      organizations/
      complaints/
      incidents/
      work_orders/
      repairs/
      verification/
    repositories/
    middleware/
    tests/
  scripts/
  pyproject.toml
  README.md

infra/
  compose/
  proxy/
```

This is a suggested layout, not permission to restructure unrelated source trees.

Prefer cohesive modules with clear dependencies.

Use typed Python and consistent naming.

Avoid enormous router files, service classes doing everything, and circular dependencies.

Use SQLAlchemy models for persistence, Pydantic models for wire contracts, services for domain decisions and explicit repository/query functions.

Do not blindly generate ORM models from M02's JSON catalogue without reviewing constraints and relationships.

---

# 6. DATABASE FOUNDATION

This is a critical part of M03.

Create real PostgreSQL schemas and executable Alembic migrations.

## Required principles

- UUID primary keys.
- UTC timestamp storage.
- Versioned mutable records.
- Strong uniqueness constraints.
- Explicit foreign keys.
- Composite same-tenant foreign keys.
- Referential integrity.
- Appropriate indexes.
- Transaction management.
- Append-only history where specified.
- Role-based access restrictions.
- Row-Level Security as defense in depth.

Tenant-owned records require `organization_id`.

Cross-tenant references must be impossible even if application validation contains a defect.

Use database constraints wherever the invariant is expressible in SQL.

Do not rely exclusively on Python validation for relational integrity.

## Stage A — Identity, governance and transactions

Implement the required foundational tables:

```text
organizations
users
organization_memberships
roles
permissions
role_permissions
role_assignments
sessions
invitations
account_recovery_tokens
audit_logs
idempotency_records
domain_events
```

Use exactly the canonical columns, types, relationships and uniqueness rules from the M02 design unless a documented correction is essential.

Seed immutable global role/permission catalogues deterministically.

Do not seed real administrator passwords or identities into the repository.

## Stage B — Core operational data

Implement the parent/child closure necessary for:

```text
water_zones
citizen_complaints
complaint_status_events

incidents
incident_events
incident_links
incident_evidence

work_orders
work_order_actions

repair_records
verification_records
verification_evidence

evidence_records
evidence_assessments
assessment_evidence
```

Use the actual canonical foreign-key relationships.

Some of these tables reference entities that belong to later scientific milestones.

Solve these dependencies safely.

Acceptable choices include:

- Creating the necessary parent schema early when there is a clear reason.
- Guarding future optional foreign-key columns with `CHECK(column IS NULL)` until their referenced table and composite FK can be introduced.
- Using staged constraints and migrations with a documented enablement sequence.

Unacceptable choices include:

- Allowing arbitrary dangling IDs.
- Omitting tenant ownership.
- Silently weakening foreign keys.
- Creating fake simulation runs simply to satisfy a relationship.
- Accepting an untyped JSON object instead of the canonical relation without review.

Do not introduce all 57 tables merely to avoid thinking through migration dependencies.

## Stage C — Minimal pipeline records

M03 must support genuine basic pipeline/service-area persistence.

Implement the required water-zone data and a small, correct pipeline graph slice where the canonical M02 model allows it:

- Network junctions.
- Pipe segments.
- Same-tenant endpoints.
- Valid coordinate geometry.
- Positive pipe diameter and length.
- Explicit surveyed versus geometry-derived length information.
- Valid zone relationships.

Use PostGIS WGS84 coordinates.

Do not use degree differences as metre distances.

Use PostGIS geography/geodesic calculations where required.

Do not invent missing survey accuracy.

Full GIS editing and acoustic path-coverage analytics remain deferred.

## Migration verification

Prove:

1. Empty database → latest migrations.
2. Migration rerun does not corrupt state.
3. Schema matches implemented models.
4. Required extensions are installed.
5. Unique/FK/check constraints reject invalid data.
6. Restricted application role cannot bypass tenant controls.
7. A disposable migration rollback or forward-repair path works.
8. Existing populated tables survive safe later revisions.

Use a disposable test database for destructive migration tests.

Never drop an unknown database or user data.

---

# 7. SECURE DATABASE ACCESS AND RLS

Implement database-level tenant isolation.

Use separate database roles for:

- Schema migration/ownership.
- Application runtime.
- Test setup, where needed.

The application runtime role must not own the protected tenant tables or have `BYPASSRLS`.

Apply RLS to tenant-scoped tables.

Use transaction-local tenant context and explicit membership/permission checks.

Do not trust a client-supplied tenant ID, role header, or application workspace mode.

Never use session-persistent RLS context that can leak between pooled connections.

Clear transactional context reliably.

Every request must enforce:

1. Authenticate current identity.
2. Verify active membership.
3. Bind requested organization.
4. Check explicit permission.
5. Load the requested resource under organization scope.
6. Check ownership or current assignment where applicable.
7. Check version and lifecycle transition.
8. Persist transaction, audit and event atomically.

## Mandatory negative tests

Set up independent organizations A and B.

Test that:

- A user from A cannot read B's records.
- A user from A cannot mutate B's records.
- Valid-looking resource UUIDs do not bypass tenant checks.
- Nested cross-tenant IDs are rejected.
- Connection pooling cannot leak the previous request's tenant context.
- Direct runtime-role SQL cannot read cross-tenant rows.
- A user with multiple memberships gets only currently authorized scope.
- Membership revocation immediately invalidates access.
- ADMIN does not inherit ENGINEER or EVALUATOR permissions.
- A TECHNICIAN cannot see arbitrary incidents or other workers' tasks.
- A CITIZEN cannot see another citizen's complaint.
- Background operations do not run with unrestricted tenant access.

Prove actual isolation against PostgreSQL, not just mocked permission functions.

---

# 8. AUTHENTICATION — FASTAPI IS THE SINGLE OWNER

Implement the canonical M02 session authentication model.

Do not use localStorage JWT authentication.

Do not use NextAuth as an independent identity owner.

Do not store plain-text passwords.

Use Argon2id with appropriately benchmarked parameters meeting the repository's minimum OWASP requirements.

## Sessions

Use cryptographically secure 256-bit opaque session tokens.

Store only token verifiers/hashes.

Cookie contract:

`__Host-hydro_session`

Cookie attributes:

- Secure
- HttpOnly
- Path=/
- SameSite=Lax
- No Domain

Use an HTTPS-capable local development proxy.

Do not weaken production cookie behavior merely to simplify local HTTP testing.

Apply:

- 30-minute idle expiration.
- 12-hour absolute expiration.
- Ten-minute recent reauthentication for sensitive governance.
- Rotation on login and relevant privilege changes.
- Revocation on logout, password reset and account suspension.

Authenticated responses must use `Cache-Control: no-store`.

Never cache Set-Cookie responses.

## CSRF protection

Implement:

`GET /api/v1/auth/csrf`

It must establish or refresh a bounded preauthentication session and provide a synchronizer CSRF token.

All cookie-authenticated mutations, including login and registration, require valid CSRF and same-origin checks.

Do not use SameSite cookies as the only CSRF defense.

Reject cross-origin mutation attempts.

Do not exempt password recovery, logout or public registration from the documented policy.

## Implement all canonical authentication operations

```text
GET  /api/v1/auth/csrf
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/recovery
POST /api/v1/auth/reset
POST /api/v1/auth/verify
POST /api/v1/auth/invitation-accept
```

Use the exact canonical request/response schemas.

### Registration

- Normalize email.
- Enforce uniqueness.
- Permit self-registration only as CITIZEN for an enabled utility.
- Do not allow public staff registration.
- Do not allow public EVALUATOR registration.
- Existing-account retry must never overwrite password or memberships.
- Use generic responses preventing account enumeration.
- No automatic authenticated session for an unverified account.

### Login

- Validate current credentials every attempt.
- Verify user/account status.
- Apply rate limits.
- Revoke/rotate the presented session.
- Rotate CSRF state.
- Protect against password-reset/login races.
- Never replay an old successful Set-Cookie response.

### Logout

- Revoke the presented session.
- Clear the cookie.
- Support only the bounded, CSRF-checked revoked-session cleanup behavior described in M02.
- Never accidentally restore a session.

### Recovery

- Return generic responses for known and unknown identities.
- Enforce bounded cooldowns.
- Generate purpose-bound expiring tokens.
- Store only token verifiers.
- Never reveal an existing token.

### Password reset

- Consume token exactly once.
- Update the Argon2id password hash atomically.
- Revoke all authenticated sessions.
- Do not automatically log the user in.
- Reject concurrent replay.

### Email verification

- Enforce purpose and expiration.
- Consume token atomically.
- Activate only the intended account state.
- Do not grant unrelated roles.

### Invitation acceptance

- Require matching verified global identity.
- Trust tenant and role only from the server-created invitation.
- Reject replay.
- Never allow evaluator self-grant.

## Authentication idempotency rules

Do NOT apply ordinary tenant business idempotency receipts to authentication.

Reject `Idempotency-Key` on these canonical auth operations as documented.

Do not cache passwords, tokens, secret-bearing responses or password-derived request fingerprints.

Implement the operation-specific retry and replay rules in:

`docs/architecture/AUTH_SECURITY_AND_PRIVACY.md`

These rules are normative.

---

# 9. CURRENT USER AND ORGANIZATION APIs

Implement the canonical current-user routes:

```text
GET    /api/v1/me
PATCH  /api/v1/me
GET    /api/v1/me/memberships
GET    /api/v1/me/sessions
DELETE /api/v1/me/sessions/{session_id}
```

Global account ownership must work independently of an active organization membership.

Use safe DTOs.

Never expose session secrets or password hashes.

Implement the essential public and organization routes:

```text
GET /api/v1/public/utilities/{slug}
GET /api/v1/public/project-status

GET /api/v1/orgs/{organization_id}
GET /api/v1/orgs/{organization_id}/memberships
GET /api/v1/orgs/{organization_id}/audit-logs
```

Implement the canonical scoped admin operations for:

- Issuing invitations.
- Assigning permitted roles.
- Changing membership status.

Enforce:

- Recent reauthentication.
- Explicit ADMIN permissions.
- Valid organization ownership.
- No evaluator self-grant.
- Last-active-ADMIN protection.
- Immediate revocation behavior.
- Safe audit records.

Do not implement public contact intake yet. Keep it disabled until its separate project-operator, abuse-control and retention requirements are fulfilled.

---

# 10. CONTROLLED FIRST-ADMIN BOOTSTRAP

A development environment must be usable without inventing default credentials.

Implement a controlled operator-only bootstrap command.

It may create:

- An initial organization.
- An initial verified administrative user.
- The minimum approved role assignments.

Requirements:

- Interactive or securely injected initial credentials.
- No password committed into Git.
- No public HTTP staff-registration endpoint.
- Explicit confirmation of target database.
- Safe handling when bootstrap already occurred.
- Idempotent reference-data seeding.
- Audit the initial privileged setup through an appropriate private operational record.

Do not display generated secrets in CI output.

Document how the owner can create a local organization safely.

Provide a separate nonprivileged deterministic test-data factory for automated tests.

Never seed synthetic citizen reports and describe them as actual field complaints.

---

# 11. LOCAL DEVELOPMENT AND HTTPS

Create a local development environment that the owner can run on Windows.

Use Docker Compose where available.

Recommended services:

- PostgreSQL/PostGIS.
- FastAPI backend.
- Same-origin HTTPS reverse proxy.
- A private development-only authentication-mail adapter or sink, if required.

Use a single backend service, not a microservice mesh.

## Health endpoints

M03 may define restricted operational health routes:

```text
GET /internal/health/live
GET /internal/health/ready
```

These are operational endpoints, not additions to the 117 business operations.

Liveness checks process availability.

Readiness checks database connectivity and migration state with short timeouts.

Do not expose schema details, passwords, stack traces or private diagnostics.

Prefer a restricted internal listener.

## Environment and secrets

Provide an `.env.example` containing placeholders only.

Separate development, testing and future production configuration.

Validate required settings on startup.

Fail closed if a production environment lacks:

- Secure cookie configuration.
- Trusted HTTPS origin.
- Required secrets.
- Safe database principal.
- Proper authentication delivery/rate-limiting infrastructure.
- Required migrations.

Do not invent SMTP credentials.

If email delivery is unavailable, implement a clearly marked private development-only sink and a pluggable adapter, with tests. Never claim a real email was delivered.

A production deployment must not depend on a non-durable debug email log or a development-only password-reset token display.

Do not start a paid deployment.

---

# 12. RATE LIMITING, VALIDATION AND ERROR HANDLING

Implement bounded request throttling for sensitive routes.

Respect the existing M02 proposed policies.

At minimum cover:

- Login attempts.
- Registration.
- Recovery.
- Verification/reset/invitation operations.
- Authenticated business mutations.

Avoid storing raw passwords, secrets or user IP addresses in limiter keys.

Use expiring keyed identifiers and documented privacy-safe controls.

For a single-process local pilot, the bounded in-memory strategy permitted by M02 may be used with explicit limitations.

Do not claim multi-instance enforcement without shared storage.

Document the scale-out requirement.

## API errors

Use consistent structured error responses.

Suggested classes:

- Validation failure.
- Authentication required.
- Permission denied.
- Inaccessible resource.
- Version conflict.
- Idempotency conflict.
- Invalid lifecycle transition.
- Rate limit exceeded.
- Service unavailable.
- Unexpected internal error.

Follow canonical status codes and response schemas.

Avoid sensitive error details.

Ensure:

- 401 is used appropriately for missing/invalid authentication.
- 403 does not leak protected resource details.
- Cross-tenant or inaccessible object IDs follow uniform 404 behavior where M02 requires it.
- Version/body conflicts return the correct conflict response.
- Invalid one-time tokens follow the canonical uniform failure behavior.

Log request IDs with safe metadata.

Do not log request bodies containing passwords, private notes or personal contact information.

---

# 13. IDEMPOTENCY FOR BUSINESS OPERATIONS

Implement the canonical seven-day tenant-business idempotency contract.

For eligible writes:

`Idempotency-Key: <UUID>`

Bind the receipt to:

- Authorized actor.
- Server-validated organization.
- HTTP method.
- Canonical route template.
- Canonical nonsecret request-body hash.

Requirements:

1. First valid request executes once.
2. Same key and same body returns the original safe result/receipt under current authorization.
3. Same key and different body returns conflict.
4. A revoked or reassigned actor cannot use an earlier receipt to regain access.
5. Concurrent same-key requests do not produce duplicates.
6. Failed transactions do not leave false success receipts.
7. Receipt expiry is enforced.
8. No passwords, recovery tokens, device secrets or raw sensitive bodies enter the cache.

Use database uniqueness and transactional locking rather than process-local dictionaries alone.

Do not apply this mechanism to the preauthentication or global self-service operations excluded by M02.

---

# 14. DOMAIN WORKFLOW — CITIZEN COMPLAINT TO VERIFIED REPAIR

This is the most important functional backend outcome of M03.

Implement a genuine persistent vertical slice:

**Citizen → Supervisor → Incident → Work order → Technician → Repair → Independent verification**

The full M07 offline, reporting and notification sophistication is deferred, but the essential backend workflow must really work now.

## A. Citizen complaint

Implement:

```text
POST /orgs/{organization_id}/complaints
GET  /orgs/{organization_id}/complaints
GET  /orgs/{organization_id}/complaints/{complaint_id}
POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups
POST /orgs/{organization_id}/complaints/{complaint_id}/review
```

The last route is supervisor-only.

Use actual canonical prefixes, schemas and authorization conditions.

Citizen rules:

- Verified citizen membership.
- Enabled reporting utility.
- Own complaint creation/read/follow-up only.
- Coarse location representation.
- Explicit consent where required.
- Controlled text lengths and safe input handling.
- No raw exact GPS requirement.
- No access to others' reports.
- No exposure of technician private notes or internal network details.

Complaint tracking numbers are identifiers, not bearer authorization tokens.

Record status events durably.

Do not allow citizens to set internal incident states or reviewer identities.

## B. Incident triage

Implement canonical incident operations:

```text
GET  /orgs/{organization_id}/incidents
POST /orgs/{organization_id}/incidents
GET  /orgs/{organization_id}/incidents/{incident_id}
GET  /orgs/{organization_id}/incidents/{incident_id}/timeline
POST /orgs/{organization_id}/incidents/{incident_id}/transitions
POST /orgs/{organization_id}/incidents/{incident_id}/links
```

Authorized ENGINEER/SUPERVISOR access follows the role matrix.

Only permitted actors may perform lifecycle transitions.

Use the canonical state machine:

```text
NEW
UNDER_REVIEW
INVESTIGATION_REQUIRED
ACCEPTED
DISMISSED
IN_PROGRESS
VERIFICATION_PENDING
RESOLVED
REOPENED
NOT_VERIFIABLE
```

Follow only the edges explicitly permitted in `DOMAIN_STATE_MACHINES.md`.

Every transition must:

- Check current status.
- Check actor permission.
- Check expected version.
- Check required reason/evidence.
- Persist a new immutable history event.
- Persist safe audit metadata.
- Persist a domain event when required.
- Complete atomically.

Do not silently skip intermediate states or bypass guard conditions.

Do not allow a sensor anomaly alone to automatically produce a confirmed leak.

## C. Work-order management

Implement canonical work-order operations for:

- List.
- Create.
- Detail.
- Assigned-worker brief.
- Assignment/reassignment.
- Worker actions.
- Permitted transitions.

Follow:

```text
CREATED
ASSIGNED
ACCEPTED
IN_PROGRESS
BLOCKED
SUBMITTED_FOR_REVIEW
COMPLETED
CANCELLED
```

Use the exact approved transition graph, including guarded reopen/block paths.

Only active valid technicians can be assigned.

On reassignment:

- Increment assignment_version.
- Preserve previous actions.
- Invalidate former assignee access.
- Reject stale worker updates.
- Retain operational history.
- Do not accidentally delete draft records owned by the former worker.

Technicians may only act on currently assigned work.

Technicians cannot grant themselves assignments, cancel completed work or approve their own repair verification.

The worker brief must be privacy-minimized and task-specific.

## D. Repair records

Implement:

```text
POST /orgs/{organization_id}/work-orders/{work_order_id}/repairs
GET  /orgs/{organization_id}/work-orders/{work_order_id}/repairs
```

Check current assignment and lifecycle permissions.

Record:

- Repair actor.
- Work order.
- Actual recorded time.
- Server receipt time.
- Description.
- Materials used.
- Correct source/environment class.
- Immutable history or superseding correction.

Manual repair records are MANUAL evidence.

Do not label a technician's record as physical validation performed by HYDROOVERITY sensors.

Record completion is not proof of leak elimination.

## E. Verification

Implement canonical verification routes:

```text
POST /orgs/{organization_id}/repairs/{repair_id}/verifications
GET  /orgs/{organization_id}/repairs/{repair_id}/verifications
```

Canonical outcomes:

```text
VERIFICATION_PASSED
VERIFICATION_FAILED
NOT_VERIFIABLE
```

Enforce reviewer independence.

A technician must not approve their own repair.

PASSED and FAILED require sufficiently comparable before/after evidence under a documented, tested evidence policy.

If M03 lacks the necessary comparable scientific evidence, the backend must return or persist NOT_VERIFIABLE with a precise reason.

Do not fabricate favorable pressure or flow measurements to make a repair pass.

Do not automatically change an incident to RESOLVED when a work order reaches COMPLETED.

Persist historical verification records append-only.

A new review must supersede the previous record without destroying its evidence.

Scientific automated verification using M05/M06 outputs belongs to later authorized integration.

## F. Manual evidence support

Implement the minimum evidence records and assessments necessary for the operational workflow, following M02.

Separate:

- Citizen report.
- Technician observation.
- Manual investigation note.
- Repair receipt.
- Reviewed evidence assessment.

Use explicit source provenance.

Do not create fake acoustic captures or GUARD-5 sensor observations merely to populate an incident.

Do not allow client-supplied hidden ground-truth fields.

If a data type cannot be represented correctly yet, return a clearly defined unsupported capability rather than a fake successful operation.

---

# 15. PIPELINE AND ZONE DATA

Implement the minimal approved zone and asset routes needed to connect incidents to real stored service areas.

At minimum:

```text
GET  /orgs/{organization_id}/zones
POST /orgs/{organization_id}/zones
GET  /orgs/{organization_id}/zones/{resource_id}
```

Where M03 basic pipeline persistence includes junctions and pipes, implement their corresponding canonical GET/POST/PATCH operations from the M02 inventory.

Do not invent new route names.

Enforce:

- Organization ownership.
- Valid geometry.
- Consistent endpoint references.
- Valid diameter and length.
- Survey-basis metadata.
- Safe versioned updates.
- Correct access permissions.

Store only actual input data or explicitly seeded development fixtures.

Do not use the M05 synthetic network as if it were surveyed public infrastructure.

---

# 16. AUDIT LOGS AND DOMAIN EVENTS

Every sensitive or important business operation must leave trustworthy history.

Implement safe audit records for:

- Membership and role changes.
- Invitation creation/acceptance.
- Complaint review.
- Incident creation and transitions.
- Work-order assignment and reassignment.
- Worker submission.
- Repair recording.
- Verification review.

Audit logs should contain:

- Safe actor reference.
- Organization.
- Action.
- Resource type/ID.
- Server timestamp.
- Request ID.
- Minimal nonsecret metadata.

Do not include:

- Passwords.
- Session cookies.
- Recovery tokens.
- Invitation secrets.
- Raw citizen contact information.
- Unredacted private request bodies.

Use a transactional domain-events/outbox pattern where the existing architecture requires it.

For M03, reliable persistence and deterministic processing are more important than WebSocket streaming.

Do not implement a premature distributed event bus.

Full notifications and SSE belong to their later milestones.

---

# 17. INPUT VALIDATION AND API CONTRACT COMPLIANCE

Use M02's canonical OpenAPI 3.1 design as the public wire contract.

Requirements:

- Correct request schemas.
- Correct response schemas.
- Correct required/optional fields.
- Correct enum values.
- Correct validation errors.
- Correct security schemes.
- Correct status codes.
- Correct UUID and UTC timestamp handling.
- Correct pagination and list envelopes.
- No unknown writable fields allowing role, tenant or provenance injection.

Create a machine-checkable inventory of implemented operations.

For each operation, record:

```text
Operation ID
HTTP method
Route
Required permission
Implemented or deferred
Request schema
Response schema
Persistence tables
Relevant test cases
```

Implement response/request conformance tests for all enabled endpoints.

Do not falsely claim that all 117 API operations are implemented.

Do not rewrite the canonical OpenAPI document to match an incorrect backend implementation.

Fix the implementation to match the reviewed contract unless there is a justified, documented contract change.

Future routes must not advertise success, return mock operational data or create inert records.

---

# 18. TESTING — REQUIRED REAL EVIDENCE

Use pytest and a disposable real PostgreSQL/PostGIS database.

Implement meaningful automated tests.

Prioritize security, correctness and complete workflows over high but meaningless test counts.

## Group A — Environment and migrations

Test:

- Fresh database creation.
- Alembic upgrade.
- Correct required tables.
- Required indexes/constraints.
- PostgreSQL extension availability.
- Test database cleanup.
- Connection lifecycle.
- Invalid configuration handling.
- Readiness failure when DB is unavailable.

## Group B — Authentication

Test:

- Registration.
- Duplicate registration with different submitted password.
- Disabled utility registration.
- Staff-role self-registration rejection.
- Password verification.
- Successful login.
- Incorrect login.
- Session rotation.
- Logout revocation.
- Idle/absolute expiration.
- Session revocation.
- Password reset.
- Expired token.
- Replayed reset token.
- Concurrent reset attempts.
- In-flight login versus password reset.
- Email verification.
- Invitation acceptance.
- Invitation for wrong identity.
- Existing-user invitation.
- Invitation replay.
- No token leakage.
- Correct no-store headers.
- Origin and CSRF enforcement.
- Throttling behavior.

## Group C — Authorization

Test:

- Tenant A versus tenant B.
- Direct SQL RLS denial.
- Multi-membership users.
- ADMIN permissions.
- ENGINEER permissions.
- SUPERVISOR permissions.
- TECHNICIAN assignment limits.
- CITIZEN ownership limits.
- No EVALUATOR inheritance.
- Current membership revocation.
- Suspended users.
- Last-admin protection.
- Nested cross-tenant resources.
- Resource ID enumeration.
- Pooled connection context isolation.

## Group D — Complaints and incidents

Test:

- Own complaint creation/read.
- Other citizen denial.
- Invalid location/content.
- Duplicate idempotency key.
- Conflicting idempotency body.
- Supervisor review.
- Incident creation.
- Valid state transitions.
- Invalid state transitions.
- Missing required reasons.
- Stale If-Match version.
- Audit event creation.
- Atomic rollback.

## Group E — Work orders

Test:

- Supervisor assignment.
- Inactive technician rejection.
- Correct worker brief.
- Unauthorized worker denial.
- Reassignment.
- Old-worker stale action denial.
- Worker acceptance.
- Progress notes.
- Blocking/unblocking.
- Repair receipt.
- Review submission.
- Supervisor acceptance.
- Work completion without scientific leak-verification success.

## Group F — Verification

Test:

- Independent reviewer.
- Worker self-approval denial.
- Missing pre/post evidence.
- NOT_VERIFIABLE outcomes.
- Invalid PASSED without comparability.
- Invalid FAILED without interpretable comparable evidence.
- Append-only review.
- Superseding review.
- Reopen on failed verification where supported.
- No automatic incident resolution from completed work.

## Group G — Concurrency and resilience

Test:

- Concurrent duplicate writes.
- Transaction rollback.
- Database constraint conflicts.
- Deadlock/serialization retry handling where applicable.
- Version conflict.
- Reauthorization on idempotency replay.
- DB restart/readiness recovery.
- Error responses without stack traces.
- No sensitive data in logs.

Use targeted fault-injection tests where helpful.

Tests must assert expected behavior, not simply check for HTTP 200.

Include tests that intentionally attempt unauthorized operations.

Document known gaps and failures.

---

# 19. END-TO-END BACKEND DEMONSTRATION

Create one reproducible integration scenario that uses real API requests and persistent database rows.

The scenario must run against the local development backend.

Required sequence:

1. Controlled operator bootstrap creates a utility organization.
2. A citizen registers and verifies identity.
3. A supervisor exists through the authorized staff provisioning process.
4. A technician accepts a valid invitation.
5. The citizen submits a water-leak complaint.
6. The supervisor reviews it.
7. An incident is created and linked.
8. The supervisor assigns a work order.
9. The technician logs in.
10. The technician receives only their assigned work.
11. The technician records investigation/actions.
12. A repair receipt is created.
13. The work order is submitted and operationally reviewed.
14. An independent reviewer records the appropriate verification result.
15. Where comparable measurements are insufficient, the result is NOT_VERIFIABLE.
16. The citizen retrieves only the public-safe complaint status.
17. Another citizen is denied access to the first citizen's report.
18. Another organization's users cannot read or mutate the incident.
19. The same write retry does not create a duplicate.
20. The full history survives application restart.

Use explicitly labeled synthetic integration fixtures for any example addresses, names or field activities.

Do not represent this as a real municipal repair.

The demonstration must produce reproducible machine-readable test evidence.

Do not build the polished dashboard during M03.

---

# 20. REQUIREMENTS FOR THE DEVELOPMENT API EXPERIENCE

Provide a useful local development interface.

FastAPI's OpenAPI/Swagger interface may be enabled in a development-only controlled environment.

Expose no secrets.

Provide clear local commands for:

- Starting the stack.
- Applying migrations.
- Bootstrapping the organization.
- Preparing test accounts through approved development tooling.
- Running all backend tests.
- Running the operational scenario.
- Inspecting health/readiness.
- Resetting a disposable test database safely.
- Stopping the stack.

Provide a complete README with Windows PowerShell instructions.

Do not assume Bash-specific commands work unchanged on Windows.

Use stable, reproducible commands with explicit working directories.

Ensure a new developer can run the backend without guessing hidden setup steps.

---

# 21. SECURITY RELEASE BOUNDARY

M03 must not be presented as penetration-tested or production certified.

Before any public deployment, the system still needs broader M09 validation, environment review, backup and restore controls, provider configuration and external operational approval.

Do not expose private user accounts or live citizen data on the internet during this milestone.

Do not run unattended public cloud infrastructure.

Do not add real municipal control endpoints.

Do not create public database passwords.

Do not put development reset-token sinks on publicly accessible routes.

A local demo may use fictional people and explicitly identified test organizations.

Never claim physical sensor measurements were received unless actual authorized hardware acquisition took place.

---

# 22. EXPLICITLY DEFERRED FROM M03

Do NOT begin the following:

**M04 — Frontend**

- Complete React/Next.js UI.
- Full 46-page website.
- Public dashboards.
- Mobile technician application.

**M05 — Already completed**

- Rewriting simulation engines.
- Retuning benchmark outcomes.
- Changing synthetic truth datasets.

**M06 — Simulation integration**

- Full hydraulic/acoustic/collar live playback.
- Simulation job scheduler.
- Restricted truth evaluation services.
- Real-time simulation monitoring.
- Scientific waveform ingestion.

**M07 — Advanced maintenance operations**

- Complete offline vault.
- Geographic work routing.
- Complete notifications and reporting.
- CSV exports.
- External SMS/email delivery.
- Full analytics and escalation automation.

**M08 — Already completed**

- New CAD fabrication release.
- Manufacturing.
- PCB purchasing.
- Field firmware deployment.

**M09 — Future validation**

- Broad browser/E2E security and performance audit.
- Independent penetration testing.
- Production-load verification.

**M10 — Paused**

- Explanation video.
- New animated demo.
- PPT redesign.

Do not claim these capabilities are complete because database columns or placeholder routes exist.

---

# 23. IMPLEMENTATION EXECUTION ORDER

Work in short, verifiable checkpoints within M03.

Do not attempt to implement everything in one enormous uncontrolled change.

## CHECKPOINT 1 — Backend environment

Complete:

- Clean Python 3.12 environment.
- Pinned dependencies.
- Docker/PostGIS setup.
- FastAPI application skeleton.
- Safe configuration.
- Logging/errors.
- Internal health endpoints.
- Test database setup.

Exit only after the app starts and actual database connectivity works.

## CHECKPOINT 2 — Migrations and tenant controls

Complete:

- Initial Alembic migrations.
- Global role/permission catalogue.
- Tenant tables and composite FKs.
- Restricted DB roles.
- RLS.
- Controlled bootstrap.
- Cross-tenant negative tests.

Exit only after a real PostgreSQL security test suite passes.

## CHECKPOINT 3 — Authentication

Complete:

- CSRF bootstrap.
- Sessions.
- Registration/login/logout.
- Recovery/reset/verification.
- Invitations.
- Current user endpoints.
- Rate limiting.
- Sensitive response protections.

Exit only after auth replay, origin and session tests pass.

## CHECKPOINT 4 — Organizations and core assets

Complete:

- Organization and membership endpoints.
- Administrative role controls.
- Audit access.
- Zones.
- Minimal required pipeline records.
- Relevant access-control tests.

Exit only after real persistence and authorization tests pass.

## CHECKPOINT 5 — Incident management

Complete:

- Citizen complaint routes.
- Supervisor review.
- Incident routes.
- State-machine enforcement.
- Work orders.
- Assignment and reassignment.
- Repair records.
- Manual evidence.
- Verification records.
- Business idempotency.

Exit only after a full database-backed workflow passes.

## CHECKPOINT 6 — Final review and publication

Complete:

- API conformance audit.
- Database constraint audit.
- Regression tests.
- Full operational scenario.
- Documentation.
- Reproduction instructions.
- Final diff review.
- CI.
- PR publication.

Keep checkpoints as reviewable commits where appropriate.

If execution is interrupted, preserve finished files and resume from the last genuinely tested checkpoint.

Do not restart work merely because an agent turn ends.

Do not claim M03 is complete if only the first few checkpoints pass.

---

# 24. CI REQUIREMENTS

Extend the existing GitHub Actions workflow carefully.

Preserve existing checks for:

- M01 repository foundation.
- M02 OpenAPI and design contracts.
- M02 negative design examples.
- M05 numerical simulation tests.
- M05 smoke profile.
- M08 engineering consistency and CAD checks.
- Git whitespace.

Add a separate M03 backend validation job or appropriate isolated workflow.

Run with disposable PostgreSQL/PostGIS where supported by the CI environment.

Ensure M03 testing does not force the CAD, hydraulic and backend dependencies into one massive Python environment.

Required CI categories:

- Backend import/start checks.
- Migration tests.
- Real DB constraint/RLS tests.
- Authentication tests.
- Authorization tests.
- Workflow/integration tests.
- OpenAPI compatibility checks.
- Dependency and secret hygiene checks.
- Whitespace/source integrity.

Do not silently remove other milestone tests to make the new job green.

Use the actual successful run URL as evidence.

---

# 25. ENGINEERING DOCUMENTATION

Create:

`docs/engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md`

Also update relevant existing documentation.

The report must include:

1. Chosen stack and exact versions.
2. Architecture and module organization.
3. Actual PostgreSQL/PostGIS setup.
4. Implemented table inventory.
5. Executed migration history.
6. RLS and tenant authorization design.
7. Authentication and CSRF implementation.
8. Rate limits and retry behavior.
9. Implemented canonical APIs.
10. Domain lifecycle handling.
11. Idempotency and transaction behavior.
12. Incident-to-verification workflow.
13. Test cases actually executed.
14. Failed or incomplete checks.
15. Security limitations.
16. Deferred M04/M06/M07 dependencies.
17. Reproduction commands.
18. GitHub commit/CI information.
19. Remaining issues before public deployment.

Provide:

`docs/testing/M03_ACCEPTANCE_RESULTS.md`

This must distinguish:

- PASS — actually executed.
- FAIL — actually executed and failed.
- BLOCKED — could not execute.
- DEFERRED — not part of M03.
- NOT TESTED — not yet exercised.

Do not mark an acceptance criterion PASS simply because source code exists.

Update the M03 roadmap record appropriately, but do not close issue #3 before owner review and merge.

---

# 26. QUALITY EXPECTATIONS

Write code that another experienced backend engineer can review and maintain.

Prefer:

- Clear module boundaries.
- Explicit dependency injection.
- Small comprehensible service functions.
- Typed request/response contracts.
- Correct database transactions.
- Tested error branches.
- Strong authorization checks.
- Meaningful exception messages.
- Minimal necessary dependencies.
- Safe migration practices.
- Repeatable local startup.
- Good development documentation.

Avoid:

- Huge monolithic files.
- Fake JSON database persistence.
- Placeholder endpoints.
- Unverified SQL queries.
- Wildcard permissions.
- Client-provided role authority.
- Frontend-only security.
- `except Exception: pass`.
- Disabling CSRF to make tests succeed.
- Weakening RLS for convenience.
- Raw password logs.
- Exposing reset/invitation tokens in responses.
- Mocked tests falsely described as real PostgreSQL integration tests.
- Premature infrastructure.
- Committing secrets.
- Removing scientific limitations.
- Large unrelated refactors.

Read only relevant documentation at each checkpoint rather than repeatedly scanning the entire repository.

Avoid excessive progress narration.

Use tokens primarily for correct implementation, testing and debugging.

---

# 27. GITHUB PUBLICATION

When the backend work passes required checks:

1. Review all changed files.
2. Review the dependency lock and licenses.
3. Search for accidentally committed secrets.
4. Verify no sensitive local database exports are staged.
5. Verify migrations and test results.
6. Verify canonical API compatibility.
7. Run all existing project checks.
8. Commit completed M03 changes.
9. Push the feature branch.
10. Open a pull request against main.
11. Link issue #3.
12. Verify CI.

Do not merge automatically.

Do not close the issue automatically.

Do not deploy publicly.

If security-critical checks fail, do not present the milestone as completed.

Instead, fix the failures or clearly document the remaining blockers.

---

# 28. REQUIRED FINAL RESPONSE

When your implementation is finished, return a structured engineering report with the following sections.

### A — Environment

Which interpreter, dependency versions, database, PostGIS, reverse proxy and Compose configuration actually work?

### B — Database

Which tables and constraints were implemented?

Did the Alembic migrations execute successfully?

Did RLS tests pass against a real PostgreSQL database?

### C — Authentication

Which routes work?

Did CSRF, token replay, session rotation, recovery/reset and invitation tests execute successfully?

### D — API implementation

List the exact number of implemented canonical operations, grouped by domain.

State how many of the 117 full-system operations remain deferred.

Do not invent operation counts.

### E — Domain workflow

Demonstrate the actual sequence:

Citizen complaint → Supervisor review → Incident → Technician assignment → Repair → Independent verification.

Explain the persisted outcome and supporting tests.

### F — Security

Summarize:

- Tenant separation.
- Citizen ownership.
- Worker assignment.
- Role restrictions.
- Database RLS.
- Idempotency.
- CSRF/session protections.
- Audit logs.
- Remaining security risks.

### G — Test results

Provide exact executed test counts.

List all failing, blocked and skipped checks.

Provide the actual CI run.

### H — Local reproduction

Give copy/paste PowerShell commands to:

- Start services.
- Apply migrations.
- Initialize local test accounts.
- Run tests.
- Execute the operational example.
- Stop services.

### I — GitHub

Provide:

- Feature branch.
- Final commit SHA.
- Pull request link.
- CI status.
- Files added/changed.
- Any unresolved conflicts.

### J — Next milestone readiness

Explain exactly which implemented backend APIs M04 can use.

Identify M06/M07 capabilities that still need separate implementation.

Do not start those milestones.

---

# FINAL EXECUTION CONTRACT

You are authorized to IMPLEMENT M03, not merely plan it.

The milestone succeeds only when:

1. A real FastAPI application runs.
2. A real PostgreSQL/PostGIS database persists records.
3. Migrations execute.
4. Authentication and CSRF are enforced.
5. Tenant and role authorization work.
6. Database-level isolation is exercised.
7. Citizens can create private complaints.
8. Supervisors can triage and assign work.
9. Technicians can update only assigned work.
10. Repair and independent verification outcomes are recorded correctly.
11. Idempotent writes resist duplication.
12. The essential end-to-end workflow survives application restart.
13. Automated tests pass.
14. Documentation and reproduction instructions are accurate.
15. The reviewed implementation is published in an M03 pull request.

Do not implement all 117 full-platform APIs merely to inflate completion numbers.

Do not produce a fake functioning backend.

Do not modify M05 or M08 scientific evidence.

Do not start M04/M06/M07/M09/M10.

**Start M03 engineering implementation now. Continue through each verified checkpoint, preserve progress on interruption, and request owner intervention only for genuine environmental or security blockers.**
