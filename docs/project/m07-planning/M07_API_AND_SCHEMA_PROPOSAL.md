# HYDROOVERITY — M07 proposed API and schema catalogue

**PROPOSED, NOT REGISTERED OR IMPLEMENTED.** Companion to the [engineering design and acceptance plan](M07_SERVICE_MANAGEMENT_ENGINEERING_PLAN.md), against M04 head `196a5902e8be77a8017c1a97e9abad671345b2c9`. These Markdown shapes are review material, not a replacement for canonical M02 OpenAPI. No application or contract file is changed. Freeze exact schema names and operation IDs only after owner approval and design consistency checks.

**Owner review update:** apply the [conditional approval record](M07_OWNER_REVIEW_DECISION.md) before reconciliation. Retain the proposed 44+11 inventory for review, but exclude PDF/arbitrary documents, external email/SMS/push and offline support from initial enabled scope. Preserve all existing 58 operation contracts. No canonical update may begin until the M04 approval/merge/main-CI gate is satisfied.

## 1. Wire conventions and authorization

Base `/api/v1`; `O` below abbreviates `/orgs/{organization_id}`. IDs are UUIDs. Every tenant operation requires existing FastAPI authentication and active membership. Cookie writes require existing CSRF and same-origin protection. Actor/owner/tenant are server-derived; reject additional properties, including client roles and storage paths. All JSON requests remain <=16 KiB. Binary content has a distinct <=5 MiB exact-byte route and transport. UTC RFC3339 timestamps with explicit offsets are normalized to UTC ending Z; display Asia/Kolkata. Do not accept naive local timestamps.

All new tenant business writes require UUID Idempotency-Key. A command receipt is `Receipt {id: UUID, version: positive integer, received_at: UTC}` plus its documented typed resource projection; never a raw cached response body. New-entity creation needs an expected parent version where listed; existing mutable resources require If-Match quoted version. No `If-Match:*` wildcard or caller-selected owner. Compound expected versions are required fields; missing child preconditions return 428, stale 412, live capacity/state conflicts 409.

Reads use `Page<T> {items: T[0..100], next_cursor: opaque string|null, as_of: UTC}`. Default limit50/max100; cursor bound to tenant, actor projection/permission, filters and snapshot. `from/to` are finite and ordered, <=31 days; availability additionally respects the configured horizon. Unknown or unauthorized filters fail422/403; never widen results. GET has no business mutation. Private responses/errors/downloads are no-store.

**Role abbreviations:** C=CITIZEN with own service; S=SUPERVISOR for tenant cases; T=TECHNICIAN with current assigned parent; E=ENGINEER with existing technical work read; A=ADMIN for listed governance actions only; M=any active membership for self preferences/notifications. No anonymous service lookup or inherited administrator case access.

For each mutation, the referenced service/work/appointment/window must be in the same tenant and authorized before checking/replaying a receipt. Bind idempotency fingerprints to actual normalized resource IDs, not only the route template. Replay after cancellation returns the safe historical command receipt with current lifecycle, not a stale booking promise. Upload content is ticket/hash retry, not business-response caching. Auth/global `/me` behavior is unchanged.

## 2. New-operation inventory (44 proposed operations)

All schemas named here are defined in sections 4–8. Version targets in the last column define the resource for If-Match; extra expected versions are body fields. Role predicates always supplement those preconditions.

| ID | Method and path | Caller; body -> success response | Version / invariants |
| --- | --- | --- | --- |
| N01 | POST `O/service-requests` | C; ServiceRequestCreate -> 201 ServiceCaseCitizen | Optional origin complaint must be owned/current and no original service already linked; expected_complaint_version if present |
| N02 | GET `O/service-requests` | C own / S tenant; -> Page<ServiceCaseCitizen or ServiceCaseStaff> | Projection chosen by authorized operation mode, never caller-requested arbitrary fields; filters status/category/created range |
| N03 | GET `O/service-requests/{request_id}` | C own / S tenant; -> ServiceCaseCitizen or ServiceCaseStaff | ETag service.version; no T/E/A general case read |
| N04 | GET `O/service-requests/{request_id}/timeline` | C own / S; -> Page<ServicePublicUpdate>; S-only audience=INTERNAL -> Page<ServiceInternalEvent> | Default PUBLIC; citizen INTERNAL request denied403; cursor binds audience, complete ordered history, no arbitrary event JSON |
| N05 | POST `O/service-request-lookups` | C own / S authorized support; ReferenceLookup -> 200 {id, tracking_reference} | Read-only lookup, no business receipt; reject Idempotency-Key; auth/CSRF/Origin and lookup throttle; uniform404 |
| N06 | POST `O/service-requests/{request_id}/follow-ups` | C own; ServiceFollowup -> 201 Receipt | If-Match service; append owner text, optionally wake AWAITING_RESIDENT; receipt updates service.version |
| N07 | POST `O/service-requests/{request_id}/triage` | S; ServiceTriage -> 200 ServiceCaseStaff | If-Match service; explicit allowed edge, own public/internal text; no automatic incident |
| N08 | POST `O/service-requests/{request_id}/transitions` | C own permitted request / S; ServiceTransition -> 200 ServiceCaseCitizen or Staff | If-Match service; child dispositions/version checks; cancellation-pending flag is separate from lifecycle |
| N09 | POST `O/service-requests/{request_id}/public-updates` | S; PublicUpdateWrite -> 201 ServicePublicUpdate | If-Match service; escaped authored update, no default internal-note copy |
| N10 | PUT `O/service-requests/{request_id}/visit-preferences` | C own; VisitPreferencesWrite -> 200 VisitPreferences | If-Match service, expected_preferences_version; state not active visit/terminal |
| N11 | GET `O/service-requests/{request_id}/visit-access` | C own / S necessary dispatch; -> VisitAccess | Separate sensitive read with ETag access version; return version/null marker if never supplied, not an invented address |
| N12 | PUT `O/service-requests/{request_id}/visit-access` | C own; VisitAccessWrite -> 200 VisitAccess | If-Match service, expected_access_version; consent; edits after confirmation flag dispatch review and safe notification |
| N13 | POST `O/service-requests/{request_id}/work-order-links` | S; ServiceWorkLinkWrite -> 201 ServiceWorkLink | If-Match service plus work version; accepted case, triaged operational incident/work, no unauthorized internal ID to resident |
| N14 | GET `O/service-requests/{request_id}/appointment-windows` | C own / S; -> Page<ResidentWindow> | Accepted case, linked eligible work; from/to; no private staff/capacity/other bookings |
| N15 | POST `O/service-requests/{request_id}/appointment-requests` | C own; AppointmentRequestCreate -> 201 AppointmentRequestCitizen | If-Match service, expected window/preference/old appointment versions; one live request; no capacity hold |
| N16 | GET `O/service-requests/{request_id}/appointment-requests` | C own / S; -> Page<AppointmentRequestCitizen or Staff> | Owned/tenant case; safe pending/offer/terminal history |
| N17 | GET `O/appointment-requests/{appointment_request_id}` | C own / S; -> AppointmentRequestCitizen or Staff | ETag request.version; include current own replacement state |
| N18 | POST `O/appointment-requests/{appointment_request_id}/decisions` | S; AppointmentDecision -> 200 AppointmentDecisionReceipt | If-Match appointment request; confirm/offer/decline; all BookingExpectations required for confirm |
| N19 | POST `O/appointment-requests/{appointment_request_id}/accept-alternative` | C own; AlternativeAccept -> 200 AppointmentDecisionReceipt | If-Match request; unexpired exact proposal; server-stored BookingExpectations and safe citizen versions; no staff privilege grant from accepting |
| N20 | POST `O/appointment-requests/{appointment_request_id}/withdrawals` | C own; ReasonWrite -> 200 AppointmentRequestCitizen | If-Match request; PENDING/ALTERNATIVE_OFFERED only; original confirmed visit unaffected |
| N21 | GET `O/service-requests/{request_id}/appointments` | C own / S; -> Page<AppointmentCitizen or Staff> | Current and historical own visits; no global customer schedule |
| N22 | GET `O/appointments/{appointment_id}` | C own / S / T assigned; -> role-specific AppointmentCitizen / Staff / Technician | ETag appointment; T receives safe task brief, never full service/account/contact DTO |
| N23 | POST `O/appointments/{appointment_id}/cancellations` | C own / S; AppointmentCancel -> 200 AppointmentCommandReceipt | If-Match appointment; expected service/work/assignment versions; before check-in policy or pending supervisor decision |
| N24 | POST `O/appointments/{appointment_id}/visit-events` | T current assignment; S administrative correction only; VisitEventWrite -> 201 VisitEventReceipt | If-Match appointment plus work/assignment versions; event-type role and check-in uniqueness; server time |
| N25 | GET `O/dispatch/technicians` | S/A minimal roster; -> Page<DispatchTechnician> | Active TECHNICIAN members eligible for enrollment or enrolled; query status/skill/area; no email/session/other role list |
| N26 | POST `O/dispatch/technicians` | A fresh reauth/reason; TechnicianEnroll -> 201 DispatchTechnician | Current membership version and single dispatch tenant check; no active work with unknown plan; does not grant TECHNICIAN role |
| N27 | PATCH `O/dispatch/technicians/{membership_id}` | A fresh reauth/reason; TechnicianProfilePatch -> 200 DispatchTechnician | If-Match profile; eligibility/skills/caps change flags impacted visits; no silent cancellation or cross-tenant transfer |
| N28 | GET `O/dispatch/technicians/{membership_id}/calendar` | S / T self; -> CalendarSnapshot | from/to <=31 days; T own safe intervals/tasks, S tenant detail; profile/calendar versions |
| N29 | POST `O/dispatch/shifts` | S; ShiftWrite -> 201 Shift | If-Match profile, expected_calendar_version; explicit dated interval |
| N30 | PATCH `O/dispatch/shifts/{shift_id}` | S; ShiftChange -> 200 Shift | If-Match shift plus calendar version; editing/withdrawal cannot invalidate bookings |
| N31 | POST `O/dispatch/blocks` | S; DispatchBlockWrite -> 201 DispatchBlock | If-Match profile/calendar; UNAVAILABLE or WORK_BLOCK; finite range and existing-assignment/work guard |
| N32 | POST `O/dispatch/blocks/{block_id}/release` | S; BlockRelease -> 200 DispatchBlock | If-Match block/calendar/work if linked; release audit; does not cancel related work |
| N33 | POST `O/dispatch/blocks/{block_id}/replacements` | S; BlockReplace -> 201 DispatchBlock | If-Match old block; atomically replace interval; rollback keeps old; no appointment bypass |
| N34 | GET `O/dispatch/appointment-windows` | S; -> Page<StaffWindow> | Staff filters date/area/category/published state; current eligibility |
| N35 | POST `O/dispatch/appointment-windows` | S; WindowPublish -> 201 StaffWindow | If-Match profile, expected calendar/policy versions; explicit finite window/duration/buffers; publish only after full validation |
| N36 | POST `O/dispatch/appointment-windows/{window_id}/withdrawals` | S; WindowWithdraw -> 200 StaffWindow | If-Match window plus calendar version; withdrawal stops new requests, existing confirmations require separate disposition |
| N37 | GET `O/dispatch/workload` | S; -> WorkloadSnapshot | Actual aggregate query, requested range/as_of; planned occupied minutes vs unplanned count, no fake utilization |
| N38 | GET `O/dispatch/policy` | S/A; -> DispatchPolicy | ETag policy; unconfigured values null and booking_enabled false |
| N39 | PUT `O/dispatch/policy` | A fresh reauth/reason; DispatchPolicyWrite -> 200 DispatchPolicy | If-Match policy; impact review, existing promises retain snapshots; incompatible reductions reject or require explicit replanning |
| N40 | GET `O/notification-preferences` | M self; -> NotificationPreferences | Current membership recipient only; ETag preferences.version |
| N41 | PUT `O/notification-preferences` | M self; NotificationPreferencesWrite -> 200 NotificationPreferences | If-Match preferences; supported channel list; no arbitrary delivery email, mandatory timeline not suppressible |
| N42 | GET `O/service-requests/{request_id}/delivery-audit` | S minimal support projection; -> Page<SafeDeliveryAttempt> | No recipient destination/raw provider error; own case only; A uses safe tenant audit, not case content |
| N43 | POST `O/work-orders/{work_order_id}/findings` | T current assignment; InvestigationFindingsWrite -> 201 FindingsReceipt | If-Match work plus assignment version; INVESTIGATION purpose, allowed active status; clean authorized attachments |
| N44 | GET `O/work-orders/{work_order_id}/findings` | S/E tenant / T current assigned; -> Page<InvestigationFindings> | Current parent ACL; citizen cannot read internal findings |

This inventory deliberately separates service responses, internal dispatch and self notification preferences. A generic supervisor membership endpoint or a public appointment calendar is not added. Queue/back-office work uses restricted internal service interfaces, not an unauthenticated worker HTTP route.

## 3. Existing M02-designed operations proposed for implementation (11)

These paths already exist in the design catalogue but are absent from the 58-operation runtime. Their presence here does not activate them. Preserve M02 schemas unless the following explicit deltas are approved.

| Method/path | Existing proposed schema / M07 delta |
| --- | --- |
| POST `O/feedback` | FeedbackWrite -> Feedback; add optional service_request_id and service_rating (1..5); authorize own service; no arbitrary owner/assignee |
| GET `O/feedback` | Page<Feedback>; retain own citizen projection; add optional authorized service filter; no internal GitHub/assignee data to resident |
| POST `O/feedback/{feedback_id}/review` | FeedbackReview -> Feedback; S/A current permission; If-Match; resolution reason; no automatic external issue creation |
| POST `O/attachments` | UploadStart -> UploadTicket; add SERVICE_REQUEST purpose and its authorized parent; existing COMPLAINT/WORK_ORDER/REPAIR/FEEDBACK only when their runtime supports links; SERVICE_TEST stays deferred |
| PUT `O/attachments/{attachment_id}/content` | Bounded binary -> Attachment; one owner ticket/hash; no JSON/base64, no general body-limit increase; same-origin CSRF |
| POST `O/attachments/{attachment_id}/complete` | Empty JSON -> 202 Attachment while queued/scanning; must not claim CLEAN synchronously before validation; seal ticket once |
| GET `O/attachments/{attachment_id}` | Attachment status; owner/parent ACL; no storage key/scan internal details |
| GET `O/attachments/{attachment_id}/download` | Authorized CLEAN derivative binary only; no-store/nosniff; parent ACL/current assignment; resident-visible audience guard |
| DELETE `O/attachments/{attachment_id}` | Owner permitted deletion with If-Match; pin/hold check; tombstone; worker rechecks before publication |
| GET `O/notifications` | Page<Notification>; current recipient only; safe messages and status; no raw domain event |
| POST `O/notifications/{notification_id}/read` | Receipt; recipient only; If-Match notification; monotonic read; receipt replay never grants others access |

**Explicit reviewed changes to current operations:**

- `POST O/work-orders`: optional task_purpose default REPAIR for old clients; INVESTIGATION only after new findings rule is implemented. Existing incident requirement remains.
- Existing assignment/transitions/actions/repairs: scheduler-aware assignment/cancellation guards and clean attachment validation; old empty attachment arrays continue working. Final repair/verification semantics remain unchanged.
- Existing WorkerBrief: safe optional appointment/access/findings context only for current assigned technician; preserve 15-minute validity and no offline grant until separately reviewed. Exact address/contact scope is an owner decision, not a silent broadening.
- Existing complaint reads/history stay compatible; new full service timeline is cursor-paginated. No automatic conversion of old complaints into accepted service requests.
- Feedback schemas may add optional service fields; add service_request_id to the typed attachment-link target. PDF media enum expansion and derivative metadata require separate owner approval; existing image-only API must reject PDF until then.
- M02 Feedback and Notification DTOs currently omit the mutable version needed by their review/read preconditions. Add a reviewed version field to their read projections and ETags before enabling those actions; do not ask clients to guess versions. The same applies to Attachment.version for deletion. These are explicit contract-usability corrections, not evidence of current runtime support.
- Root request body/parser/proxy limits need a route-specific binary exception only for the validated content endpoint. Same JSON/CSRF/auth/security policies remain elsewhere.

If all 44 new operations and all 11 deferred operations are ultimately implemented, the runtime would contain 113 operations (58+44+11), while the updated design catalogue would contain 161 (117+44). These are **planning counts**, not claims of implementation. Conditional media/email/offline scope may change the approved count; do not force a numeric target or enable other deferred M02 endpoints merely to meet it.

## 4. Scalar types, enums and shared responses

Notation below is a schema description, not code. `?` means optional property, `T|null` permits explicit null, and `List<T,n>` has maximum n elements; all objects reject unknown properties. Required fields are listed unless marked optional. PlainText excludes control characters except normal newline/tab where appropriate, is rendered escaped, and has the given character limit. Validation must also enforce the overall byte cap. Mutable row versions are >=1. Nullable child versions mean no child row exists yet; null is compared atomically, never treated as “ignore precondition.”

| Type | Proposed definition |
| --- | --- |
| ServiceCategory | Existing VISIBLE_LEAK / LOW_PRESSURE / SERVICE_INTERRUPTION only |
| ServiceStatus | SUBMITTED / UNDER_REVIEW / AWAITING_RESIDENT / ACCEPTED / SERVICE_IN_PROGRESS / SERVICE_REVIEW_PENDING / SERVICE_CLOSED / DECLINED / WITHDRAWN / CANCELLED |
| ServiceOutcome | ADVICE_PROVIDED / VISIT_COMPLETED / REPAIR_REPORTED / REFERRED / NO_ACTION_WITH_REASON |
| ServiceVerificationSummary | NOT_APPLICABLE / PENDING_REVIEW / NOT_VERIFIABLE; never PASSED merely through M07 |
| AppointmentRequestStatus | PENDING / ALTERNATIVE_OFFERED / CONFIRMED / DECLINED / WITHDRAWN / EXPIRED |
| AppointmentStatus | CONFIRMED / CHECKED_IN / VISIT_FINISHED / NO_ACCESS / ABORTED / NO_SHOW / CANCELLED / SUPERSEDED |
| Interval | {start_at: UTC, end_at: UTC}; finite, start<end; half-open semantics |
| ReasonWrite | {reason_code: allowlisted action-specific code<=40, reason: PlainText5..1000} |
| CalendarVersion | positive integer; increment on booking/block/shift/window/roster eligibility change; cannot be set by client |
| TaskPurpose | REPAIR / INVESTIGATION; default REPAIR for old work/clients |
| SafeDeliveryState | QUEUED / SENDING / DELIVERED / RETRY_WAIT / FAILED / SUPPRESSED / DELIVERY_UNKNOWN |
| Error | Existing {error:{code,message,request_id,field_errors:[{field,message}]}}; no SQL/colliding identifiers/provider trace |
| ServicePublicUpdate | {id, sequence: positive integer, event_kind: allowlist, message: PlainText<=2000, occurred_at: UTC, published_at: UTC, appointment_id: UUID|null, supersedes_id: UUID|null}; appointment_id only if from same own case |
| ServiceInternalEvent | S-only {id, sequence, event_kind: allowlist, actor_membership_id: UUID|null, received_at: UTC, observed_at: UTC|null, internal_reason: PlainText<=2000, resource_type: allowlist, resource_id: UUID|null, previous_version: positive|null, resulting_version: positive|null, supersedes_id: UUID|null}; no raw JSON serialization, access instructions or file contents |
| CommandReceipt<T> | {receipt: Receipt, resource: T}; if compound, explicit named versioned projections replace generic resource; never issue a secret |

Error matrix: 400 malformed/forbidden idempotency header; 401 session expired; 403 permission/CSRF/Origin/action denied; 404 unknown or inaccessible; 409 state/slot/assignment/idempotency conflict; 412 stale version; 413 byte limit; 422 body/range/type/unknown filter; 428 missing precondition; 429 bounded quota/rate; 503 persistence/queue/scanner unavailable. Existing app error shape and Retry-After policy remain. For asynchronous scanning, unavailable processing yields a durable pending/quarantine status; do not return synchronous CLEAN.

## 5. Service and visit schemas

### ServiceRequestCreate

Required: category, description (10..2000), coarse_area (2..200), origin_complaint_id (UUID|null), expected_complaint_version (positive|null), follow_up_of_id (UUID|null), service_privacy_acknowledged (true).

Rules: origin complaint belongs to the caller/tenant and category/coarse data must be reviewed if copied; expected version is mandatory/non-null only with origin complaint. Follow-up of a terminal own service uses a new ID/reference and no reused origin complaint link. Initial submission does not include accepted/status/assignee/incident fields, attachments, exact GPS or arbitrary user ID. Intake consent for service handling is distinct from photo consent/marketing preferences.

### ServiceCaseCitizen

Required: id, tracking_reference (server random128-bit, e.g. `HYS-` plus 26 Crockford-base32 symbols), category, description, coarse_area, status, cancellation_pending (boolean), service_outcome (ServiceOutcome|null), verification_summary, created_at, updated_at, accepted_at (UTC|null), version, own_origin_complaint_id (UUID|null), own_follow_up_of_id (UUID|null), preferences (VisitPreferences|null), latest_public_update (ServicePublicUpdate|null), current_appointment (AppointmentCitizen|null), allowed_actions (allowlisted strings<=20).

Do not include internal incident/work/profile IDs, other-case links, resident/user IDs, staff email/name/contact, exact infrastructure locations, internal reasons or notes. Allowed_actions helps UX; the server still reauthorizes. Timeline is independently paginated. Keep visit access separate even from ordinary case lists.

`ServiceCaseStaff` is a separate schema: citizen-safe fields plus service owner opaque membership ID, authorized internal work/incident link IDs, dispatch health, pending request IDs, internal lifecycle event summary and current versions. It is supervisor-only; do not build it by serializing the ORM row. Full sensitive access is still N11, not embedded in list rows.

### Lookup, follow-up, triage and transitions

- ReferenceLookup: `{tracking_reference: string6..40}`, normalized case-insensitively; POST body avoids URLs/logs; login and ownership mandatory. The reference is an identifier, not a secret recovery credential. S support lookup still requires tenant case permission.
- ServiceFollowup: `{operation_id: UUID, message: PlainText1..2000}`. Parent If-Match; immutable owner-authored safe event; terminal case gets409 with follow-up-case guidance. Attach photos after the case exists through the attachment service.
- ServiceTriage: `{target: UNDER_REVIEW|AWAITING_RESIDENT|ACCEPTED|DECLINED, public_message: PlainText5..1000, internal_reason: PlainText5..2000}`. State graph restricts edge; acceptance has no incident_id input and creates no incident.
- PublicUpdateWrite: `{event_kind: INFORMATION|PROGRESS|CORRECTION, message: PlainText5..2000, supersedes_update_id: UUID|null}`. Correction references same-case update and retains tombstone/history; no arbitrary supersession of another resident's update.
- ServiceTransition is a discriminated union with `action`: WITHDRAW (C preacceptance); REQUEST_CANCELLATION (C after acceptance); CANCEL (S); START_SERVICE / REQUEST_REVIEW / RETURN_TO_WORK / CLOSE (S/system-eligible rules). All carry reason_code and public_message5..1000. Staff-only variants add internal_reason5..2000; CLOSE adds service_outcome and expected_open_work_versions (List<{work_order_id,version},20>); CANCEL adds explicit child_dispositions (List<{appointment_id,expected_version,action:CANCEL|KEEP_FOR_SHARED_WORK},20>) and expected_work_versions. Never let customer fields specify staff decisions. REQUEST_CANCELLATION sets pending metadata without pretending child bookings are cancelled; response returns current lifecycle plus pending flag.

### VisitPreferences / VisitPreferencesWrite

Read: `{version, intervals: List<Interval,5>, access_needs: PlainText<=500, updated_at}`. Write: `{expected_preferences_version: positive|null, intervals: List<Interval,5>, access_needs: PlainText<=500}` with parent If-Match service.

Each interval must fall in the configured horizon and be nonoverlapping; no more than 31 days total query window. Preferences are requests, not publication/booking. Avoid sensitive medical detail. Only resident edits initially; S asks for an update instead of impersonating the resident. Updating preferences does not move a confirmed visit.

### VisitAccess / VisitAccessWrite

Read: `{version: positive|null, site_text: PlainText<=500|null, safe_access_instructions: PlainText<=500|null, consented_at: UTC|null, updated_at: UTC|null}`; null values indicate none supplied. Write: `{expected_access_version: positive|null, site_text: PlainText1..500, safe_access_instructions: PlainText<=500, technician_disclosure_consent: true}` with parent If-Match. Server encrypts at rest; no contact/address in generic audit/outbox.

T receives only the necessary instructions for a currently assigned confirmed visit in AppointmentTechnician/WorkerBrief, not N11. A changed address after confirmation sets REVIEW_REQUIRED, suppresses inaccurate reminders and alerts supervisor; the system does not silently route a technician to a new address. Confirmation requires supervisor review of sufficient visit instructions, not compulsory GPS/phone data.

### ServiceWorkLinkWrite / ServiceWorkLink

Write: `{work_order_id, expected_work_version, purpose: INVESTIGATION|REPAIR, internal_reason: PlainText5..2000}`; service If-Match. Work's purpose must match; source incident is triaged operational data. Read S-only: `{id, service_request_id, work_order_id, purpose, created_at, version}`. Multiple cases may link the same work, but no resident gets other-case/work IDs. Unlinking completed work is not exposed; incorrect links need append-only correction procedure, never history rewriting.

## 6. Scheduling, appointment and dispatch schemas

### ResidentWindow and StaffWindow

ResidentWindow: `{id, version, arrival_start: UTC, arrival_end: UTC, timezone: const Asia/Kolkata, expected_service_minutes: integer1..480, policy_version, as_of: UTC, confirmation_required: true}`. Return only windows currently eligible for the specific accepted case; no bookable staff count or full calendar. The displayed duration is an estimate, not a fabricated measured time. A window can become unavailable before confirmation.

StaffWindow adds `{technician_membership_id, calendar_version, category_codes: List<ServiceCategory,3>, service_area_codes: List<string1..40,20>, before_buffer_minutes: integer0..240, after_buffer_minutes: integer0..240, state: PUBLISHED|WITHDRAWN, occupied_interval: Interval}` and authorized conflict health. These bounds are input safety caps, not policy defaults; utility policy must be configured within them.

### AppointmentRequestCreate / read

Create: `{kind: INITIAL|RESCHEDULE, window_id, expected_window_version, expected_preferences_version: positive|null, replaces_appointment_id: UUID|null, expected_appointment_version: positive|null, message: PlainText<=500}`. Parent service If-Match. INITIAL requires null replacement/version and no current active appointment. RESCHEDULE requires the case's current CONFIRMED appointment/version. One live request per case, policy horizon/lead time checked, no reservation or promise made.

AppointmentRequestCitizen: `{id, service_request_id, kind, status, requested_window: ResidentWindow, alternative_window: ResidentWindow|null, offer_expires_at: UTC|null, replaces_appointment_id: UUID|null, confirmed_appointment_id: UUID|null, public_message: PlainText<=1000|null, created_at, updated_at, version}`. Staff schema adds only authorized decision/work/assignee revision context and internal reason, not to the citizen schema.

### BookingExpectations

Required fields: `{service_version, work_order_id, work_version, assignment_version, window_version, calendar_version, policy_version, replaced_appointment_version: positive|null}`. All versions are positive integers unless null is explicitly allowed. Values come from authorized projections; the citizen alternative acceptance receives a server-bound proposal revision/token rather than hidden staff/work IDs.

**Citizen-safe equivalent:** AlternativeAccept carries `{proposal_revision: positive, expected_window_version: positive, expected_service_version: positive, expected_replaced_appointment_version: positive|null}`. The authenticated owned request/proposal row binds the offered safe window and supervisor-reviewed internal BookingExpectations. Store an immutable proposal revision and its expectations when offering; expire it with the offer. Only authenticated own-request acceptance is allowed. A proposal ID/revision is not a credential. The transaction reads the internal work/calendar/policy expectations from that stored proposal and repeats all live checks; no extra login system or bearer token is needed.

This explicit distinction prevents exposing internal work/profile identifiers merely so a resident can accept an alternative. A changed internal plan invalidates the proposal and returns a safe conflict requiring a refreshed offer.

### AppointmentDecision

Discriminated by `decision`:

- CONFIRM_REQUESTED: `{decision, expectations: BookingExpectations, public_message: PlainText5..1000, internal_reason: PlainText5..2000}`. S can confirm only the requested published window; work/assignee binding and occupied interval are server-derived.
- OFFER_ALTERNATIVE: `{decision, alternative_window_id, expected_window_version, expectations: BookingExpectations, offer_expires_at: UTC, public_message: PlainText5..1000, internal_reason: PlainText5..2000}`. No reservation; binds reviewed work/plan. Request status changes to ALTERNATIVE_OFFERED; resident must accept.
- DECLINE: `{decision, reason_code, public_message: PlainText5..1000, internal_reason: PlainText5..2000}`. No original appointment is cancelled by declining a replacement.

AppointmentDecisionReceipt: `{receipt: Receipt, request: role-specific AppointmentRequest, appointment: role-specific Appointment|null, replaced_appointment: role-specific Appointment|null}`. Staff receipt additionally carries new work/assignment/calendar versions; citizen receipt never does. No automatic confirmation if email fails; booking and in-app state are authoritative.

### Appointment read schemas

AppointmentCitizen: `{id, service_request_id, status, arrival_start, arrival_end, expected_service_minutes, timezone: Asia/Kolkata, public_visit_message: PlainText<=1000|null, cancellation_pending: boolean, replaces_id: UUID|null, version, created_at, updated_at, allowed_actions: List<string,10>}`.

AppointmentStaff adds request_id, window_id, work_order_id, assignee_membership_id, assignment_version, occupied_interval, calendar/policy revision, dispatch_health, internal reason and attendance metadata. AppointmentTechnician is a separate minimal schema: `{id,status,arrival_start,arrival_end,expected_service_minutes,work_order_id,assignment_version,work_version,version,safe_access_instructions,safe_task_instructions,brief_expires_at,allowed_actions}`. No resident email/name/contact, other visits or internal topology. It is reauthorized on every read/action and expires by the existing 15-minute brief policy.

### AppointmentCancel / visit events

AppointmentCancel: citizen form `{reason_code, public_reason: PlainText5..1000, expected_service_version}`; staff form adds `{internal_reason, expected_work_version, expected_assignment_version, disposition: CANCEL|ACCEPT_PENDING_CANCEL|DECLINE_PENDING_CANCEL}`. For citizen cancellation, server loads work/assignment revisions under locks rather than disclosing them; If-Match appointment plus current service protects stale requests. A cutoff/checked-in rule returns a cancellation-pending receipt, not false CANCELLED. AppointmentCommandReceipt contains `{receipt,appointment: role-specific Appointment,current_service_version}`.

VisitEventWrite: `{operation_id, event_type: CHECK_IN|VISIT_FINISHED|NO_ACCESS|ABORTED|OVERRUN_REPORTED|ADMIN_CORRECTION, observed_at: UTC, assignment_version, expected_work_version, note: PlainText1..2000, supersedes_event_id: UUID|null}`. Appointment If-Match. T may record the first five types only on its current assignment; S only ADMIN_CORRECTION with a reason and same-appointment supersedes event. Completion of visit does not transition work to COMPLETED. If observed time >server+5 minutes, reject422; older delayed manual time is labeled and allowed only within approved task/visit ordering, never backdate a booking. Server records received_at separately. Response VisitEventReceipt contains `{receipt, appointment: role-specific Appointment}`.

### Roster, shifts and blocks

DispatchTechnician: `{membership_id, display_name: string<=100, enrollment_state: ELIGIBLE|ENROLLED|UNAVAILABLE, active: boolean, skill_codes: List<string1..40,20>, service_area_codes: List<string1..40,20>, max_daily_minutes: integer1..960|null, profile_version: positive|null, calendar_version: positive|null, scheduling_health: READY|UNPLANNED_WORK|REVIEW_REQUIRED|UNCONFIGURED}`. Name is a dispatch identity, not citizen-facing staff contact. A nonenrolled eligible entry has null versions; membership version is returned to A for governance, not roster clients indiscriminately.

TechnicianEnroll: `{membership_id, expected_membership_version, skill_codes, service_area_codes, max_daily_minutes, exclusive_dispatch_acknowledged: true, reason: PlainText5..2000}`. Current active TECHNICIAN grant required; no implicit role assignment. Unknown caps/active work plans block READY publication. TechnicianProfilePatch: same mutable fields plus active and reason, all explicit; no user/tenant reassignment. Existing bookings require impact review/replanning when disabling/skills change; revoked role immediately denies new work regardless of profile flag.

ShiftWrite: `{technician_membership_id, expected_calendar_version, interval: Interval, reason: PlainText5..2000}`; If-Match profile. Shift read: `{id,technician_membership_id,interval,status: ACTIVE|WITHDRAWN,version,calendar_version}`. ShiftChange: `{interval,status,expected_calendar_version,reason}` with If-Match shift. No interval includes a break implicitly; blocks account for those separately. Finite shifts <=24h; longer duty periods need multiple reviewed shifts, not unbounded ranges.

DispatchBlockWrite: `{technician_membership_id, expected_calendar_version, kind: UNAVAILABLE|WORK_BLOCK, interval: Interval, work_order_id: UUID|null, expected_work_version: positive|null, reason_code: allowlist, internal_reason: PlainText5..2000}`. WORK_BLOCK requires same-tenant currently assigned work and version; UNAVAILABLE requires null work fields. Work block cannot alter/cancel an appointment allocation through this endpoint. DispatchBlock read returns id/profile/kind/interval/work_id/internal reason/version/calendar_version to S; T self only gets safe occupied interval/kind/own task, not private leave explanations.

BlockRelease: `{expected_calendar_version, expected_work_version: positive|null, reason}`; If-Match block. BlockReplace adds interval; atomic replacement preserves old on failure. Releasing a work block with active unplanned work marks scheduling health UNPLANNED_WORK, not free capacity. Preserve blocked history and relationship to work.

### WindowPublish, policy, calendar and workload

WindowPublish: `{technician_membership_id,expected_calendar_version,expected_policy_version,arrival_start,arrival_end,expected_service_minutes,before_buffer_minutes,after_buffer_minutes,category_codes,service_area_codes,reason}` with profile If-Match. Arrival width must be positive <=8h and within policy; expected_service_minutes1..480, buffers0..240; full conservative occupied interval must fit the shift and daily cap. Published windows cannot promise a different arrival range than they reserve. WindowWithdraw: `{expected_calendar_version,reason}` with window If-Match; current bookings remain until explicit cancellation/replacement.

DispatchPolicy read: `{version,booking_enabled:boolean,configured:boolean,horizon_days:integer1..60|null,minimum_lead_minutes:integer0..10080|null,free_cancel_before_minutes:integer0..10080|null,max_arrival_width_minutes:integer1..480|null,request_expiry_hours:integer1..168|null,offer_expiry_hours:integer1..72|null,max_daily_minutes:integer1..960|null,allowed_duration_minutes:List<integer1..480,20>,minimum_before_buffer_minutes:integer0..240|null,minimum_after_buffer_minutes:integer0..240|null,updated_at}`. These ranges are validation caps, not an assumed utility schedule.

DispatchPolicyWrite supplies every configured policy field and reason, no nulls when enabling booking. Migration seeds a disabled UNCONFIGURED singleton, not made-up operating hours. Policy changes keep appointment snapshots; a newly stricter live safety cap cannot silently declare old promises valid. Reject incompatible changes until a reviewed replanning disposition exists. No recurrence engine, holiday provider or unlimited booking horizon is included.

CalendarSnapshot: `{profile_version,calendar_version,as_of,timezone,shifts:Page<Shift>,blocks:Page<role-specific DispatchBlock>,appointments:Page<role-specific Appointment>}`. Each collection has its own filter/scope-bound cursor; all bind the same calendar revision. A changed revision requires a refreshed snapshot. In a busy range, pagination must be complete before the UI claims the interval is free; the booking transaction always queries all DB allocations directly, not the client page.

WorkloadSnapshot: `{as_of,from,to,timezone,items:List<WorkloadRow,100>,next_cursor}`. Row: `{technician_membership_id,confirmed_appointments,planned_occupied_minutes,unplanned_work_count,overdue_work_count,available_shift_minutes,known_load_ratio:number|null,scheduling_health}`. Available minutes are shift union minus UNAVAILABLE block union; planned minutes are APPOINTMENT/WORK_BLOCK occupied union only, not leave/breaks. Include reserved travel/setup buffers. Ratio is planned/available, null when denominator unknown/zero or unplanned work remains. Counts use the complete authorized query, not the current visible page, and do not represent efficiency/performance of a person. No customer names/contacts or scientific metrics.

## 7. Investigation, communication, feedback and attachment deltas

### InvestigationFindingsWrite / read

Write: `{operation_id,assignment_version,observed_at:UTC,findings:PlainText10..4000,no_repair_reason:PlainText5..2000,attachment_ids:List<UUID,10>,supersedes_id:UUID|null}` with work If-Match. Work purpose INVESTIGATION, current assigned T and allowed IN_PROGRESS/BLOCKED state required. All attachment IDs are CLEAN, same tenant/owner and authorized parent. No schema fields for leak_confirmed, measured_savings or verification_passed.

Read: `{id,work_order_id,recorded_by_membership_id,observed_at,received_at,findings,no_repair_reason,attachment_ids,supersedes_id,provenance:const MANUAL}`; staff technical/assigned only. FindingsReceipt is CommandReceipt<InvestigationFindings>. Parent work version increments; findings supersede rather than edit. Investigative task submission requires at least one nonsuperseded valid findings receipt. Existing REPAIR purpose retains actual repair receipt requirement.

### Notification preferences / audit

NotificationPreferences: `{version,channels:{in_app:boolean,email:boolean},event_categories:List<SERVICE_PROGRESS|APPOINTMENT|WORK_ASSIGNMENT|SERVICE_FEEDBACK,4>,quiet_hours:{start_local:HH:mm,end_local:HH:mm,timezone:Asia/Kolkata}|null,email_available:boolean}`. One versioned row per tenant membership; backfill/create a minimal in-app default when membership is provisioned, not on a GET. Timeline remains available regardless of optional alert preferences. Empty categories disable optional alerts; mandatory in-product commitment state remains.

Write: channels/event_categories/quiet_hours only; no recipient ID, arbitrary address or provider secret. Reject enabling email when adapter/verified address/consent gate unavailable; never pretend it is delivered. Turning off in-app optional alerts does not hide case history. Existing notification.read requires current recipient even after list/load; display DELIVERED as channel receipt, not guaranteed human reading.

SafeDeliveryAttempt: `{notification_id,event_kind,channel,state,attempt_number:integer0..3,attempted_at:UTC|null,next_attempt_at:UTC|null,safe_error_code:string<=40|null}`. No provider response, email address, attachment URL or raw text body. Case support is S only; ADMIN sees restricted delivery-health/audit information through its existing audit rights, not the case endpoint.

### Feedback compatibility

Retain M02 FeedbackWrite summary5..200/description5..2000/complaint_id nullable. Add optional service_request_id UUID|null and optional service_rating integer1..5|null. If a service link is present it must be an owned SERVICE_CLOSED case (or a permitted cancelled-case experience); do not also accept an unrelated complaint link. For internal product feedback both links may be null. Citizen feedback returns only own safe Feedback with optional service ID/rating and public resolution, never internal assignee/GitHub issue data. Rating has no verification/incident transition side effect. A recurrence request creates a linked new service case after resident confirmation rather than changing the old outcome.

### Attachment review delta

Preserve M02 UploadStart fields purpose/target_id/media_type/size_bytes/sha256/consent:true. Add SERVICE_REQUEST purpose; typed link has service_request_id and exactly one parent FK per link. Default approved formats remain JPEG/PNG/WebP. PDF is disabled until D7; accepting an enum in documentation is not permission to serve documents.

Extend storage metadata internally with original_digest, derivative_digest, processor_version, scan_verdict/version, quota reservation, scan/job refs, deletion/hold state and audience. Public Attachment exposes id/status/size/media/expiry/version and a safe reason code (SCANNING/UNSUPPORTED/REJECTED/EXPIRED), never storage paths/raw scanner output. UploadTicket exposes an authenticated same-origin path, expiry and ID only. `/complete` can return QUARANTINED while processing; download denies unless all security gates are complete.

Audience defaults: resident-origin photos OWN_CASE; technician work/repair photos INTERNAL_TASK. Publishing an internal derivative to the resident requires an explicit supervisor review action and audit. For the initial release, omit that publication API and keep all internal work media private; customer-safe textual summaries suffice. Resident photos may be disclosed to current authorized assigned staff only through a server-derived task-safe evidence link, never all photos on a shared incident. This cross-domain link must be typed/audited and tenant/ownership checked; one case link is not permission to read other residents' media.

Document gate, if approved: input application/pdf only; <=5 MiB, <=20 pages, no active/encrypted/embedded content; sandbox scan/render/rebuild, <=12 MP/page/60 MP total and configured time/memory/output-byte caps; clean derivative only. It must have the same ownership/consent/quota/retention/scan states and fail closed. No office/archive upload, public original or arbitrary URL import.

## 8. Contract acceptance examples and edge cases

| Scenario | Required outcome |
| --- | --- |
| Service reference is guessed, caller unauthenticated | 401; login needed; no record existence/content |
| Logged-in resident uses another resident's valid reference | Same generic404 as unknown reference; no timing/content distinction claimed without testing |
| Old complaint is linked to a service twice | Safe409 ORIGINAL_SERVICE_EXISTS; return own existing case link only after ownership check |
| Request a published window then someone else confirms it | Pending request persists; confirmation/alternative accept fails409; no duplicate allocation, no confirmed UI |
| Two S transactions confirm overlapping different windows for one technician | Exactly one commit; other safe409; no leaking collision metadata |
| Two tenants enroll one physical global user concurrently | Exactly one dispatch enrollment; loser generic unavailable, no other tenant data |
| Reschedule fails assignment/policy/capacity check | Original appointment/allocation unchanged; request has safe pending/conflict disposition |
| Customer alternative request/proposal reference is copied to another account | 404/403 uniformly according to authenticated resource rule; no booking or internal data |
| Alternative accepted after work/roster/policy changed | Safe412/409 requiring refreshed offer; do not silently accept stale plan |
| Reassigned worker replays old repair/photo/visit request | Current assignment denial before receipt; no file download or new receipt |
| Legacy assignment attempts to change a booked worker | 409 SCHEDULE_CHANGE_REQUIRED; use atomic dispatch path |
| Investigation task has findings and no repair | Valid submission for supervisor operational review; no manufactured repair/verification row |
| Repair task has no actual repair receipt | 409 REPAIR_REQUIRED as existing behavior |
| Work completes or customer rates five stars | No VERIFICATION_PASSED, no incident RESOLVED without existing scientific guards |
| Photo scanner is unavailable or worker dies | QUARANTINED with honest pending/failure state; download denied; bounded retry/expiry |
| PDF sent before approved pipeline enabled | 422 unsupported format; no silently stored/served document |
| Membership revoked during download/booking | Recheck current access at authorization/commit boundary; revoke further reads/emission; no false remote-erasure guarantee |
| Late cancellation while technician checked in | Pending/correction workflow, not pretend-unattended cancellation or silent work stop |
| HTTP reply lost after successful commit | Deliberate identical retry returns receipt/current state; owned list/detail also reveals committed result |

## 9. Review/change protocol

First reconcile this proposed catalogue with D1–D10 in the main plan. Then, only after owner implementation authorization, add approved API/schema/permission/DB/route metadata together and validate it before migrations or code are enabled. Maintain explicit implemented/deferred inventories; update generated frontend types from the actual reachable implementation. Keep tests and documentation tied to the source commit and migration head. The owner reviews the complete result; this plan neither merges M04 nor begins M06/scientific integration.
