# HYDROOVERITY — MILESTONE 02
# COMPLETE WEBSITE ARCHITECTURE, DATABASE DESIGN, USER EXPERIENCE AND API CONTRACTS

## YOUR ROLE AND AUTHORIZATION

You are the Chief Software Architect, Senior Full-Stack Systems Designer, Database Architect, UI/UX Lead, Security Architect and Quality Assurance Planner for HYDROOVERITY.

**Project:** HYDROOVERITY  
**Team:** TARK  
**Competition:** Smart India Hackathon 2026  
**Problem:** SIH26254 — Development of Indigenous Leak Detection Sensor Systems for Operation & Maintenance of Water Supply Pipelines.

**GitHub repository:**  
https://github.com/siddalakarthik/HYDROOVERITY-SIH26254

**Current status:** Milestone 01 completed. Milestone 02 is now authorized.

The repository already contains substantial project specifications, engineering constraints and architecture documentation.

Your mission is to design the complete software foundation for a genuinely useful, secure, professional water-distribution monitoring and maintenance platform.

This must eventually become a working application used by utility engineers, field technicians, supervisors, administrators and citizens.

Do not design a generic IoT dashboard.

Design a real operational product whose features connect sensors, scientific evidence, investigations, workers, repairs, citizens and performance reporting.

**Milestone 02 authorizes architecture, documentation, interface contracts, UX specifications and database designs. It does not authorize implementation of the actual website, authentication service, database migrations, scientific engines or production deployment.**

---

# PHASE A — INSPECT THE EXISTING REPOSITORY

Before changing anything:

1. Confirm the repository, owner, branch and latest commit.
2. Check the working-tree status.
3. Read `AGENTS.md` completely.
4. Read the authoritative Master Context.
5. Read the existing requirements and architecture documents.
6. Read the data dictionary, threat model, decision log and evidence register.
7. Read the M02 GitHub issue.
8. Identify existing decisions that are frozen.
9. Identify decisions specifically reserved for M02.
10. Check the existing documentation and validation conventions.

Important documents include:

- `docs/project/HYDROOVERITY_MASTER_CONTEXT.md`
- `docs/requirements/WEBSITE_REQUIREMENTS.md`
- `docs/requirements/SYSTEM_REQUIREMENTS.md`
- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/architecture/DATA_DICTIONARY.md`
- `docs/architecture/THREAT_MODEL.md`
- `docs/decisions/DECISION_LOG.md`
- `docs/testing/EVIDENCE_REGISTER.md`
- `docs/project/ROADMAP.md`
- `AGENTS.md`

Do not recreate M01.

Do not discard the existing documents.

Preserve their meaning while producing detailed, consistent M02 design artifacts.

Use GitHub issue #2 as this milestone's traceability reference.

---

# PHASE B — FROZEN HYDROOVERITY HARDWARE ARCHITECTURE

The proposed physical system contains:

## 1. HYDRO-WATCH

Measures or receives relevant hydraulic observations, including pressure and flow, and identifies operating states:

- OFF
- FILLING
- STEADY
- DRAINING
- UNKNOWN

Hydraulic anomalies must not automatically become confirmed leaks.

Unknown customer demand, storage variation and sensor faults must remain competing explanations.

## 2. GUARD-5

A proposed external, non-pressure-bearing diagnostic collar installed at accessible pipe joints.

Exactly five independent wetness channels:

- COLLAR_A
- COLLAR_B
- COLLAR_C
- COLLAR_EXT
- COLLAR_BYPASS

A/B/C monitor protected water-collection compartments.

EXT provides environmental water-exposure evidence.

BYPASS provides evidence about water escaping the intended collection paths.

The concept includes physical separation, guards, drainage and maintenance challenge ports.

**These physical functions remain unvalidated.**

The website must display individual channel observations, diagnostic events, sensor faults and service-test records.

Wetness does not by itself prove that the joint is leaking.

## 3. HYDRO-EAR

Two external acoustic receivers connected to an acquisition system using one shared physical sampling clock.

On eligible simple pipe spans, the system attempts acoustic time-delay localization.

It must preserve:

- Actual available acoustic evidence.
- Pipe length assumptions.
- Wave-speed calibration information.
- Signal quality.
- Possible multipath.
- Candidate location intervals.
- Measurement uncertainty.
- Reasons for unresolved results.

Never present a fabricated exact location.

## 4. EVIDENCE QUALIFICATION

The system combines available observations to propose reasonable interpretations without overstating certainty.

Examples include:

- Hydraulic anomaly.
- Possible local joint leak.
- Environmental wetness.
- Collar collection failure.
- Sensor failure.
- Qualified acoustic candidate interval.
- Insufficient acoustic evidence.
- Unresolved cause.

These categories must not be confused with incident workflow status.

## 5. HYDRO-VERIFY

Supports field investigations, work orders, repairs and comparable before/after verification.

Repair verification may conclude:

- VERIFICATION_PASSED
- VERIFICATION_FAILED
- NOT_VERIFIABLE

Final nomenclature must be consistently designed and documented.

Do not silently equate a closed work order with a scientifically verified repaired leak.

---

# PHASE C — DEFINE THE SOFTWARE PRODUCT

The software platform should be called:

**HYDROOVERITY Operations**

The main application is a professional responsive website.

It must support desktop utility operations and mobile field work.

There must be a meaningful distinction between:

1. Public informational pages.
2. Citizen/customer functionality.
3. Field worker functionality.
4. Maintenance supervisor functionality.
5. Utility engineer functionality.
6. System/organization administration.

Build the architecture for real workflows, not decorative screens.

Every planned interaction must have a defined action, authorization rule, database effect, response and error state.

---

# PHASE D — COMPLETE ROLE-BASED USER EXPERIENCE

## ROLE 1 — CITIZEN / CUSTOMER

Design a simple, mobile-first experience.

Functions:

- Account registration and login.
- Account recovery.
- Submit water-leak complaints.
- Submit low-pressure complaints.
- Submit service-interruption complaints.
- Add a description.
- Enter a rough location.
- Upload a photo with consent.
- Receive a tracking number.
- View their own reports.
- Track complaint progress.
- Receive service updates.
- Add follow-up information.
- Submit feedback after resolution.

Citizens must NOT receive:

- Internal pipeline coordinates.
- Sensitive underground infrastructure topology.
- Private sensor telemetry.
- Other residents' complaints.
- Technician-private notes.
- Internal utility security information.
- Device-control permissions.

Public status should be suitably generalized.

## ROLE 2 — FIELD TECHNICIAN

Design primarily for Android-sized screens.

Functions:

- View assigned tasks.
- See relevant pipe segment and permitted approximate investigation location.
- View suspected leak evidence.
- Read safe investigation instructions.
- Navigate to the site using an authorized external navigation handoff.
- Record inspection results.
- Add photos.
- Add investigation notes.
- Record materials used.
- Record what was repaired.
- Perform GUARD-5 service-test documentation.
- Record comparable post-repair observations.
- Submit work for supervisor review.
- Work with intermittent or temporarily unavailable internet.

Design the actual offline-data policy:

- Which operations can be queued offline?
- Which must require online authorization?
- How do we handle duplicate submissions?
- How do we handle conflicting updates?
- How do we secure locally stored photographs and notes?
- When are cached records deleted?
- How do we show synchronization failures?

## ROLE 3 — MAINTENANCE SUPERVISOR

Functions:

- Incident triage.
- Severity and urgency review.
- Worker assignment.
- Repair scheduling.
- Duplicate-incident reconciliation.
- Escalation of unresolved incidents.
- Repair approval.
- Review of evidence.
- Operational workload dashboard.
- Overdue task management.
- Maintenance performance reporting.

The supervisor must never be forced to accept a scientifically unqualified location.

## ROLE 4 — UTILITY ENGINEER

Functions:

- Pipeline-network explorer.
- Pipe materials and diameters.
- Pipe lengths and accessible fittings.
- Sensor placements.
- Instrumented and uninstrumented coverage.
- Pressure/flow measurements.
- Water-supply state history.
- Acoustic investigation details.
- GUARD-5 diagnostic history.
- Sensor health and calibration.
- Scientific simulation runs.
- Evidence-based incident investigations.
- Repair-comparison reports.
- Network performance analytics.

The engineer should see not only the suspected cause but also why it was suggested.

## ROLE 5 — ADMINISTRATOR

Functions:

- Organization management.
- User invitations.
- Role assignments.
- Account deactivation.
- Device registration records.
- Tenant configuration.
- Access control.
- Audit history.
- Retention settings.
- Integration configuration.
- Security-sensitive event review.

Administrative powers must remain tenant-scoped.

Avoid creating a universal super-admin interface without a clearly justified need.

---

# PHASE E — DESIGN EVERY WEBSITE PAGE

Create a complete information architecture and route inventory.

For each proposed page, specify:

1. Route.
2. Intended roles.
3. Primary user objective.
4. Visible data.
5. Interactive controls.
6. Backend APIs.
7. Required permissions.
8. Loading state.
9. Empty state.
10. Error state.
11. Offline state where relevant.
12. Mobile adaptation.
13. Acceptance criteria.

At minimum, cover:

### Public pages

- Landing page.
- Our Solution.
- How HYDROOVERITY Works.
- GUARD-5 Explanation.
- Acoustic Localization Explanation.
- Benefits and Limitations.
- Public Project Status.
- Citizen Reporting.
- Contact and Feedback.
- Privacy and Terms.

### Authentication pages

- Login.
- Registration where permitted.
- Forgot password.
- Reset password.
- Account verification.
- Profile and session management.

### Internal application

- Operations overview.
- Pipeline network explorer.
- Live and historical monitoring.
- Sensor directory.
- Individual sensor detail.
- GUARD-5 collar detail.
- Acoustic investigation workspace.
- Leak incident center.
- Incident detail and evidence timeline.
- Work-order board.
- Individual work order.
- Repair verification.
- Citizen complaint review.
- Maintenance planning.
- Analytics.
- Reports and exports.
- Simulation laboratory.
- Simulation result viewer.
- Hardware/device diagnostics.
- Feedback and development suggestions.
- Notifications.
- User management.
- Organization settings.
- Audit log.

Do not add unnecessary pages merely to make the website look large.

Consolidate related functions where that improves usability.

---

# PHASE F — PROFESSIONAL UI/UX DESIGN SYSTEM

Create an actual UI/UX design specification.

The visual identity should feel like a modern infrastructure operations platform rather than a typical college IoT dashboard.

Design qualities:

- Professional.
- Clean.
- Technically credible.
- Accessible.
- Fast.
- Mobile responsive.
- Information dense without becoming confusing.
- Suitable for nontechnical field workers.
- Suitable for technical engineers.
- Consistent between all user roles.

Define:

- Brand color tokens.
- Neutral palette.
- Status and severity colors.
- Typography hierarchy.
- Spacing scale.
- Layout grid.
- Navigation structure.
- Sidebar behavior.
- Mobile navigation.
- Data tables.
- Charts.
- Cards.
- Forms.
- Buttons.
- Dialogs.
- Notifications.
- Map legends.
- Incident timelines.
- Loading skeletons.
- Empty states.
- Error states.
- Offline status components.

Do not rely only on red/green colors.

Every important state must also have text and/or icons.

Target WCAG 2.2 AA design where practicable.

English is the initial language. Design the interface for later localization into Telugu and Hindi without claiming completed translation.

Include both dark/light mode considerations, but prioritize a polished default theme rather than doubling all implementation work.

Create high-quality wireframe specifications for at least:

1. Public landing page.
2. Citizen reporting form.
3. Utility command center.
4. Pipeline-network explorer.
5. Acoustic investigation.
6. GUARD-5 diagnostics.
7. Mobile technician work order.
8. Supervisor task board.
9. Simulation laboratory.
10. Incident evidence timeline.

Wireframes may use Mermaid, SVG source or structured Markdown representations appropriate for the existing repository.

Do not include externally copied copyrighted designs or assets.

---

# PHASE G — FINAL DATABASE ARCHITECTURE

Use PostgreSQL with PostGIS for the proposed primary database.

Treat this as a production-oriented design that we can also run locally during development.

Do not install the database or execute migrations yet.

Develop a normalized database model with clear relationships, key fields, nullability, constraints, indexing and authorization implications.

At minimum, investigate these entity groups:

### Identity and organizations

- organizations
- users
- organization_memberships
- roles
- permissions
- role_assignments or equivalent scoped grants
- sessions
- invitations
- account_recovery_tokens

### Pipeline infrastructure

- water_zones
- network_junctions
- pipe_segments
- supply_windows
- pipe_access_points
- device_installations

### Hardware

- devices
- sensor_channels
- device_configuration_versions
- calibration_records
- device_health_events

### Observations and scientific evidence

- sensor_observations
- acoustic_captures
- acoustic_location_estimates
- evidence_assessments
- evidence_records
- observation_artifacts

### Incidents and maintenance

- incidents
- incident_events
- work_orders
- work_order_actions
- repair_records
- verification_records
- incident_links

### Citizen and feedback systems

- citizen_complaints
- complaint_status_events
- feedback_items
- feedback_events
- attachments
- notifications

### Simulations

- simulation_scenarios
- simulation_runs
- simulation_outputs
- restricted_simulation_truth
- algorithm_configurations

### Security

- audit_logs
- idempotency_records or equivalent
- notification_delivery_attempts

You may merge or normalize these conceptual tables where justified.

Do not create dozens of redundant tables merely because they are listed.

For every retained entity, define:

- Purpose.
- Primary key.
- Tenant ownership rules.
- Foreign keys.
- Important columns and types.
- Unique constraints.
- Indexing strategy.
- Lifecycle.
- Privacy classification.
- Deletion/retention rules.
- Relationship to source observations and evidence.

### Tenant isolation

Every tenant-owned record must be traceably bound to an organization.

Cross-organization references must be prohibited.

Avoid relying on frontend filtering for access control.

Design backend authorization checks.

Consider database-level row security as defense in depth, explaining operational complexity.

### Spatial data

Use PostGIS where justified.

Represent actual graph topology with junctions and segments, not merely two arbitrary map pins.

Document:

- Geometry type.
- Coordinate system.
- Segment length consistency.
- Accessible installation points.
- Coverage metadata.
- Branches and uncertain topology.
- Estimated intervals along a segment.
- Public versus internal coordinate exposure.

### Sensor data provenance

An observation must preserve:

- Sensor/channel identifier.
- Collection time.
- Receipt time.
- Unit.
- Value or waveform/artifact reference.
- Quality.
- Freshness.
- Source category.
- Acquisition environment.
- Device or simulator configuration.
- Applicable calibration record.
- Simulation run/scenario where relevant.

Use explicit distinction among simulated, laboratory hardware, field hardware and manually entered evidence.

These distinctions must survive database queries, exports, APIs and reports.

### Ground-truth protection

Simulation ground truth must NOT be included in ordinary sensor payloads.

It must not appear in the same data contracts passed to detection algorithms.

It must be inaccessible from ordinary citizen, worker and utility monitoring APIs.

Design separately authorized evaluation access.

### Database performance

Include index recommendations for:

- Organization and role lookup.
- Device observations by timestamp.
- Active incidents.
- Assigned work orders.
- Spatial pipe searches.
- Simulation runs and provenance.
- Audit-event history.

Avoid speculative enterprise-scale infrastructure.

Design for a modest pilot first, with a documented scaling path.

---

# PHASE H — DEFINE DOMAIN STATE MACHINES

Create separate explicit state machines for:

## 1. Water-supply state

OFF / FILLING / STEADY / DRAINING / UNKNOWN.

Describe state transitions, observation prerequisites, missing-data behavior and urgency exceptions.

## 2. Device-health state

Healthy, degraded, disconnected, stale, calibration-needed and relevant fault categories.

Differentiate a legitimately dry GUARD-5 electrode from an electrically disconnected channel where the proposed hardware supervision supports that distinction.

Do not pretend that this discrimination exists before its electronics are designed.

## 3. Leak-evidence state

Separate observed measurement, suspected explanation, qualified location and unresolved evidence.

Do not automatically mark a physical leak confirmed because a citizen reported it or a sensor became wet.

## 4. Incident lifecycle

Propose clear transitions for:

- New observation.
- Under review.
- Investigation required.
- Accepted incident.
- Work ordered.
- Repair pending.
- Verification pending.
- Resolved.
- Reopened.
- Unable to verify.

Refine the exact enums to avoid ambiguous or redundant states.

## 5. Work-order lifecycle

Created, assigned, accepted, in progress, blocked, submitted for review, completed/cancelled as appropriate.

## 6. Repair-verification outcome

Keep verification outcomes separate from work-order completion.

Use one canonical name for NOT_VERIFIABLE or UNVERIFIABLE and document the choice.

All transitions require authorization, recorded timestamps and auditability.

---

# PHASE I — API CONTRACT DESIGN

Create an OpenAPI 3.1 specification for the future FastAPI backend.

Do not implement the endpoints yet.

Design coherent API groups:

- Authentication and sessions.
- Current user and organization.
- Pipeline assets.
- Water zones.
- Devices.
- Sensor observations.
- Device diagnostics.
- Evidence assessments.
- Acoustic investigations.
- Incidents.
- Work orders.
- Repairs.
- Verification.
- Citizen complaints.
- Feedback.
- Simulations.
- Notifications.
- Reports.
- Administration.

For each endpoint specify:

- HTTP method.
- Path.
- Request model.
- Response model.
- Authorization.
- Tenant scope.
- Input validation.
- Pagination.
- Filtering.
- Error behavior.
- Idempotency where required.

Use stable identifiers and strongly defined units.

Use consistent UTC timestamps.

Define a clear, safe error-response structure.

Never expose sensitive internal error traces.

For operations that modify data, document duplicate-submission prevention, concurrency and audit behavior.

### Sensor ingestion

Design an adapter for future authenticated physical sensor events and a clearly separate simulated data producer.

The simulator must not be able to relabel itself as a verified field sensor merely by setting a request field.

### Live monitoring

Evaluate:

- Server-sent events.
- WebSockets.
- Polling fallback.

Choose one sensible initial architecture.

Document reconnect behavior, missed-event recovery, freshness timestamps, bounded queues and permission checks.

Do not stream unnecessarily large raw acoustic waveforms over a dashboard channel.

### Contract versioning

Define how schema changes will be managed.

Avoid unnecessarily elaborate enterprise API versioning.

---

# PHASE J — AUTHENTICATION AND APPLICATION SECURITY

Propose a specific authentication architecture suitable for Next.js and FastAPI.

Avoid two independent, competing authentication systems.

Evaluate:

- Secure HTTP-only cookies.
- Server-side sessions.
- SameSite policy.
- CSRF protection.
- Password hashing.
- Account recovery.
- Session expiration.
- Rate limits.
- Audit history.
- Permission checks.
- Multi-organization memberships.
- Device identity.
- Future optional MFA.

Select a coherent initial approach and document why.

Define backend enforcement for all role-sensitive operations.

A citizen changing an ID in a URL must never gain access to another citizen's complaint.

An engineer from Organization A must never access Organization B's devices.

A worker must not update a work order merely by guessing its identifier.

### File uploads

Specify:

- Allowed types.
- Size limits.
- Content validation.
- Storage isolation.
- Private download authorization.
- Consent.
- Retention.
- Metadata stripping where appropriate.
- Malware review strategy.
- Auditability.

### Privacy

Avoid exposing sensitive geographic infrastructure detail to public users.

Design for data minimization and appropriate handling of personal data.

Do not claim legal compliance merely because the architecture contains privacy features.

---

# PHASE K — WORKER OFFLINE STRATEGY

Design an implementation-feasible progressive web application strategy.

Important situations:

- Weak mobile connection.
- No internet at a repair site.
- Interrupted photo upload.
- Work-order assignment changed while offline.
- Duplicate form submission.
- Device lost with locally cached data.

The worker must be able to understand:

- Which data is local.
- Which data has synchronized.
- Which data failed to synchronize.
- Which actions require connectivity.

Use explicit operation IDs and server-side idempotency.

Prefer a simple, reliable offline model rather than introducing complex distributed synchronization unnecessarily.

Do not promise full offline GIS mapping without deciding how licensed map tiles and storage limits will work.

---

# PHASE L — SCIENTIFIC SIMULATION INTEGRATION

This milestone does not implement the simulation engines.

However, their integration must be designed now.

We will eventually have three engines:

### Hydraulic engine

EPANET/WNTR-based steady or extended-period network scenarios within the models' validity.

### Acoustic engine

Leak-signal and propagation experiments, candidate localization, error and ambiguity analysis.

### GUARD-5 engine

Simplified water-path, environmental-exposure and fault-state experiments.

Design the complete simulation workflow:

1. User selects an authorized scenario.
2. User specifies allowed input parameters.
3. Backend validates the request.
4. A simulation run record is created.
5. Simulator executes in an isolated job context.
6. Results are saved with provenance.
7. Dashboard receives a completion event.
8. Simulation outputs can be visualized and compared.
9. Restricted ground truth becomes available only in an authorized evaluation workflow.
10. Reports clearly state assumptions and scientific limitations.

Design run-status states, cancellation behavior, progress handling and artifact storage.

Ensure simulation-generated incidents cannot silently contaminate real field-performance reports.

Design a prominent and persistent **SIMULATED DATA** indicator throughout the application.

Do not generate synthetic measurements in this milestone.

---

# PHASE M — PROPOSE THE DEPLOYMENT ARCHITECTURE

Prefer the simplest coherent deployment.

Evaluate:

- Next.js web frontend.
- FastAPI backend.
- PostgreSQL + PostGIS.
- Optional background worker for long-running simulations.
- Private object storage for attachments.
- Local Docker Compose for development.
- A future hosting approach.

`services/ingestion` and `services/notifications` are logical boundaries, not compulsory independently deployed microservices.

Document:

- Network connections.
- Authentication boundaries.
- Database connections.
- API routing.
- Local development.
- Environment configuration.
- Worker queue requirements.
- Database backup considerations.
- Health checking.
- Logging and monitoring.
- Hosting cost implications.

Recommend compatible dependency and runtime versions based on trustworthy official documentation available in your environment.

Do not install packages yet.

Do not provision paid services.

Do not deploy the website.

Do not configure production credentials.

---

# PHASE N — COMPLETE M02 DOCUMENTATION DELIVERABLES

Create or update coherent design documents in the established repository structure.

At minimum deliver:

**01 — PRODUCT_INFORMATION_ARCHITECTURE.md**

Complete route inventory, navigation and user journeys.

**02 — ROLE_PERMISSION_MATRIX.md**

Role/resource/action authorization, tenant boundaries and ownership checks.

**03 — UI_UX_DESIGN_SYSTEM.md**

Branding, visual tokens, accessibility, responsive layout and components.

**04 — PAGE_AND_WIREFRAME_SPECIFICATIONS.md**

Detailed specifications and wireframes for the principal screens.

**05 — DATABASE_DESIGN.md**

Normalized data model, relationships, constraints, indexes, retention and spatial types.

**06 — DATA_CONTRACTS_AND_PROVENANCE.md**

Observation schemas, hardware/simulation provenance, restricted truth and units.

**07 — API_CONTRACTS.md**

Endpoint inventory, authentication/authorization and request/response behavior.

**08 — DOMAIN_STATE_MACHINES.md**

Supply, devices, evidence, incidents, work orders and verification lifecycle.

**09 — AUTH_SECURITY_AND_PRIVACY.md**

Session approach, threat boundaries, tenant security, upload privacy and audit.

**10 — REALTIME_OFFLINE_AND_NOTIFICATIONS.md**

Live monitoring, reconnection, worker offline data and message delivery design.

**11 — DEPLOYMENT_AND_STACK_DECISIONS.md**

Compatible stack recommendation, local deployment topology and alternatives.

**12 — M02_ACCEPTANCE_AND_TEST_PLAN.md**

Traceable tests for future M03/M04/M06/M07 implementation.

Also create, where useful:

- An OpenAPI 3.1 YAML contract.
- Mermaid database entity-relationship diagrams.
- Mermaid system architecture diagrams.
- Mermaid incident and repair state diagrams.
- An illustrative SQL DDL design file, clearly marked NOT A DEPLOYED MIGRATION.
- Design tokens or schema examples that do not pretend an application is running.

Update existing documents such as the data dictionary and decision log where necessary.

Avoid duplicate sources of truth.

If an authoritative current document should be expanded rather than duplicated, do that and explain the choice.

---

# PHASE O — REQUIRED ENGINEERING DECISIONS

Resolve M02-owned choices with documented alternatives and rationale:

1. Exact relationship between user identity, organization membership and role.
2. Session/authentication ownership.
3. Secure frontend-to-backend API boundary.
4. Schema and spatial representation.
5. Canonical evidence and workflow status nomenclature.
6. Simulation-versus-hardware provenance.
7. Live event delivery method.
8. Worker offline operation scope.
9. Attachment storage/authorization model.
10. Initial deployment topology.
11. API contract conventions.
12. UX navigation and design principles.

Do not silently resolve choices that belong to future hardware or scientific measurement stages.

For example:

- Acoustic sensor model and analog circuit belong to detailed hardware engineering.
- Actual wave speed remains a measured/calibrated quantity.
- True physical detection accuracy remains unverified.
- GUARD-5 collection-channel performance is not established.
- Simulation thresholds require explicit future experiment definitions.

If any critical choice genuinely needs owner approval, document the alternatives and recommend a default rather than inventing authorization.

---

# PHASE P — ACCEPTANCE TEST PLANNING

For each major planned workflow, specify the future automated tests required to prove it works.

Required categories include:

### Functional

- Citizen creates complaint.
- Citizen views only their own complaint.
- Supervisor accepts or investigates an incident.
- Work order is assigned.
- Worker submits update.
- Repair evidence is recorded.
- Supervisor reviews.
- Verification outcome is saved.
- Reopened incident preserves historical events.

### Security

- Unauthorized requests rejected.
- Cross-tenant access rejected.
- Cross-citizen access rejected.
- Worker assignment permissions enforced.
- Invalid uploads rejected.
- Sessions expire correctly.
- Audit history records significant changes.

### Scientific provenance

- Simulated data remains labeled.
- Restricted truth is absent from detector inputs.
- Laboratory and field data remain distinguishable.
- Invalid or stale sensor observations are handled.
- Acoustic unresolved results do not become fake pinpointed locations.
- GUARD-5 external wetness is not automatically classified as a confirmed joint leak.
- Exports retain provenance.

### Reliability

- Duplicate events are deduplicated.
- Network interruption does not corrupt an incident.
- Reconnect resumes live updates correctly.
- Offline worker forms synchronize safely.
- Retried notifications are not duplicated indefinitely.

### UI/UX

- Responsive desktop/mobile layouts.
- Accessible forms.
- Keyboard navigation.
- Loading and error states.
- High-contrast status presentation.
- Clear SIMULATION mode indication.

Tests should be documented as future acceptance cases. Do not pretend they have executed.

---

# PHASE Q — DEVELOPMENT WORKFLOW AND GITHUB

Create a focused short-lived branch, preferably:

`feature/m02-architecture-database-design`

Before branching, verify that the actual `main` head matches your checkout and that no unrelated changes are present.

Do not overwrite remote changes.

Perform this milestone entirely on the feature branch.

Reference GitHub issue #2.

Create useful commits.

Run actual available checks:

- Repository integrity validator.
- Git whitespace checks.
- Markdown link checks where supported.
- OpenAPI structural validation if an appropriate validator is available.
- Schema documentation consistency checks.
- Mermaid syntax checks where available.

Do not install large development stacks merely to validate planning documents.

If tooling cannot be run, report the limitation honestly.

After completing documentation:

1. Review the complete diff.
2. Check for secrets.
3. Check that no implementation work accidentally entered scope.
4. Commit the completed design.
5. Push the feature branch.
6. Open a pull request targeting `main`, if GitHub permissions permit.
7. Link issue #2.
8. Report GitHub Actions results when available.

**Do not merge the pull request, close issue #2, or close M02 without my separate approval.**

The design must be reviewed before implementation.

---

# PHASE R — QUALITY EXPECTATIONS

I want serious professional engineering work.

Do not optimize for the number of files or pages.

Optimize for completeness, consistency, implementation feasibility and real user usefulness.

Every important website feature must eventually connect to:

- A real user.
- An explicit permission.
- A validated action.
- A persistent data entity.
- An API contract.
- Appropriate evidence.
- An acceptance test.

No empty decorative features.

No invented leak-detection accuracy.

No fictitious hardware validation.

No false claims of indigenous components or originality.

No invented real-world utility customers.

No exposing sensitive pipeline information publicly.

No expensive unnecessary cloud architecture.

No rewriting the frozen physical sensing concept.

The hardware materials budget ceiling remains ₹60,000, but this milestone should not pretend that the complete cloud operating cost is part of that materials budget.

---

# PHASE S — FINAL COMPLETION REPORT

After finishing Milestone 02, provide:

## A. Current repository state

- Repository URL.
- Feature branch.
- Commit SHA.
- Pull request URL.
- Changes awaiting review.

## B. Architecture summary

Explain the proposed frontend/backend/database structure in simple language.

## C. Complete application inventory

Summarize all role-specific pages and major workflows.

## D. Database design

Give the actual number of designed entities/tables and explain the most important relationships.

## E. API design

List all proposed API groups and the count of defined endpoints.

## F. Security

Summarize authentication, tenant isolation, public privacy and protected upload decisions.

## G. UI/UX

Describe the visual design system, wireframe deliverables and mobile worker experience.

## H. Scientific integrity

Explain how simulator output, genuine future hardware readings, uncertainty, and restricted ground truth remain separated.

## I. Technical decisions

State every important resolved M02 decision, plus owner approvals still required.

## J. Validation

List commands actually executed, tests actually passed, failed checks and unresolved limitations.

## K. Next milestone

Explain precisely whether we are ready for:

**M03 — Backend Foundation and Functional API Implementation.**

Do not start M03 automatically.

---

# FINAL INSTRUCTION

I am authorizing **Milestone 02 now**.

Read the existing repository thoroughly and complete the website architecture, database design, UI/UX specification, API contracts, domain workflows and security design to a high professional engineering standard.

Preserve all frozen HYDROOVERITY decisions.

Work autonomously within this milestone, verify your outputs, use the existing GitHub workflow and give me a clear completion report.

**Begin M02.**
