# HYDROOVERITY — M07 owner architecture review decision

**Decision: CONDITIONAL ARCHITECTURE APPROVAL.**

This records the owner's review of the [engineering plan](M07_SERVICE_MANAGEMENT_ENGINEERING_PLAN.md) and [proposed API/schema catalogue](M07_API_AND_SCHEMA_PROPOSAL.md). It supersedes unapproved alternatives and pilot-policy suggestions in those proposal documents. It does not authorize application implementation, migrations, public release, merging or issue closure.

## Adopted decisions

| Decision | Controlling owner instruction |
| --- | --- |
| D1 | Use M04 only after owner approval of PR #16, merge and successful main-branch CI. The agent must not merge PR #16 or change it for M07. |
| D2 | Initial categories are VISIBLE_LEAK, LOW_PRESSURE and SERVICE_INTERRUPTION. Dispatch requires a legitimately triaged incident. No incident is invented merely to satisfy a foreign key. |
| D3 | Investigation-purpose work and findings receipts are approved; do not create fake repair records. |
| D4 | Initial technician scheduling enrollment is exclusive to one utility per global user. No shared cross-utility calendar broker is included. |
| D5 | Scheduling stays disabled until actual authorized shifts, skills, service areas, durations, buffers and policies are configured. No operating hours, capacity or availability defaults are invented. |
| D6 | Visit-access information is minimal and separately consented. Encryption, retention and disclosure design require review. |
| D7 | Secure images require prior scanner, processing, licensing and storage-control review. PDF and arbitrary documents are deferred. |
| D8 | In-app notifications only initially; three total delivery attempts. External email, SMS and push remain disabled. |
| D9 | Online-only initial operation. Offline drafts, leases/vaults and synchronization are deferred. |
| D10 | No invented SLA. Proposed retention numbers are not approved legal policy. Retention, privacy consent, erasure/holds and operator commitments require explicit review before live release. |

The existing M02 contracts, M03 implementation, M04 frontend, M05 scientific models and M08 digital hardware evidence remain authoritative. HYDRO-WATCH, GUARD-5, HYDRO-EAR and HYDRO-VERIFY are unchanged. The current manual-only NOT_VERIFIABLE gate is preserved. Service completion, attendance, images and satisfaction scores do not establish scientific repair verification.

## Authorized next change and its prerequisite

After D1 is satisfied, prepare a **contract-only M07 engineering change**. Reconcile the M02 API, database, permissions and route specifications with the 44 proposed new operations and 11 previously designed/deferred operations. Preserve compatibility of all 58 implemented M03 operations. Validate canonical contracts and design checkers, then report exact changes, discrepancies and remaining blockers for owner approval.

Do not start additive migrations or operational backend implementation before that further review. Do not modify PR #16, start M06/M10, change scientific evidence, deploy publicly, merge M07 or close milestone issues without separate authorization.

### Development priority and proposed operation ownership

The operation allocation below organizes the existing proposal, rather than introducing or activating contracts. Contract review may refine it with an explicit discrepancy report.

| Increment | Scope | Existing proposal IDs |
| --- | --- | --- |
| M07-A — service foundation | Own service submissions/reference/timeline/follow-ups, explicit utility acceptance/closure, minimal access/preferences design, incident/work linkage and investigation findings | N01–N13 and N43–N44: 15 proposed new operations |
| M07-B — scheduling/dispatch | Published windows, request/confirm/alternative/reschedule/cancel, assigned visits, exclusive roster/calendar, shifts/blocks, transactional allocation, workload and policy | N14–N39: 26 proposed new operations; disabled until D5 prerequisites are met |
| M07-C — communications/evidence/feedback | In-app preferences and safe delivery audit; M02 notifications, image lifecycle and service-linked feedback | N40–N42: three proposed new operations, plus 11 M02-designed deferred operations; image enablement subject to D7 |

The 44+11 counts describe the proposal to reconcile, not implemented operations. PDF/document and offline expansions must be removed from initial enabled scope. Service preference/time inputs can be documented in M07-A without claiming that booking exists before M07-B. Notification retry limit is three total attempts; exact delay configuration still needs an explicit documented policy and does not add a fourth attempt.

## Verified D1 gate state at this review checkpoint

Read-only GitHub metadata returned:

- [PR #16](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/pull/16): OPEN, `merged=false`, no recorded GitHub review entries.
- PR head: `196a5902e8be77a8017c1a97e9abad671345b2c9`.
- Main: `e0122f5ee4146e49ae6113a1aa6a5ee444b25973`, which does not contain the M04 merge.
- [Main run 39588590017](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39588590017): successful for that pre-M04 main commit. It is not proof of M04 passing after merge.

GitHub's `merge_commit_sha` for an open PR can identify a test merge; it is not evidence that the PR merged. D1 must be checked using actual merge state and the resulting main commit/CI. Existing successful PR CI does not replace this owner-required post-merge gate.

**Result: contract reconciliation has not started because D1 is unsatisfied.** The next continuation must re-read PR merge status, owner-approval evidence and CI jobs on the actual M04-containing main commit before any contract branch/change. If those conditions are still unmet, preserve this gate; do not merge M04 or substitute another baseline automatically.

## Checkpoint integrity

Only this decision record and a short link from the separate planning package are added. No Git branch, canonical contract, application file, migration, PR or milestone issue is changed. The proposal documents remain historical design material, with this owner decision taking precedence. Document links and operation-phase counts are checked; no M07 implementation or test-pass claim is made.
