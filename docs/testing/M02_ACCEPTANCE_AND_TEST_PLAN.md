# M02 acceptance and test plan

All product cases below are **future acceptance cases, not executed tests**. M02 executes only documentation/contract consistency, link, whitespace and repository checks. Reference SIH/ENG requirements in SYSTEM_REQUIREMENTS.md; issue #2 is milestone traceability. The route/API catalogs connect user objective to authorized action and schema; database design gives persistent entities; these cases prove the behavior in later milestones.

| ID | Implementation milestone | Workflow | Given / when | Required result |
| --- | --- | --- | --- | --- |
| F01 | M03/M07 | Citizen creates report | Verified citizen of enabled utility submits valid complaint twice with same key | One complaint/tracking number and public receipt, one notification; different body same key409 |
| F02 | M03/M07 | Citizen ownership | Citizen B requests A report ID/list/followups/photo | Uniform404 and no row/content disclosure |
| F03 | M03/M07 | Triage | Supervisor moves NEW concern through reviewed acceptance | Guarded versioned transition, immutable event/audit and same-mode evidence links |
| F04 | M03/M07 | Assignment | Supervisor assigns active technician then reassigns while worker offline | Assignment version increments; old worker sync denied without discarding local draft |
| F05 | M07 | Worker repair | Assigned technician records notes/materials/photos/repair and submits | Persistent immutable receipts and review state; no scientific PASSED invented |
| F06 | M07 | Verification | Supervisor reviews comparable versus missing-calibration before/after sets | PASSED/FAILED only comparable; otherwise NOT_VERIFIABLE; work completion independent |
| F07 | M07 | Reopen | Resolved incident recurs with new evidence | New reopen event; prior repairs/evidence preserved |
| S01 | M03 | No authentication | Anonymous calls internal API/stream/download | 401, no private data or hidden side effects |
| S02 | M03/M09 | Tenant isolation | Tenant A engineer references B IDs through API/FK/pool reuse | Uniform denial; composite FK and RLS deny cross-tenant reads/writes; context reset |
| S03 | M03 | CSRF/session | Missing/wrong token, cross-origin mutation, expired/revoked session | 403/401; login rotates; reset revokes sessions; no cookie/token in logs |
| S04 | M03/M09 | Role/resource checks | Worker guesses unassigned work; ADMIN requests raw telemetry/truth | Deny; no ADMIN wildcard or evaluator self-grant |
| S05 | M03/M07 | Uploads | Oversize/type spoof/polyglot/decompression/missing-consent/quarantined download | Reject413/422 or quarantine; no original/EXIF/public object exposure |
| S06 | M03 | Audit | Sensitive role/retention/device-key action succeeds or denied | Safe actor/action/resource/time/request evidence; no credentials or private bodies |
| P01 | M05/M06 | Truth exclusion | Inspect detector input, API schemas, ordinary outputs/streams/exports | No actual labels/positions/private truth seed; ordinary DB/object roles denied |
| P02 | M06 | Origin integrity | Simulator sends hardware/environment fields or different tenant/run | Reject; server-derived SIMULATION survives queries and export |
| P03 | M06 | Lab versus field | Ingest authorized lab and field adapters plus manual note | Distinct immutable acquisition environments; no source relabeling by UI |
| P04 | M05/M06 | Acoustic abstention | Zero pressure/weak signal/ambiguous path cases | No fake pinpoint; reasons and empty candidate list for abstention |
| P05 | M05/M06 | Guard wetness | EXT-first/bypass-only/disconnected-supervision-unsupported scenario | Competing explanations; no automatic joint-confirmed state; unsupported health UNKNOWN |
| P06 | M06 | Staleness | Late/out-of-order/invalid observations arrive during filling | Retain quality/freshness; no routine false attribution; urgent/fault lane retained |
| R01 | M03/M06 | Idempotency | Duplicate events/keys and changed payload collision | One stable receipt; conflicts reject atomically, no duplicated incident side effects |
| R02 | M06 | Realtime recovery | Drop SSE between snapshot and subscription; replay cursor expires | Watermark/replay or reset snapshot; no lost authorized event; bounded queue; no waveform |
| R03 | M04/M07 | Offline vault | Lost connectivity, quota eviction, expired lease, logout, wrong unlock | Clear safe error/expiry/purge behavior; no plaintext cached keys/data or false synced badge |
| R04 | M07 | Offline conflict | Replay note after role removal/task reassignment/stale version | Current authorization and versions checked; conflict preserved for reconciliation, not last-write-wins |
| R05 | M06/M07 | Jobs and delivery | Worker crash/lease expiry/cancel race/provider timeout | Bounded retries; partial outputs incomplete; notification deduplication/failed status visible |
| U01 | M04/M09 | Responsive UI | 320px Android-like width, desktop and zoom200/400% | Readable labeled data, usable task controls, no obscured focus; map/table alternative |
| U02 | M04/M09 | Accessible forms | Keyboard/screen reader login/complaint/errors/dialogs | Labels, error summary, focus restore and no drag/color-only action; password paste allowed |
| U03 | M04/M06 | Mode/freshness | Navigate/filter/export synthetic records and disconnect feed | Persistent SIMULATED DATA and timestamps; no synthetic field-performance savings |
| U04 | M04 | States | Exercise loading, no permitted records, permission/error/offline forms | Useful distinct states; every visible mutation tied to actual API receipt |

## Implementation evidence contract

M03 uses pytest/API/database tests for transactions, membership/FK/RLS, auth/CSRF/idempotency and DTO exclusions. M04 uses component/Playwright checks for routes, access-denied/empty/error/mobile/keyboard modes; no mock success presented as production persistence. M05 numerical experiments require independent tuning/holdout seeds, honest denominators/coverage and all failures. M06 integration verifies synthetic ingestion, job completion/replay and truth isolation. M07 E2E proves citizen -> triage -> assignment -> offline worker -> repair -> comparable review -> public-safe update. M09 combines security, performance, accessibility and provenance audit. Actual test output must identify commit/environment/commands, not just a checklist.

Cross-document review gates: every OpenAPI local ref resolves, operation IDs unique, path params declared, requests/responses typed, mutations carry CSRF/idempotency policies, protected routes list roles/scopes, tenant FKs reference same-tenant identity, state enums match contracts, and every route has loading/empty/error/offline/mobile/acceptance specification. A standard-library design checker is a limited structural check, not full OpenAPI conformance, SQL execution, Mermaid rendering or a security test. Missing full parser tools must be disclosed; do not install large stacks just to claim planning validation.

M02 may open a PR only after review and available checks; **do not merge, close issue #2 or close milestone M02** without separate owner approval. M03 begins only after that review/authorization. Physical/scientific claims remain unestablished.
