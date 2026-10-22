# M07 contract reconciliation engineering report

**CONTRACT REVIEW ONLY — no operational implementation, migrations or public release.**

## Verified M04 closure gate

Direct GitHub inspection confirmed PR #16 merged by `siddalakarthik` on 22 October 2026 at 05:26:45 UTC. Exact merge/main commit: `fe69ccdb10ab515f73bbceaaa4652ce440859c85`. Parents are pre-M04 main `e0122f5ee4146e49ae6113a1aa6a5ee444b25973` and reviewed M04 head `196a5902e8be77a8017c1a97e9abad671345b2c9`. The merge tree is exactly equal to the reviewed head. `git fsck --connectivity-only --no-dangling` passed and the M04 worktree was clean.

[Main run 39728063698](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39728063698) completed successfully on that exact merge commit: repository-integrity, m03-backend, m08-cad-and-figures and m04-frontend all passed. Issue #4 is CLOSED with state_reason `completed` (05:29:32 UTC). The first observation saw frontend CI still running; no M07 modification began until a later direct read confirmed all four passed.

No services/api, simulations or hardware source changed between pre-M04 main and the M04 merge. M04 implementation, dependency lock, third-party notices and documented development-only HIGH braces advisory/license obligations are preserved. This report does not claim that the advisory is fixed or that a new security audit was performed.

An isolated `feature/m07-contract-reconciliation` worktree/branch starts at that verified main commit. No M04 branch edit, merge, issue closure or deployment is performed by this task.

## Proposed contract package

Start at the [candidate architecture/index](../architecture/m07/README.md), [OpenAPI](../architecture/m07/openapi-proposed.json), [reconciliation matrix](../../data/schemas/m07-reconciliation-matrix.json), [database model](../../data/schemas/m07-database-design.json), [states/policy gates](../../data/schemas/m07-state-machines.json) and [routes](../../design/ui-ux/m07-route-catalog.json). Preserved owner-reviewed planning sources and D1–D10 are included, with hashes and historical gate observations explicitly distinguished from this report.

Counts are exact: baseline 117 operations/57 designed tables/46 routes; candidate 161 operations/74 designed tables/51 proposed routes. Current runtime remains **58 operations, 30 migrated tables and unchanged M04 route availability**. Candidate classification is 58 unchanged implemented operations +44 new proposals +11 selected deferred designs +48 remaining outside M07. No proposed operation is claimed implemented.

Seventeen new designed tables are added. Five baseline designed tables have explicit candidate column deltas. The proposal's optional outbox checkpoint table is dropped in favor of existing background_jobs with one event dedup reference; this is a documented choice between alternatives, not two queues. M07-A owns15 new operations, M07-B26, M07-C3 plus eleven deferred designs.

## Compatibility and discrepancies resolved

1. **Runtime catalogue coupling:** M03 imports M02 JSON and selects implemented domains dynamically. Replacing it in place would change runtime validation/registration and M03's strict117-operation traceability. Therefore all deployed JSON/TypeScript/source remains frozen; the M07 canonical candidate is composed separately and not imported. Independent hashes pin171 baseline files, all58 operation definitions and every existing schema. Existing M03 implementation matrix and M04 generated contracts stay unchanged.
2. **Investigation versus repair:** existing M03 requires repair receipts for every submission despite M02's investigation-only intent. Candidate purpose/findings model resolves the design; `M07FutureWorkOrderWrite` is explicitly staged, with old clients' omitted purpose remaining REPAIR in the future implementation. No runtime behavior changes now. Activation, future DTO enrichment and guarded submission need a subsequent reviewed implementation.
3. **Parent/version usability:** named If-Match targets and child/calendar/policy versions are explicit. Feedback/Notification/Attachment candidate reads include mutable versions. Absent visit-access row does not fabricate a child version; first write uses service If-Match plus expected_access_version=null.
4. **Tracking and safe history:** reference is a random128-bit identifier, not a bearer grant. Lookup POST avoids URL/log reference disclosure and rejects business idempotency. Public/internal timelines have distinct DTOs and cursor audience; role-specific nested booking receipts cannot accidentally serialize internal work/roster context.
5. **Bootstrapping and cancellation:** D5 guards capacity promises only. Policy/roster/shift configuration, reads, withdrawal and cancellation remain usable while booking is disabled. Own-window lists expose a safe UNCONFIGURED/DISABLED reason and zero windows, not invented availability. Alternatives and preferences never hold capacity.
6. **Atomic scheduling:** allocation exclusion, exclusive tenant enrollment, active-check-in uniqueness, sorted lock ordering and legacy endpoint guards are specified. Rescheduling cannot cancel first over a separate HTTP call. Overrun/leave/revocation cannot be hidden to make a calendar appear conflict-free. These are constraints to implement/test later, not executed booking evidence.
7. **Online-only image scope:** initial null-target drafts and SERVICE_TEST/PDF/document formats are excluded. Six planned attachment operations have image-only candidate schemas and route-specific binary limits; complete returns202 while quarantined. No body-limit relaxation or scanner is installed. Feedback and notification paths stay deferred.
8. **D8–D10:** only in-app; external channels const false; three total attempts with delay values unconfigured; offline false; no customer SLA or approved live retention period. Encryption/key custody, consent/disclosure, retention/erasure/holds and storage/scanner/license gates remain outstanding.

Future compatibility risks are not hidden: adding fields to current strict response schemas or applying new scheduler guards to existing assignment endpoints requires coordinated backend/frontend tests and activation approval. This PR avoids that risk by leaving existing58 wire definitions, runtime behavior and generated M04 types unchanged. Legacy due_at remains a deadline, not a booking.

## Validation and limits

Reproduction from repository root, Python3.12+; independent validators use the existing isolated pinned requirements, not application dependencies:

```text
python scripts/build_m07_contracts.py --check
python scripts/check_m07_design.py
python scripts/test_m07_design_checker.py -v
python scripts/check_m02_design.py
python scripts/test_m02_design_checker.py -v
python scripts/check_repository.py
python apps/web/tools/contracts.py --check
python scripts/validate_openapi_design.py
python scripts/validate_m07_openapi.py
git diff --check
```

`validate_*` commands require the isolated environment from `scripts/openapi-validation-requirements.txt`. M03/M04 contract checks use the existing isolated M03 environment. CI adds the new design checks to repository-integrity and retains backend, CAD/figures and frontend jobs.

Executed local evidence: M02 consistency passed57/117/46 and all33 deliberate invalid-design mutations. M04 implemented-only contract/route check passed. M07 consistency and all34 deliberate invalid-design mutations passed. Independent M07 OpenAPI3.1 and273 component metaschemas passed, with19 positive/negative synthetic schema examples. Independent baseline OpenAPI/154 metaschemas passed. Repository integrity passed300 files/224 local links, frozen-file checks passed171 files and git whitespace passed. Validators: openapi-spec-validator0.9.0, openapi-schema-validator0.9.0, jsonschema4.26.0, referencing0.37.0. Actual PR CI results are recorded on the review PR after execution; this text does not preclaim their result.

These tests establish schema/design consistency and frozen compatibility. They do not execute new M07 transactions, concurrency, row security, scanners, notifications, customer journeys or physical tests. M05 source/results and M08 source/caveats remain unchanged. Future operational tests must implement the accepted plan's real PostgreSQL races, cross-tenant/ownership denials, scanner failure corpus and browser workflows; mock-only acceptance is insufficient.

## Outstanding approvals before operational development/release

- Owner approval of the composed contract package, staged task-purpose delta and canonical activation strategy; no additive migration/backend/frontend implementation yet.
- Actual authorized roster/skills/areas/shifts/durations/buffers/caps/lead times/cancellation/expiry policy; until then scheduling remains disabled.
- Reviewed encryption algorithm/implementation/key custody and rotation, minimum visit-access disclosure/consent, privacy notice version binding, erasure/holds/audited redaction, backup/purge and operator responsibilities. No proposal TTL is an approved legal policy.
- FOSS image scanner/decoder versions, licenses, isolated processing/resource limits and private storage configuration; no images enabled until reviewed. PDFs/documents remain deferred, not a pending automatic format expansion.
- In-app job attempt-delay configuration with exactly three total attempts, job lease/recovery and retention policy; no external channel enablement.
- Owner authorization for the next M07-A implementation slice only after this contract review. M06, scientific results, video/M10, public release and automatic M07 merging/issue closure remain outside scope.

Stop after publication of this review package. PR description is the current-head CI/status authority; historical planning documents and this execution record must not be read as permission to start migrations or as a substitute for actual test results.
