# M07 contract reconciliation — review candidate

**Contract-only proposal. No M07 endpoints, tables, routes, jobs or uploads are implemented.**

The [engineering report](../../engineering/M07_CONTRACT_RECONCILIATION_REPORT.md) records the verified M04 closure, compatibility proof, executed design checks, discrepancies and outstanding owner gates. The preserved [owner decisions](../../project/m07-planning/M07_OWNER_REVIEW_DECISION.md) govern the scope. Their earlier observation that M04 was unmerged is historical; the report records the subsequent successful closure gate.

## Contract authority and composition

The existing [M02 OpenAPI](../openapi-design.json), API inventory, 57-table database catalogue, role/state specifications and 46-route catalogue remain the deployed design revision consumed by M03/M04. They are not replaced by this candidate. M03 reads those JSON files at runtime, so silently widening them would risk registering future operations or altering validation. All 171 locked M03/M04/M05/M08 and legacy machine-contract files remain byte-identical to verified main.

The [M07 candidate OpenAPI](openapi-proposed.json) composes all 117 baseline paths/operations with 44 proposed new operations. It reconciles 11 already-deferred Feedback/Uploads/Notifications operations within their existing IDs; they are not counted twice. Its 58 implemented operations and all existing component schemas are unchanged. New schemas are prefixed M07. Candidate response changes for the 11 deferred paths do not activate them. No application imports this file.

| Catalogue | Designed operations | Implemented operations | Designed tables | Migrated tables | Routes |
| --- | --- | --- | --- | --- | --- |
| Frozen deployed M02/M03/M04 | 117 | 58 | 57 | 30 | 46 current classifications |
| M07 composed review candidate | 161 | Still 58 | 74 | Still 30 | 51 proposed; no new route implemented |

Of 161 candidate operations: 58 are unchanged implemented operations; 44 are new M07 proposals; 11 are selected existing deferred designs; 48 remain outside M07. The potential eventual 113-operation runtime (58+44+11) is not an implementation claim or an acceptance target to manufacture.

Machine-readable review sources:

- [API inventory](../../../data/schemas/m07-api-inventory.json), [operation classifications and compatibility matrix](../../../data/schemas/m07-reconciliation-matrix.json).
- [Database catalogue](../../../data/schemas/m07-database-design.json), [states/concurrency/policy gates](../../../data/schemas/m07-state-machines.json).
- [Route catalogue](../../../design/ui-ux/m07-route-catalog.json), [frozen baseline hashes](../../../data/schemas/m07-baseline-lock.json).
- [Preserved engineering plan](../../project/m07-planning/M07_SERVICE_MANAGEMENT_ENGINEERING_PLAN.md), [API proposal](../../project/m07-planning/M07_API_AND_SCHEMA_PROPOSAL.md), [source hashes](../../../data/schemas/m07-planning-source-manifest.json).

`python scripts/build_m07_contracts.py --check` compares deterministic composed output; `scripts/check_m07_design.py` checks compatibility, roles, model links and policy invariants. Independent OpenAPI validation and adversarial design examples are separate checks. They prove design consistency, not executable authorization or race prevention.

## Approved development order

- **M07-A:** N01–N13 and N43–N44: service intake, owned tracking, safe timelines, preferences/access design, explicit triage/closure, incident/work links, investigation findings. Fifteen new proposed operations.
- **M07-B:** N14–N39: scheduling/dispatch, unit-capacity windows and transactional allocations. Twenty-six new proposed operations. Publishing/requesting/confirming capacity is disabled until actual authorized configuration exists. Configuration, withdrawal and cancellation must remain usable while disabled.
- **M07-C:** N40–N42 plus eleven deferred operations: self in-app preferences, safe delivery audit, images, notifications and feedback. Three new plus eleven existing proposed operations. Images need scanner/processing/storage/license approval; no PDF, external delivery or offline drafts.

After this contract review, additive migrations and operational implementation require another owner instruction. This package neither authorizes them nor merges M07.

## Reconciled database and concurrency contract

Seventeen proposed tables are added to the existing 57-table design, totaling 74. All remain unmigrated. Six service tables separate service_requests, internal events, public updates, visit preferences, encrypted visit access and typed work links. Eleven additional tables cover one restricted global calendar enrollment registry, tenant technician profiles, dated shifts, active allocation ledger, windows, appointment requests, appointments, visit events, dispatch policy, investigation findings and notification preferences.

The proposal's optional `service_outbox_checkpoints` table is omitted. Existing M02 background_jobs gets a proposed same-tenant source_event_id plus a kind/event dedup invariant, providing one queue/outbox strategy. This avoids two fan-out checkpoints/queues. Five existing designed tables have candidate column deltas: work_orders, attachments, attachment_links, feedback_items and background_jobs. Other invariants, including notification attempt caps, are specified without pretending migrations exist.

- Composite same-tenant FKs protect service/work/appointment/attachment relationships. The restricted global enrollment row has unique global user_id and exactly one dispatch utility. Tenant profiles must resolve to the same user and enrollment organization; no global calendar/list API is introduced.
- Active allocation ranges use finite nonempty half-open tstzrange. Proposed GiST exclusion combines organization, subject equality and range overlap, with an active predicate and btree_gist. No current-time expression is used in the predicate. One active checked-in visit per subject and one active appointment per case/work are separate constraints.
- Reserve `[arrival_start-before_buffer, arrival_end+estimated_duration+after_buffer)`. The entire interval must fit explicit shifts and avoid breaks/leave/work blocks; daily caps split by Asia/Kolkata date and include buffers. Unplanned active work blocks publication, not a zero-load assumption.
- Acquire current-membership guards, sorted service roots, sorted work rows, sorted request/appointment rows, actor idempotency lock, sorted subjects/profiles, then windows/shifts. Legacy assignment/actions/cancellation must join this ordering before any future service hooks. Confirm/reschedule/cancel commits allocation, assignment/version, history, safe public update, audit and outbox atomically. Failed replacement restores the original booking.
- Revocation denies new writes/downloads immediately. It does not silently erase an existing commitment. Overruns remain honest manual events and require replanning; the design guarantees scheduled non-overlap inside the enrolled platform scope, not actual travel/arrival duration or external employment availability.

Database invariants here are descriptive constraints for future migration review. No SQL has been generated or executed, and concurrency behavior has not been tested as an M07 service.

## State and scientific boundaries

Service lifecycle, complaint public status, appointment request, confirmed appointment, incident, work order, repair and independent verification remain separate. An INITIAL/RESCHEDULE request holds no capacity. An alternate window requires resident acceptance. Cancellation pending is not CANCELLED. After check-in, record a visit outcome/correction rather than pretending no visit occurred. Service closure is an operational outcome, not incident RESOLVED or VERIFICATION_PASSED.

Investigation-purpose work will require findings rather than fake repair receipts. The candidate includes a named `M07FutureWorkOrderWrite` schema and an explicit future-runtime delta, but does not wire it into the deployed POST work-orders operation. Omitted purpose remains REPAIR in a future compatible implementation. A coordinated activation and purpose-specific submission test is mandatory before these findings endpoints can operate.

All scientific ingestion, HYDRO-WATCH states, GUARD-5 A/B/C/EXT/BYPASS, common-clock HYDRO-EAR, M05 results and M08 digital-only caveats stay frozen. Manual evidence remains NOT_VERIFIABLE; ratings, photos and attendance never satisfy measured comparability. No M06 work is included.

## Privacy, permissions and safe schemas

Every candidate operation specifies roles, a required permission, tenant/current-parent guards, idempotency policy and the exact If-Match resource where required. Reusing a permission code does not bypass per-operation roles or own/assigned/self checks. ADMIN has governance only; no general case-content or technical access. Supervisor roster contains minimal dispatch identities, not emails, sessions or unrelated grants. Technicians get only current assigned briefs; their self calendar excludes private leave explanations.

Separate citizen/staff/technician DTOs and x-role-projections prevent a generic union serializer from choosing a privileged view. Customer timelines use an explicitly separate public update table/DTO. Internal timeline audience is supervisor-only, with filter-bound cursors. Customer alternative acceptance supplies a proposal revision and safe versions; internal work/calendar expectations stay server-side. Reference lookup is authenticated/owned, read-only POST with CSRF/throttling, no business receipt and uniform inaccessible404; a tracking reference is not a bearer credential.

The following remain explicit release blockers: reviewed encryption/key custody, actual consent/disclosure text and its versioning, approved retention/erasure/holds/backup purge policy, operator ownership and actual service commitments. All proposed M07 retention fields are REVIEW_REQUIRED; original pilot numbers are not legal approval. Access changes after a confirmed booking require dispatch review rather than silently sending a technician elsewhere.

## Online-only images and in-app communication

The eleven deferred designs get candidate mutable versions in Feedback, Notification and Attachment DTOs, closing precondition gaps without changing current runtime. Service-linked feedback/rating remains owned and scientifically independent. No automatic GitHub issue or external message is sent.

Images accept JPEG/PNG/WebP only; <=5MiB and <=12 decoded megapixels, exact-size/hash ticket retry, separate original/derivative digests, owner plus current-parent authorization at every stage, and CLEAN derivatives only after the reviewed processing/scanner pipeline. Same-origin binary transport has a route-specific limit; JSON stays <=16KiB. First create the report/service, then upload; null-target draft tickets and SERVICE_TEST/PDF/Office/SVG/HTML are outside initial M07. Completion is202 with actual quarantine/status, never fake CLEAN. Resident media does not expose all images from a shared internal incident/work item. Internal work media stays private until an explicit future publication contract is reviewed.

In-app only; email/SMS/push are const false. Three total delivery attempts include the initial attempt; delay configuration remains unset for owner/operator review. Use the existing planned PostgreSQL jobs/notifications/attempt rows with recipient-event-template-channel uniqueness, lease/replay safety and current-recipient reauthorization. No email provider, offline vault/service worker or scientific job integration is implemented or enabled.

## Proposed page specifications

PAGE-47 `/citizen/{org}/service-requests`: own references, category/status/time filters and authenticated lookup. PAGE-48 `/new`: explicit service review submission with private receipt, no acceptance fiction. PAGE-49 `/{id}`: own public timeline, preferences/access consent, request/confirmation/replacement/cancel states, safe closure and optional feedback. All require loading/empty/denied/expired/stale/offline-error states, persisted receipt evidence, keyboard operation and mobile reflow.

PAGE-50 `/app/{org}/service-requests`: supervisor tenant triage queue with honest as-of counts. PAGE-51 `/{id}`: controlled internal/public timeline, legitimate incident/work linkage and service/appointment decisions. Reuse existing maintenance/work/notifications/admin pages through candidate operation associations; do not add a second dashboard shell. M04's live 46-route classifications and generated TypeScript remain unchanged. New roles/navigation/actions must only activate after actual backend implementation and acceptance.

Keep Option 3 public design, current M02 tokens and structured staff workspaces. Calendar operations need equivalent list controls, explicit timezone, keyboard/focus/status behavior and accessible error recovery. No mockups, invented metrics or fabricated availability are introduced.
