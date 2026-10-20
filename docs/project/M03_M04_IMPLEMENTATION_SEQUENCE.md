# M03/M04 implementation sequence

**PLANNED ONLY — none of these slices is implemented or authorized by this plan.** Issue #2/M02 remains open pending owner approval. This sequences the existing [M03–M10 roadmap](ROADMAP.md), not four new milestones. The complete catalogue now has57 proposed tables and117 operations; each is a design requirement, not an instruction to build everything together.

Use one reviewed vertical slice at a time. M03 supplies persistent backend behavior; M04 supplies the matching real frontend. M05 builds scientific engines, M06 integrates them, M07 hardens maintenance operations, M08 creates digital hardware engineering, M09 validates the whole system, M10 records the demonstration. Do not mark an entire milestone complete because its early slice works.

API paths below are relative to `/api/v1`; `O` means `/orgs/{organization_id}` and braces retain their canonical parameter names. Exact bodies/permissions remain in openapi-design.json and the inventory; no placeholder success responses. Include loading/empty/error/denied/online states when enabling a page. Disable unavailable routes/features explicitly; never display fabricated telemetry.

## Dependency and migration rules

Choose maintained patch versions and compatible locks during separately authorized M03 setup. Use FastAPI/Python, PostgreSQL/PostGIS and a single authentication owner; adopt migration tooling then, not in M02. First prove an empty-database upgrade and rollback/forward-repair procedure on disposable data.

The final schema includes forward/cyclic optional links (for example incidents.simulation_run_id, evidence_records.observation_id/capture_id and assessment acoustic/run links). An early migration may leave a future nullable feature column inaccessible under `CHECK(column IS NULL)` until its target exists; add its composite same-tenant FK before removing that guard and before enabling writes. Alternatively create the target schema earlier if it is already needed. Do not create dangling writable IDs, drop tenant constraints or require implementing a future engine merely to create an incident. Nonnullable parent dependencies always precede child creation. Record the chosen staged DDL and tests in the M03 migration review; the M02 catalogue remains the final target, not an executable migration.

## First slice — platform foundation

Backend M03 first; frontend M04 only after its APIs and persistence pass. Establish database connection/pool cleanup, migration runner, fixed configuration/secrets, same-origin proxy/local HTTPS, structured safe errors/logging, session authentication, CSRF, global identity, tenant membership and reusable authorization. A controlled local bootstrap creates the first organization/admin via an audited operator procedure, not public staff registration. EVALUATOR grants stay separately controlled.

Required tables:

- organizations, users, organization_memberships.
- roles, permissions, role_permissions, role_assignments.
- sessions, account_recovery_tokens, invitations.
- audit_logs, idempotency_records and domain_events for tenant governance transactions. Auth events use restricted global security logs, not invented tenant rows; pretenant email uses the bounded private post-commit adapter described in the security contract, not tenant background_jobs.

Required endpoints:

- GET /auth/csrf; POST /auth/register, /auth/login, /auth/logout, /auth/recovery, /auth/reset, /auth/verify, /auth/invitation-accept.
- GET/PATCH /me; GET /me/memberships; GET /me/sessions; DELETE /me/sessions/{session_id}.
- GET /public/utilities/{slug}; GET /public/project-status; GET O.
- GET O/memberships; POST O/invitations; PUT O/memberships/{membership_id}/roles; POST O/memberships/{membership_id}/status; GET O/audit-logs. These support real invite/deny/revoke tests; complete administration UI/integrations/settings are deferred.
- Internal liveness/readiness probes are required before exposure: proposed GET /internal/health/live and GET /internal/health/ready on a restricted operations listener. They are future infrastructure contracts, currently absent from the117 business operations. Define them in the M03 operational contract before implementation; readiness checks connection/migration state with short timeout, reveals no secrets and fails when DB is unavailable. No public diagnostic endpoint is implied.

Permissions: global self ownership without active-membership prerequisite; PUBLIC auth requires preauth cookie/CSRF as specified; enabled utility CITIZEN registration only. Tenant paths require active current membership; ADMIN gets only listed governance permissions, recent reauth/last-admin guards. No ADMIN engineer/evaluator inheritance. Same-tenant composite FKs, application checks and restricted runtime DB role/RLS must be proven before tenant data exposure.

Frontend: PAGE-12–19 login/register/recovery/reset/verify/invite/account/sessions; only enough organization selection/navigation for current real memberships. PAGE-01/07 editorial status and PAGE-08 utility selection may be shown without fictitious operational data. Successful navigation depends on real API responses.

Completion tests: disposable DB upgrade; unique identity and membership races; positive/negative authorization; A/B tenant requests and pooled-context reuse; CSRF/Origin denial; login rotation/logout revocation; each lost-response/single-use auth case A01–A08; pretenant email failure/cooldown; no secret logs/cache; no evaluator self-grant; expired sessions; health readiness failure; essential accessible form/error flows. Record executed output/environment/commit when implemented. M02 has executed none of these backend tests.

Dependencies: owner M02 merge/design approval and separate M03 authorization, actual dependency/version review, selected private local delivery/HTTPS configuration. Deliberately defer device ingestion, graph editor, simulations, acoustic processing, notification provider integration, reports, offline vault and public contact intake until their controls exist.

## Second slice — complete incident workflow

Build the smallest persistent end-to-end workflow across M03 backend and M04 pages: citizen complaint -> supervisor review/incident -> work order -> assigned technician updates/repair -> independent verification record -> citizen-safe status. This is an early vertical slice; robust offline recovery/reporting remains M07.

Required tables beyond slice1:

- water_zones; citizen_complaints, complaint_status_events.
- incidents, incident_events, incident_links, incident_evidence.
- work_orders, work_order_actions, repair_records, verification_records, verification_evidence.
- evidence_records, evidence_assessments, assessment_evidence, using complaint/manual/repair evidence first. Future observation/acoustic/run references remain guarded-null until their targets are available.
- attachments and attachment_links only when enabling photo controls; until secure quarantine/scanning/storage is ready, defer photo input explicitly rather than accept unsafe uploads. Add notifications initially only for persistent in-app receipts if actually shown; defer external delivery. Existing audit/idempotency/domain_events support atomic history and retry semantics.

Required endpoints:

- GET/POST O/zones and GET O/zones/{resource_id} for a declared service area; no complete pipe graph needed yet.
- POST/GET O/complaints; GET O/complaints/{complaint_id}; POST .../follow-ups and .../review.
- POST/GET O/incidents; GET O/incidents/{incident_id}; GET .../timeline; POST .../transitions and .../links.
- POST/GET O/work-orders; GET O/work-orders/{work_order_id}; GET .../brief; POST .../assignment, .../actions and .../transitions.
- POST/GET O/work-orders/{work_order_id}/repairs; POST/GET O/repairs/{repair_id}/verifications.
- GET/POST O/evidence-assessments; GET O/evidence-assessments/{assessment_id} for reviewed manual evidence.
- When photographs are enabled, implement the complete canonical attachment ticket/content/completion/download lifecycle together; no inert upload control. When in-app notifications are enabled, GET O/notifications and POST O/notifications/{notification_id}/read.

Permissions: CITIZEN can create/read/follow up only own safe complaints; SUPERVISOR reviews, creates/assigns work and records guarded verification; TECHNICIAN sees current assigned work only and can use only allowed transition edges; ENGINEER reviews technical comparability/evidence. Assignment/version/current membership and all nested IDs are checked again on retry. Work completion never creates scientific PASSED. If independent before/after evidence is insufficient, persist NOT_VERIFIABLE with reason, not a fabricated success. A verification reviewer must be independent of the recorded repair actor; technical uncertainty requires engineer review.

Frontend: PAGE-20–22 citizen reports; PAGE-31–36 incidents/tasks/verification/complaint review; a useful minimal PAGE-23 overview may link real records. Do not enable analytics totals, map pins or savings without their real source.

Completion tests: actual API/DB workflow through every role; own-vs-other complaint and photo denial; cross-tenant body/path IDs; unassigned worker denial and reassignment races; durable repair/history; same-key dedup/body conflict and reauthorization on replay; invalid/stale transitions; independent verifier and NOT_VERIFIABLE behavior; citizen DTO excludes internal topology/contact/worker notes; responsive accessible UI; quarantine/parent-ACL tests before photos. Prove F01–F07 and S01–S06 for enabled features. PASSED/FAILED comparable sensor scenarios wait for slice3/science, and M07 expands the offline/reopen workflow.

Dependencies: slice1 auth/membership/RLS/transactions; reviewed zone data; explicit consent/content limits. Deliberately defer full offline encrypted draft vault, real sensors, graph editor, scientific automatic verification, external messages and reports. Accepting manual evidence is not a hardware test.

## Third slice — sensor evidence

M03/M04 prepare schema, read/query paths and server-origin contracts; M05 supplies scientifically meaningful engines, and M06 enables their real integration. Use clearly labeled synthetic test fixtures before that, with reproducible fixture provenance and no numerical-performance claim. Do not describe a fixture emitter as a completed hydraulic/acoustic engine.

Required tables beyond earlier slices:

- devices, sensor_channels, device_configuration_versions, device_credentials, calibration_records, device_health_events; algorithm_configurations.
- sensor_observations and observation_artifacts; reuse evidence_records/evidence_assessments/assessment_evidence and existing incident/evidence joins.
- supply_windows for WATCH context. Geometry/installation support is added only as needed from network_junctions, pipe_segments, pipe_access_points and device_installations; the full editor/coverage workflow is slice4.
- Synthetic ingestion with an active run lease additionally requires simulation_scenarios, background_jobs, simulation_runs, simulation_outputs and the isolated restricted_simulation_truth store/principals. Create necessary parent schemas and controlled fixtures before enabling the ingestion endpoint. Do not bypass the active-run rule for an early demonstration. Generator/evaluator/detector credentials remain separate; full engine integration is M06.

Required endpoints:

- GET/POST O/devices; GET O/devices/{device_id}; GET .../channels; GET/POST .../configurations; POST .../credentials; DELETE .../credentials/{credential_id}; installation/calibration/health routes only when that feature is enabled with valid parents.
- POST /ingest/simulation/observations under an active credential-bound SIMULATION run; POST /ingest/hardware/observations only with a reviewed profile/acquisition adapter. Until M08/hardware authorization, actual hardware intake remains disabled; software fixtures never become field readings.
- GET O/observations; POST O/manual-observations; GET O/supply-windows; GET/POST O/evidence-assessments; GET O/evidence-assessments/{assessment_id}.
- Operational read endpoints and filters already listed are wired into monitoring pages; bounded polling first. SSE/replay is slice4 after snapshot/query consistency is stable.

Permissions: ADMIN can provision reviewed identities/credentials without inheriting raw engineering telemetry; ENGINEER manages acquisition configurations and assessments; ENGINEER/SUPERVISOR query permitted evidence. SIMULATOR and DEVICE are separate bearer-only scoped principals. SIMULATION is server-derived and immutable; no client override/environment/truth keys. Ordinary API/detector DB/object credentials cannot read truth seeds/labels/artifacts; ordinary manifest listings exclude restricted IDs as well as content.

Frontend: PAGE-25–27 monitoring/devices/detail plus real evidence links in incidents. Show SIMULATED DATA, collection/receipt time, freshness, units/configuration/quality and no-data/uncalibrated states. Operational views exclude simulated data by default. PAGE-35 verification may use comparable evidence only after its logic is actually tested.

Completion tests: authenticated batch size/unit/time validation; exact event dedup/conflicting UUID; transactional rollback; wrong tenant/device/channel/run; source override422; SIMULATION label preserved through storage/query/UI; readonly truth principal denial and unknown artifact classifications; expired/revoked credentials; secret issuance replay409; staleness/out-of-order handling; bounded cursor/query behavior; evidence/verification comparability. P01–P06 require actual M05/M06 engine/integration execution before being claimed complete; fixture checks cover only their data-contract portion.

Dependencies: slices1–2; required FK parent closure and private objects; fixture manifests; M05 for meaningful engine outputs, M06 for full simulation integration, M08 before real acquisition. Deliberately defer acoustic estimates, detailed GUARD-5 logic, graph editor, performance claims, calibration-derived probabilities and field validation.

## Fourth slice — advanced operations

Do this incrementally after the first three slices, respecting each milestone's authorization. M03 may deliver basic pipeline persistence and M04 navigation shells, but full scientific/delivery/maintenance workflows depend on M05–M07. M08 hardware remains digital engineering; M09 proves combined behavior and M10 captures actual software.

Required tables beyond earlier slices: network_junctions, pipe_segments, pipe_access_points, device_installations; collar_service_tests; acoustic_captures, acoustic_location_estimates; notifications, notification_delivery_attempts; feedback_items, feedback_events; project_contact_submissions; complete simulation_scenarios/runs/outputs/restricted_simulation_truth and background_jobs responsibilities. Reuse existing evidence/repair/verification, audit and queue tables; reports persist jobs plus private artifact manifests, not an invented reports table. No new table is justified merely for a page.

Required endpoints, enabled by capability:

- Graph: GET/POST O/junctions, O/pipes, O/access-points; GET/PATCH each corresponding /{resource_id}; PATCH O/zones/{resource_id}; GET O/coverage. Enable with topology/offset/unit validation and a table alternative to the map.
- Devices/GUARD-5: canonical device installation, calibration, health-event and service-test endpoints; exactly A/B/C/EXT/BYPASS, separate supervision. Do not infer leak source merely from wetness.
- Acoustics: GET/POST O/acoustic-captures; GET .../{capture_id}; POST/GET .../{capture_id}/estimates; GET O/artifacts/{artifact_id}/download. Gate on surveyed path/shared-clock metadata, eligibility/uncertainty and nontruth artifact ACL. No independent wireless clocks or fake pinpoint result.
- Simulation M05/M06: GET O/simulations/scenarios; POST/GET O/simulations/runs; GET .../{run_id}; POST .../{run_id}/cancel; GET .../{run_id}/outputs and .../{run_id}/evaluation; GET O/algorithm-configurations. Evaluation alone needs ENGINEER+EVALUATOR and sealed terminal run; no detector access to truth. Engines precede integration/UI success claims.
- Operations M07: complete notifications/read, POST O/reports, GET O/reports/{report_id}, GET .../download; GET O/events for authorized SSE/replay; canonical feedback/create/review routes; public project contact only after its operator/retention/abuse controls exist. Complete organization settings/integration administration routes with recent reauth, safe configuration references and no provider purchase.

Permissions: graph/science ENGINEER with specified SUPERVISOR reads; assigned TECHNICIAN only on task-linked records; ADMIN only listed governance; sealed evaluator grant never inferred. SSE/reports/jobs/downloads recheck tenant, membership, current ACL, mode and classification. Project inbox access is restricted project-operator support, not organization ADMIN. CSV formula safety and private artifact lifecycle are mandatory before report downloads.

Frontend: PAGE-24/28–30 graph/GUARD/acoustics; PAGE-37–41 maintenance/analytics/reports/simulations; PAGE-42–46 feedback/notifications/admin plus PAGE-09 contact. Add offline draft vault, conflict recovery and SSE with safe fallback only when backend support passes. Never enable an action that only produces mock success.

Completion tests: valid/ambiguous topology and surveyed offsets; five independent channels including EXT-only/BYPASS-only cases; shared-clock acoustic abstention/interval bounds; blind holdouts and honest denominators; lease/cancel/crash races; truth isolation on every transport; no mixed-mode operational reports; notification dedup/status; CSV safety; offline reassignment/revocation; private object expiry; contact abuse/deletion; integration/restore/accessibility/performance/security tests. M09 combines actual evidence; M10 uses real captured flows. Digital CAD/electronics/firmware/BOM evidence remains M08 and unbuilt until separately authorized construction/testing.

Dependencies: previous slices plus M05 engines -> M06 integration -> M07 complete maintenance, explicit deployment/provider/retention/tile-license choices, M08 digital source for hardware representation, M09 release validation. Deliberately defer real field-performance/savings claims and procurement; keep the ₹60,000 materials ceiling and all frozen architecture decisions.

## Exit bookkeeping

For each slice PR, record enabled operation IDs, migrated tables/constraints, pages, executed positive/negative tests, denied/deferred capabilities and remaining milestone criteria. Changes to contracts precede implementation. Schema-only targets and empty pages never count as implemented domain behavior. No current slice is complete; M03 has not begun.
