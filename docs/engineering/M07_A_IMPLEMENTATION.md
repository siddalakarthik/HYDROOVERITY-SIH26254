# M07-A service foundation

## Authorization and baseline

Owner authorization enables M07-A implementation after PR #17. Direct GitHub verification confirmed owner merge at `c3f785c4fa2974ec45e473786bca4ea8806e2c7a`, incorporating reviewed contracts `5893c5c79831d77fc228d3eae9b814915c071d98`. All four post-merge jobs passed in [run 39789020447](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39789020447). PR #16 is merged and issue #4 completed. The merge tree equals the reviewed contract tree.

## Controlled implementation sequence

1. Add service intake, owned references and separate safe/internal history; test persistence, RLS, authorization, retries and versions against disposable PostgreSQL.
2. Add supervisor triage, resident follow-ups, guarded closure/cancellation and explicit links to already triaged operational work. Never automatically create an incident.
3. Activate the approved optional work `task_purpose` input (omission remains REPAIR), investigation findings and purpose-specific submission. Integrate resident/supervisor/technician flows in the existing M04 shell, then run database, browser and regression acceptance.

The M02 catalogue remains frozen. The M03 matrix retains its original 117-operation/58-implemented/30-table classifications; only positive test references are refreshed from real acceptance runs. A separate M07-A runtime manifest records additive activation. Existing M02 response shapes remain unchanged; work purpose is recorded in the database and selected at creation, and findings are available only for investigation/inspection work. Optional investigation input is the explicitly approved staged delta, not a new unrelated endpoint.

N01–N09, N13, N43 and N44 are the implementation target: twelve additional operations, seventy total including the existing fifty-eight. N10–N12 remain explicitly disabled: the approved preference DTO includes visit access needs, whose privacy/encryption/consent controls have not been independently approved. No access table, plaintext substitute, booking, window, notification or upload implementation is included.

Scheduling/appointments remain M07-B. Images, notifications and feedback remain M07-C. Existing manual NOT_VERIFIABLE and private-development deployment gates remain enforced. No live retention/SLA is approved. The original M07 baseline lock remains an historical hash record; authorized application-source changes are separately classified, while legacy machine contracts and all simulation/hardware evidence remain frozen.

## Implemented controls

The additive `m07_a_001` migration creates five service/history/work-link/findings tables, composite tenant FKs, owned unpredictable 128-bit tracking references, ordered per-case history, immutable append-only records, and RLS with a non-owner runtime principal. Internal history/work links are supervisor-only; resident projections do not expose internal incident/work/roster identifiers. Findings are readable by authorized engineers/supervisors and the current assigned technician. No plaintext visit-access table or substitute exists.

Writes reuse verified session authentication, same-origin CSRF, current membership/permission checks, root/work locks, actor-scoped idempotency, explicit If-Match preconditions and transactional audit/domain-event records. Lookup is authenticated read-only POST with CSRF and a separate throttle; it rejects business idempotency and uses uniform inaccessible404. Cursors bind actor, role, case, filters and public/internal audience. A former assignee cannot read/write or replay findings. No external fan-out job or notification worker is activated.

Resident submission does not create an incident. Supervisor acceptance is an explicit state change. Work linkage checks accepted service, active operational work, matching purpose, current work version and a legitimately triaged incident. Service cancellation requests remain pending until a utility decision. Final closure/cancellation checks all linked work versions and requires linked work to be completed/cancelled first; shared work is not silently cancelled. Appointment dispositions are rejected because no appointments exist in M07-A. VISIT_COMPLETED is deliberately unavailable until M07-B.

Work creation accepts optional task_purpose; omitted purpose remains REPAIR for old clients. Investigation/inspection submissions require a current-assignment findings receipt, not a repair. Repair receipts on investigation work are rejected. Findings corrections append history; they do not overwrite the original. Service closure does not resolve an incident or establish scientific verification. REPAIR_REPORTED requires an actual repair receipt and remains NOT_VERIFIABLE.

## Acceptance and reproduction

Run from the repository root using the existing isolated Python and frontend environments. Database acceptance requires explicitly confirmed disposable PostgreSQL/PostGIS, separate migration/runtime roles and private operator/runtime JSON files outside Git:

```text
python services/api/tools/verify_backend.py --operator-config <private operator.json> --runtime-config <private runtime.json> --confirm-disposable-database <hydro_disposable_name> --evidence-directory <outside-repository evidence>
python services/api/tools/traceability.py --check --evidence <acceptance-summary.json>
python scripts/check_m07a_implementation.py
python scripts/check_m07_design.py
python scripts/check_m02_design.py
python scripts/check_repository.py
python apps/web/tools/contracts.py --check
git diff --check
```

For browser acceptance, prepare the existing private fixture with `apps/web/tools/prepare_browser_fixture.py`, start the private API/Next.js/HTTPS proxy, and run `pnpm run test:browser` from `apps/web`. The runner executes M04 then M07-A and waits one actual login-IP throttle window between suites. It does not weaken the security limits. All fixture credentials/tokens stay outside Git and browser screenshots contain synthetic test records only. Local isolated ports are API8007, Next.js3007 and HTTPS9443; default CI reproduction remains8000/3000/8443. HTTP frontend-only preview does not provide authenticated API routing on the isolated ports.

Executed local evidence includes real PostgreSQL intake, triage, role/tenant/ownership denials, CSRF, stale versions, owned reference lookup, signed cursor isolation, duplicate complaint conversion, concurrent retries, competing versions, current-assignment findings, no fake repairs, empty upgrade/downgrade round trip and refusal to remove populated history. The original backend regression suite is included. Browser evidence covers resident intake, safe/private timelines, supervisor review/linkage, investigation findings, mobile ownership/stale errors, offline recovery and cancellation pending. Automated accessibility checks target WCAG2A/AA,2.1AA and2.2AA; this is bounded tested-page evidence, not a universal accessibility certification.

Executed local totals:56 PostgreSQL tests passed twice with zero failures/errors/skips and identical backend source digests; all twelve new operation responses and all58 baseline operations had actual positive conformance evidence. All37 traceability adversarial tests,17 frontend unit tests, TypeScript/lint/format, production build, both M04 and both M07-A browser suites, M02/M07 checks and independent OpenAPI checks passed. M05's38 unit tests and smoke profile passed, with outputs kept outside this repository; M08 source checks and13 focused tests passed. A Windows temporary-directory permission failure was resolved by selecting the existing task-owned temporary directory; no simulation source/parameter was changed. Browser testing demonstrated and corrected mobile reference overflow and selection-state reset. Independent synthetic service actors prevent M04's deliberate role-revocation tests from contaminating M07-A acceptance.

The current source SHA, CI link and artifact existence are recorded in the review PR after actual execution. The CI retains all four jobs including M02/M05/M08 regressions. The separate `HYDROOVERITY_M07A_BROWSER_EVIDENCE` artifact is uploaded only after successful browser validation and retained14days. Seven M07-A screenshots are stored locally outside the checkout and uploaded from synthetic fixtures; no real resident data or raw scientific evaluation truth enters the artifact.

## Remaining boundaries

This is private-development, code-tested service management. There are no physical trials, hardware/field performance claims, scientific integration, bookings, technician shift policy, notifications, media processing, access encryption or live release approvals. Investigation-only closure supplies an honest operational reason, never a measured verification. Existing M04 dependency/license limitations remain unchanged; no packages or paid services were added. Native CAD physical fit and KiCad ERC limitations remain unchanged. Owner engineering review is required before merge or a subsequent increment.
