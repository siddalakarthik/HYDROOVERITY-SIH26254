# API contracts

Issue #2; **no endpoints implemented**. [OpenAPI 3.1 JSON](openapi-design.json) is the canonical wire contract; JSON avoids a second YAML source and needs no installed parser. This inventory explains actions, roles and persistence. [Provenance](DATA_CONTRACTS_AND_PROVENANCE.md), [security](AUTH_SECURITY_AND_PRIVACY.md) and [state guards](DOMAIN_STATE_MACHINES.md) are normative service invariants that JSON Schema alone cannot express.

## Conventions

M03 complaint-history correction: PublicUpdate.message allows 2000 characters, matching the existing ComplaintFollowup.description limit. Full owner-authored follow-ups are retained in the complaint event ledger. Private supervisor review reasons are persisted separately in complaint_status_events.internal_reason and are never included in CitizenComplaint/PublicUpdate projections. This adds no route or role.

M03 implementation clarification (issue #3): administrator membership-directory items include the optional `MembershipView.version` integer. Membership governance requires If-Match but has no individual membership GET route; this field makes the existing precondition usable without inventing another endpoint. Global self-membership lists may omit it. Asset detail and profile GETs return ETag for their existing versioned edits.

The existing If-Match on POST repair verifications refers to the immutable repair receipt, whose stable receipt version is 1. Send `If-Match: "1"`. A correction creates another repair ID; reviews append/supersede earlier reviews and never mutate the repair. Current resource authorization and transactional review ordering still apply.

Base `/api/v1`; UUID resource IDs; RFC3339 UTC times ending Z; explicit units. All tenant paths include organization_id, validated against current membership. Never trust a client role, arbitrary organization header or source_environment field. ADMIN has only listed governance actions, not implicit telemetry/truth access. ALL means authenticated active membership on tenant endpoints; global /me/session endpoints require only the authenticated identity and ownership, even without an active membership. It never means any visitor. DEVICE/SIMULATOR are scoped nonhuman principals. ENGINEER+EVALUATOR requires both grants and a sealed terminal run. Own/assigned restrictions apply in addition to role and organization checks. Missing/inaccessible object -> uniform 404; do not reveal existence cross-tenant.

GETs do not mutate business state. `GET /auth/csrf` is a documented bounded preauth-cookie bootstrap and rate-limited. Cookie mutations require session-bound X-CSRF-Token plus validated Origin; login/register/recovery use preauth session. Same-origin proxy means no credentialed wildcard CORS. Bearer ingestion rejects human cookies and is not CSRF-authenticated.

Tenant business writes and credential-bound ingestion require UUID Idempotency-Key (7-day receipt keyed by actor, server-validated organization, method and route template plus canonical nonsecret body hash). Same key/same body returns the original safe receipt after current authorization; different body ->409. Authentication, global /me writes and project contact are explicitly exempt and reject that header with400. No auth payload, password/token fingerprint, raw response or secret is stored in this cache. Credential issuance is the further safe exception: same-key replay returns409 without redisclosing the one-time secret; recover by authorized revocation/new issuance. See the per-operation x-retry-policy and authentication retry matrix below. Worker bodies also carry operation_id and base/assignment version. Versioned updates/transition routes require If-Match, except immutable append receipts whose parent/base version is explicit; all state checks still occur transactionally. Missing precondition ->428, stale ->412, reassigned task ->409 with safe recovery instruction, not leaked assignee identity. POST actions do not accept arbitrary status patches. Required fields, enums, max lengths, bounded batches and additionalProperties:false are specified. All nested resource IDs must be authorized and same-tenant.

List responses use `items,next_cursor,as_of`, default limit50/max100, stable timestamp+ID cursor bound to filter/organization/permission scope. Unknown filters return422; unauthorized filters never widen results. workspace_mode defaults OPERATIONAL; simulation mode is explicit and cannot be mixed into operational savings/field-performance reports. Time queries need from<to and a bounded pilot range (31 days per request; use cursors/exports for longer periods). bbox searches limited to permitted tenant zones. Do not expose internal exception text: error={code,message,request_id,field_errors}. Retry-After on429/503 where appropriate; no raw logs, SQL or token values.

Observation ingest batches are atomic, <=500 scalar events/1 MiB body; adapters supply authenticated source class. Hardware credential binds LABORATORY/FIELD profile; simulator credential binds SIMULATION and active run/virtual device. Exact event retry returns duplicate IDs; changed content for same event UUID ->409. No privileged schema lets a simulated producer claim field validation. Manual observations are MANUAL/MANUAL. Raw acoustic binaries use separately scoped artifacts and never a dashboard stream. Future hardware artifact upload must be added as a versioned acquisition adapter contract after M08; M02 does not invent a finished raw acquisition transport.

Report jobs use the background_jobs queue plus private observation_artifacts manifest and retain creator/current authorization (see DATABASE_DESIGN.md). Export/download endpoints preserve provenance, omit restricted truth except the separate evaluation route, and neutralize CSV formula cells. Requests to QUEUED analysis/report operations return receipt/status; completion is reported by status/SSE, not fake immediate analysis.

Contract changes: additive optional fields within v1 require schema/test review; enums are not casually extended without consumers reviewed. Breaking changes require explicit /v2 plan later, not enterprise versioning infrastructure. info.version is a design contract revision only. Do not generate implementation from this draft before owner review.

## Endpoint inventory

117 method/path operations across 24 groups. Every write lists a concrete persistence effect; every read is a permitted projection. Global session/identity endpoints are the deliberate exceptions to organization-prefixed resources.

### Authentication

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /auth/csrf` | None -> Csrf | PUBLIC; preauth/session | Create/refresh bounded preauth session and synchronizer CSRF verifier; no business mutation. |
| `POST /auth/register` | Register -> Message | PUBLIC; preauth/session | Create unverified global identity and CITIZEN membership; enqueue verification. |
| `POST /auth/login` | Login -> UserView | PUBLIC; preauth/session | Validate credentials, rotate session/CSRF; audit login. |
| `POST /auth/recovery` | Recovery -> Message | PUBLIC; preauth/session | Generic response; bounded single-use reset token if account exists. |
| `POST /auth/reset` | Reset -> Message | PUBLIC; preauth/session | Consume token, update hash, revoke all authenticated sessions. |
| `POST /auth/verify` | TokenAction -> Message | PUBLIC; preauth/session | Consume email token and activate allowed citizen membership. |
| `POST /auth/invitation-accept` | TokenAction -> Message | ALL; verified global identity, invited email; no active membership required | Atomically consume invitation and apply exact server-bound tenant role; replay422. |
| `POST /auth/logout` | None -> Message | PUBLIC; presented session cleanup only, CSRF required | Monotonic revoke/clear, including recognized revoked/expired verifier cleanup; never issue a session. |

### Current user

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /me` | None -> UserView | ALL; self | Read identity only. |
| `PATCH /me` | ProfilePatch -> UserView | ALL; self | Update display name; audit safe identity change. |
| `GET /me/memberships` | None -> Page_MembershipView | ALL; self | Read active memberships; no other user directory. |
| `GET /me/sessions` | None -> Page_SessionView | ALL; self | List own sessions without token verifiers. |
| `DELETE /me/sessions/{session_id}` | None -> Message | ALL; self | Revoke owned session immediately. |

### Public

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /public/utilities/{slug}` | None -> PublicUtility | PUBLIC; public allowlist | Read enabled utility public metadata only. |
| `GET /public/project-status` | None -> ProjectStatus | PUBLIC; public allowlist | Read editorial evidence status, no field metrics invented. |
| `POST /public/contact` | ContactWrite -> Message (202) | PUBLIC; preauth/session + fixed project inbox | Persist private project_contact_submissions; generic receipt without ID; no tenant mapping or public retrieval. |

### Organization

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}` | None -> OrganizationView | ALL; active membership | Read permitted organization summary. |
| `PATCH /orgs/{organization_id}` | OrganizationPatch -> OrganizationView | ADMIN; tenant + fresh reauth | Update approved settings/retention policy; audit, no cloud provisioning. |

### Water zones

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/zones` | None -> Page_ZoneView | ENGINEER, SUPERVISOR; tenant | Read internal graph/asset list. |
| `POST /orgs/{organization_id}/zones` | ZoneWrite -> ZoneView | ENGINEER; tenant | Validate topology/units, insert asset and audit; no physical installation implied. |
| `GET /orgs/{organization_id}/zones/{resource_id}` | None -> ZoneView | ENGINEER, SUPERVISOR; tenant | Read asset or uniform not-found. |
| `PATCH /orgs/{organization_id}/zones/{resource_id}` | ZoneWrite -> ZoneView | ENGINEER; tenant + If-Match | Versioned asset edit; reject inconsistent endpoints, offsets or zones. |
| `GET /orgs/{organization_id}/supply-windows` | None -> Page_SupplyWindow | ENGINEER, SUPERVISOR; tenant | Read observed supply history with reasons. |

### Pipeline assets

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/junctions` | None -> Page_Junction | ENGINEER, SUPERVISOR; tenant | Read internal graph/asset list. |
| `POST /orgs/{organization_id}/junctions` | JunctionWrite -> Junction | ENGINEER; tenant | Validate topology/units, insert asset and audit; no physical installation implied. |
| `GET /orgs/{organization_id}/junctions/{resource_id}` | None -> Junction | ENGINEER, SUPERVISOR; tenant | Read asset or uniform not-found. |
| `PATCH /orgs/{organization_id}/junctions/{resource_id}` | JunctionWrite -> Junction | ENGINEER; tenant + If-Match | Versioned asset edit; reject inconsistent endpoints, offsets or zones. |
| `GET /orgs/{organization_id}/pipes` | None -> Page_Pipe | ENGINEER, SUPERVISOR; tenant | Read internal graph/asset list. |
| `POST /orgs/{organization_id}/pipes` | PipeWrite -> Pipe | ENGINEER; tenant | Validate topology/units, insert asset and audit; no physical installation implied. |
| `GET /orgs/{organization_id}/pipes/{resource_id}` | None -> Pipe | ENGINEER, SUPERVISOR; tenant | Read asset or uniform not-found. |
| `PATCH /orgs/{organization_id}/pipes/{resource_id}` | PipeWrite -> Pipe | ENGINEER; tenant + If-Match | Versioned asset edit; reject inconsistent endpoints, offsets or zones. |
| `GET /orgs/{organization_id}/access-points` | None -> Page_AccessPoint | ENGINEER, SUPERVISOR; tenant | Read internal graph/asset list. |
| `POST /orgs/{organization_id}/access-points` | AccessPointWrite -> AccessPoint | ENGINEER; tenant | Validate topology/units, insert asset and audit; no physical installation implied. |
| `GET /orgs/{organization_id}/access-points/{resource_id}` | None -> AccessPoint | ENGINEER, SUPERVISOR; tenant | Read asset or uniform not-found. |
| `PATCH /orgs/{organization_id}/access-points/{resource_id}` | AccessPointWrite -> AccessPoint | ENGINEER; tenant + If-Match | Versioned asset edit; reject inconsistent endpoints, offsets or zones. |
| `GET /orgs/{organization_id}/coverage` | None -> Coverage | ENGINEER, SUPERVISOR; tenant | Derive instrumented/eligible coverage and explicit gaps. |

### Devices

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/devices` | None -> Page_Device | ENGINEER, SUPERVISOR, ADMIN; tenant | Read permitted device identity/health, not raw telemetry. |
| `POST /orgs/{organization_id}/devices` | DeviceWrite -> Device | ADMIN; tenant + fresh reauth | Register reviewed device identity; cannot bypass future physical provisioning gate. |
| `GET /orgs/{organization_id}/devices/{device_id}` | None -> Device | ENGINEER, SUPERVISOR, ADMIN; tenant | Read device metadata. |
| `GET /orgs/{organization_id}/devices/{device_id}/channels` | None -> Page_Channel | ENGINEER, SUPERVISOR; tenant | Read independently identified channels. |
| `GET /orgs/{organization_id}/devices/{device_id}/configurations` | None -> Page_ConfigurationView | ENGINEER; tenant | Read immutable acquisition configurations. |
| `POST /orgs/{organization_id}/devices/{device_id}/configurations` | DeviceConfigurationWrite -> ConfigurationView | ENGINEER; tenant | Append reviewed config; enforce five collar identities and acquisition-clock conditions. |
| `POST /orgs/{organization_id}/devices/{device_id}/installations` | InstallationWrite -> Receipt | ENGINEER; tenant | Record declared installation metadata; not proof of actual hardware trial. |
| `POST /orgs/{organization_id}/devices/{device_id}/credentials` | CredentialIssue -> CredentialView | ADMIN; tenant + fresh reauth | Issue one-time scoped credential matching device profile; audit without secret. |
| `DELETE /orgs/{organization_id}/devices/{device_id}/credentials/{credential_id}` | None -> Message | ADMIN; tenant + fresh reauth | Revoke only same-device credential and audit. |

### Diagnostics

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/devices/{device_id}/health-events` | None -> Page_HealthEvent | ENGINEER, SUPERVISOR; tenant | Read health evidence; do not infer dry/disconnected without supervision. |
| `GET /orgs/{organization_id}/devices/{device_id}/calibrations` | None -> Page_Calibration | ENGINEER; tenant | Read calibration history. |
| `POST /orgs/{organization_id}/devices/{device_id}/calibrations` | CalibrationWrite -> Calibration | ENGINEER; tenant | Append actual/calibration design record with explicit validity/provenance; no default successful calibration. |
| `GET /orgs/{organization_id}/collars/{device_id}/service-tests` | None -> Page_ServiceTest | ENGINEER, SUPERVISOR; tenant | Read external challenge receipts, channel response and limitations. |
| `POST /orgs/{organization_id}/collars/{device_id}/service-tests` | ServiceTestWrite -> ServiceTest | TECHNICIAN; assigned work order + matching device | Append assigned technician manual service receipt; no injection into pipeline. |

### Observations

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/observations` | None -> Page_Observation | ENGINEER, SUPERVISOR; tenant | Read provenance-preserving limited observations; never truth. |
| `GET /orgs/{organization_id}/observations/{observation_id}` | None -> Observation | ENGINEER, SUPERVISOR; tenant | Read one qualified source receipt. |
| `POST /orgs/{organization_id}/manual-observations` | ManualObservationWrite -> Observation | ENGINEER; tenant | Append MANUAL/MANUAL observation; cannot manufacture calibrated field sensor data. |

### Ingestion

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /ingest/hardware/observations` | ObservationBatch -> BatchReceipt | DEVICE; credential-bound organization/device/environment | Atomically deduplicate hardware events; server assigns LABORATORY/FIELD profile. |
| `POST /ingest/simulation/observations` | SimulationObservationBatch -> BatchReceipt | SIMULATOR; credential-bound tenant + active run lease | Atomically append SIMULATION-only output, verify run and virtual channels. |

### Evidence

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/evidence-assessments` | None -> Page_Evidence | ENGINEER, SUPERVISOR; tenant | Read explanations with immutable source links. |
| `GET /orgs/{organization_id}/evidence-assessments/{assessment_id}` | None -> Evidence | ENGINEER, SUPERVISOR; tenant | Read assessment reasons, alternatives and source IDs. |
| `POST /orgs/{organization_id}/evidence-assessments` | AssessmentWrite -> Evidence | ENGINEER; tenant | Append reviewed interpretation, preserve competing explanations. |

### Acoustics

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/acoustic-captures` | None -> Page_AcousticCapture | ENGINEER; tenant | Read capture metadata, not waveform on live stream. |
| `POST /orgs/{organization_id}/acoustic-captures` | CaptureWrite -> AcousticCapture | ENGINEER; tenant + provenance-bound artifact | Validate authorized artifact and endpoint/clock metadata; do not relabel source environment. |
| `GET /orgs/{organization_id}/acoustic-captures/{capture_id}` | None -> AcousticCapture | ENGINEER; tenant | Read capture and signal-quality metadata. |
| `POST /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates` | EstimateRequest -> Receipt | ENGINEER; tenant | Queue bounded future analysis; no analysis implementation in M02. |
| `GET /orgs/{organization_id}/acoustic-captures/{capture_id}/estimates` | None -> Page_AcousticEstimate | ENGINEER; tenant | Read baseline/qualified interval or abstention results. |
| `GET /orgs/{organization_id}/artifacts/{artifact_id}/download` | None -> BINARY | ENGINEER; tenant + nontruth artifact ACL | Authorized bounded/range raw artifact download; no public URL or truth namespace. |

### Incidents

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/incidents` | None -> Page_Incident | ENGINEER, SUPERVISOR; tenant | List concerns separate from evidence confidence. |
| `POST /orgs/{organization_id}/incidents` | IncidentWrite -> Incident | ENGINEER, SUPERVISOR; tenant | Create concern with same-mode evidence links and NEW event. |
| `GET /orgs/{organization_id}/incidents/{incident_id}` | None -> Incident | ENGINEER, SUPERVISOR; tenant | Read concern and allowed operational state. |
| `GET /orgs/{organization_id}/incidents/{incident_id}/timeline` | None -> Page_TimelineEvent | ENGINEER, SUPERVISOR; tenant | Read immutable source/status/assignment history. |
| `POST /orgs/{organization_id}/incidents/{incident_id}/transitions` | IncidentTransition -> Incident | SUPERVISOR; tenant + If-Match | Validate state guard; append event/audit/outbox in one transaction. |
| `POST /orgs/{organization_id}/incidents/{incident_id}/links` | IncidentLinkWrite -> Receipt | SUPERVISOR; tenant + If-Match | Link duplicates/related concerns with provenance; no history deletion. |

### Work orders

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/work-orders` | None -> Page_WorkOrder | SUPERVISOR, ENGINEER, TECHNICIAN; tenant; TECHNICIAN assigned only | Read task board, not scientific verification. |
| `POST /orgs/{organization_id}/work-orders` | WorkOrderWrite -> WorkOrder | SUPERVISOR; tenant | Create task for accepted concern; no automatic verified leak status. |
| `GET /orgs/{organization_id}/work-orders/{work_order_id}` | None -> WorkOrder | SUPERVISOR, ENGINEER, TECHNICIAN; tenant; TECHNICIAN assigned only | Read task. |
| `GET /orgs/{organization_id}/work-orders/{work_order_id}/brief` | None -> WorkerBrief | TECHNICIAN; current assigned membership | Issue minimal safe task cache and 12-hour offline lease. |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/assignment` | AssignmentWrite -> WorkOrder | SUPERVISOR; tenant + If-Match | Assign active technician, increment assignment_version, notify/deduplicate. |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/actions` | WorkerAction -> Receipt | TECHNICIAN; assigned + version/assignment checks | Append offline-compatible note/material/photo references, operation ID deduplication. |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/transitions` | WorkTransition -> WorkOrder | SUPERVISOR, TECHNICIAN; tenant; worker assigned + permitted edge | Apply authorized transition; only supervisor completes/cancels; never scientific PASSED. |

### Repairs

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /orgs/{organization_id}/work-orders/{work_order_id}/repairs` | RepairWrite -> Repair | TECHNICIAN; assigned + If-Match | Append manual repair receipt and immutable evidence; no claimed success. |
| `GET /orgs/{organization_id}/work-orders/{work_order_id}/repairs` | None -> Page_Repair | SUPERVISOR, ENGINEER, TECHNICIAN; tenant; worker assigned only | Read repair records. |

### Verification

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /orgs/{organization_id}/repairs/{repair_id}/verifications` | VerificationWrite -> Verification | SUPERVISOR; tenant + If-Match + comparable evidence | Record explicit PASSED/FAILED/NOT_VERIFIABLE; require engineer review for technical comparability uncertainty. |
| `GET /orgs/{organization_id}/repairs/{repair_id}/verifications` | None -> Page_Verification | ENGINEER, SUPERVISOR, TECHNICIAN; tenant; worker assigned parent only | Read verification outcomes, independent of completed task. |

### Complaints

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /orgs/{organization_id}/complaints` | ComplaintWrite -> CitizenComplaint | CITIZEN; self in enabled reporting tenant | Create own report/tracking number with validated consent and safe updates. |
| `GET /orgs/{organization_id}/complaints` | None -> Page_CitizenComplaint | CITIZEN, SUPERVISOR; tenant; citizen owned only | Read citizen-safe projection even for supervisor; private review is separate. |
| `GET /orgs/{organization_id}/complaints/{complaint_id}` | None -> CitizenComplaint | CITIZEN, SUPERVISOR; tenant; citizen owned only | Return own report; guessed IDs return uniform 404. |
| `POST /orgs/{organization_id}/complaints/{complaint_id}/follow-ups` | ComplaintFollowup -> Receipt | CITIZEN; owned complaint + If-Match | Append own followup; no internal notes disclosed. |
| `POST /orgs/{organization_id}/complaints/{complaint_id}/review` | ComplaintReview -> Receipt | SUPERVISOR; tenant + If-Match | Write public-safe status event and optional internal incident link; do not confirm leak automatically. |

### Feedback

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /orgs/{organization_id}/feedback` | FeedbackWrite -> Feedback | ALL; tenant; citizen owns complaint if linked | Create feedback; safe acknowledgment. |
| `GET /orgs/{organization_id}/feedback` | None -> Page_Feedback | ALL; tenant; citizen own only; internal staff per role | List own or permitted internal feedback. |
| `POST /orgs/{organization_id}/feedback/{feedback_id}/review` | FeedbackReview -> Feedback | SUPERVISOR, ADMIN; tenant + If-Match | Append triage/resolution and optional existing GitHub issue link; no automatic external message. |

### Uploads

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /orgs/{organization_id}/attachments` | UploadStart -> UploadTicket | ALL; owned complaint/draft or authorized assigned task | Reserve scoped quota/ticket; clean source not yet downloadable. |
| `PUT /orgs/{organization_id}/attachments/{attachment_id}/content` | BINARY -> Attachment | ALL; ticket owner + target authorization | Write bounded private quarantine bytes; content hash and size checked. |
| `POST /orgs/{organization_id}/attachments/{attachment_id}/complete` | UploadComplete -> Attachment | ALL; ticket owner + target authorization | Finalize checksum; decode, strip metadata/reencode, quarantine/scan; fail closed. |
| `GET /orgs/{organization_id}/attachments/{attachment_id}` | None -> Attachment | ALL; parent resource ACL + own citizen restriction | Read allowed upload processing status. |
| `GET /orgs/{organization_id}/attachments/{attachment_id}/download` | None -> BINARY | ALL; CLEAN + parent ACL rechecked | Serve private safe derivative with nosniff/no-store; originals never served. |
| `DELETE /orgs/{organization_id}/attachments/{attachment_id}` | None -> Message | ALL; owner + evidence-pin/retention check | Request permitted erasure/redaction; preserve safe evidence tombstone. |

### Simulations

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/simulations/scenarios` | None -> Page_Scenario | ENGINEER; tenant | Read allowed scenario metadata without source truth. |
| `POST /orgs/{organization_id}/simulations/runs` | RunWrite -> SimulationRun | ENGINEER; tenant + allowed scenario | Create QUEUED run/noise seed; generator truth seed sealed separately. |
| `GET /orgs/{organization_id}/simulations/runs` | None -> Page_SimulationRun | ENGINEER; tenant | Read run status/manifests, not truth. |
| `GET /orgs/{organization_id}/simulations/runs/{run_id}` | None -> SimulationRun | ENGINEER; tenant | Read progress/assumptions without restricted truth. |
| `POST /orgs/{organization_id}/simulations/runs/{run_id}/cancel` | None -> SimulationRun | ENGINEER; tenant; creator or simulation control grant | Request cancellation; preserve partial results explicitly. |
| `GET /orgs/{organization_id}/simulations/runs/{run_id}/outputs` | None -> Page_RunOutput | ENGINEER; tenant | Read nontruth outputs/manifests. |
| `GET /orgs/{organization_id}/simulations/runs/{run_id}/evaluation` | None -> EvaluationResult | ENGINEER+EVALUATOR; tenant + sealed completed run + audited evaluation grant | Separately authorized evaluation, forbidden to detector/ordinary monitoring. |
| `GET /orgs/{organization_id}/algorithm-configurations` | None -> Page_AlgorithmConfiguration | ENGINEER; tenant | Read published immutable scientific method configurations. |

### Notifications

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/notifications` | None -> Page_Notification | ALL; self membership only | Read safe in-app messages. |
| `POST /orgs/{organization_id}/notifications/{notification_id}/read` | None -> Receipt | ALL; self membership only | Idempotently mark owned message read. |

### Reports

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `POST /orgs/{organization_id}/reports` | ReportWrite -> ReportJob | ENGINEER, SUPERVISOR; tenant + projection-specific permission | Queue scoped CSV/PDF, exclude simulation from operational defaults, preserve provenance. |
| `GET /orgs/{organization_id}/reports/{report_id}` | None -> ReportJob | ENGINEER, SUPERVISOR; creator + current grants | Read authorized export status; use simulation_outputs manifest or outbox job metadata, no new warehouse. |
| `GET /orgs/{organization_id}/reports/{report_id}/download` | None -> BINARY | ENGINEER, SUPERVISOR; creator + current grants + not expired | Download private time-limited export; neutralize spreadsheet formula injection. |

### Administration

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/memberships` | None -> Page_MembershipView | ADMIN; tenant + fresh session | Read tenant membership directory without credential material. |
| `POST /orgs/{organization_id}/invitations` | InviteWrite -> Receipt | ADMIN; tenant + fresh reauth | Create bounded one-use staff invitation; no existing credentials disclosed. |
| `PUT /orgs/{organization_id}/memberships/{membership_id}/roles` | RoleWrite -> MembershipView | ADMIN; tenant + fresh reauth + last-admin guard | Replace allowed primary grants, audit; cannot grant EVALUATOR here. |
| `POST /orgs/{organization_id}/memberships/{membership_id}/status` | MemberStatusWrite -> MembershipView | ADMIN; tenant + fresh reauth + last-admin guard | Suspend/reactivate tenant membership; revoke tenant authorization immediately. |
| `GET /orgs/{organization_id}/audit-logs` | None -> Page_AuditEvent | ADMIN; tenant + security permission | Read safe significant-change audit, no secret/IP dumps. |
| `GET /orgs/{organization_id}/integrations` | None -> Page_IntegrationView | ADMIN; tenant | Read configured status only. |
| `PUT /orgs/{organization_id}/integrations` | IntegrationWrite -> IntegrationView | ADMIN; tenant + fresh reauth | Change approved configuration references; no provider purchase or secret value in API. |

### Realtime

| Method/path | Request -> response | Role and additional scope | Persistence / result |
| --- | --- | --- | --- |
| `GET /orgs/{organization_id}/events` | None -> SSE | ALL; tenant + per-event current permission | Read bounded safe SSE; no implicit access to all tenant events. |
| `GET /orgs/{organization_id}/events/history` | None -> Page_EventEnvelope | ALL; tenant + per-event current permission | Poll/recover authorized missed event summaries with opaque cursor. |

## Authentication retries and replay — normative review correction

Authentication has no tenant business receipt. Every auth response, including errors and CSRF bootstrap, has `Cache-Control: no-store`; never cache Set-Cookie. All seven POSTs require the session cookie, required X-CSRF-Token and validated same-origin request. A bounded PREAUTH session is sufficient except invitation acceptance, which requires a verified authenticated global user. PUBLIC on these routes means no membership requirement, not absence of preauth/CSRF. Idempotency-Key on auth is rejected400; no password/token-derived fingerprint enters idempotency_records. No response may return an old password, reset/invitation token or session secret.

| Operation | Transaction and safe retry |
| --- | --- |
| Registration | Normalize email; unique global identity, enabled utility/CITIZEN only. Generic duplicate response never changes an existing password or grants. No authenticated session issued. Coalesce verification delivery; a repeated registration may resend verification only to that same still-unverified account under cooldown, never reveal its token. |
| Login | Validate current credentials and limits anew every time; revoke presented old session and rotate cookie/CSRF. Never replay Set-Cookie. Serialize session issuance with reset/suspension and recheck credential version/user state at commit, so in-flight old-password login cannot survive reset. Lost response: bootstrap current CSRF, check /me when a cookie was received, otherwise retry credentials. An unreachable issued session expires; no old token is recovered. |
| Logout | Monotonic revocation plus clear cookie/local vault, no new authenticated token. Recognized revoked/expired verifier plus matching CSRF can authorize cleanup only during its bounded retained lifetime (30days), never business access. Unknown verifier fails401. After cookie clearing, a fresh preauth bootstrap permits harmless cleanup retry. No missing/wrong-CSRF exception. |
| Recovery | Generic accepted response for known/unknown account. Cooldown coalesces delivery without returning an existing token. Later allowed request creates new30min token and invalidates earlier unused reset tokens; store only purpose-bound verifier. No automatic login or secret redisclosure. |
| Password reset | Atomic single-use token consumption + new password hash + revoke all authenticated sessions. No automatic login. Concurrent/replayed/expired/invalid token -> same422; lost reply recovered by login or fresh recovery, never cached success. |
| Email verification | Atomic purpose-bound token consumption and allowed pending activation only, no session issuance or extra grants. Replay/expired/invalid -> same422; login/account state or bounded verification resend resolves lost reply. |
| Invitation acceptance | Verified global user must match invited normalized email. Tenant and exact allowed role come from server invitation; consume/apply in one transaction. No existing active membership prerequisite. Replay/expired/invalid -> same422; lost reply -> /me/memberships. No evaluator self-grant. |

Pilot throttles (tunable, not measured): login/recovery5/min per IP and20/hour per normalized account; register/verification5/hour per normalized account; reset/verify/invitation10/min per preauth/session and IP. Registration/verification/recovery delivery cooldown60seconds per purpose/account with bounded attempts. Rate limits apply to failures and generic responses; do not reveal account existence. Logout uses the general120/min/session limit. Use bounded in-memory buckets with daily-rotated HMAC identifiers and <=24h expiry; never put passwords/tokens into bucket keys or logs. Multi-instance deployment must provide shared bounded limits before exposure.

Pretenant email delivery must not invent a tenant/member to enter background_jobs/notifications. Use a bounded post-commit private mail adapter for auth delivery; token plaintext exists only transiently for that send, never in the business outbox/cache/log. Delivery failure leaves generic response and an expiring unusable verifier; after cooldown, retry creates a new token and revokes the older one. Durable auth-email retry would need a separately reviewed encrypted global outbox later. Global auth security events go to restricted, minimized server security logs (safe outcome/request ID/opaque identity reference, no submitted email/password/token/IP dump), not fabricated tenant audit rows. Tenant grant actions still produce tenant audit receipts.

Global PATCH /me and DELETE /me/sessions/{session_id} also reject Idempotency-Key. Apply only reauthorized self-owned final state; profile version conflict -> refetch, repeated revocation stays revoked. No response cache. Ordinary tenant complaint/task/repair/ingestion writes retain seven-day actor+tenant+method+route+nonsecret-body receipts, with authorization rechecked before replay. Device-credential issuance returns its secret only on first success, no-store; same-key retry409 omits it. Lost issuance reply requires authorized revocation and a new key, never retrieving a prior secret.

## Public project contact — fixed server ownership

POST /public/contact is a HYDROOVERITY project-team contact form, separate from utility leak complaints and authenticated tenant feedback. ContactWrite accepts only category QUESTION/FEEDBACK, message10..2000 and optional reply_email<=254. Reject owner/organization/member/assignee/storage fields via additionalProperties:false. Preauth cookie, CSRF and Origin are required; no arbitrary tenant selection. Persist in global project_contact_submissions, not feedback_items (which requires a real member). Fixed ownership is the server's project inbox repository; the caller never supplies a routing tenant. Generic202 contains only Message, no record ID/read token; there is no public inbox read/list API.

Cap body8KiB; rate-limit3/min per session and daily-rotating IP HMAC, plus5/day normalized reply email when supplied. Buckets expire<=24h; no raw IP in inbox rows. Reject control/header injection; render escaped plain text; no attachments, automatic reply/forwarding, URL fetch or HTML execution. Limit total stored intake and fail503 when capacity is reached rather than claim successful persistence. Designated project operator uses a restricted support procedure with audit/least privilege; tenant ADMIN has no inherited inbox access. Contact intake remains disabled until that operator, access and deletion job are configured. Delete text/email/row after30days. These pilot policies require review before public deployment.

Contact rejects Idempotency-Key400. A lost response may cause a bounded duplicate submission; UI shows a pending/uncertain state and permits deliberate retry after throttle, never promises exactly-once delivery or stores a secret receipt. Utility-specific routing remains deferred and would require a separate allow-listed public utility contract with ownership derived from enabled slug, not internal tenant UUID.
