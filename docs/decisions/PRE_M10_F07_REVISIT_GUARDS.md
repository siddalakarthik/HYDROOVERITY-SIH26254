# Pre-M10 F07 incident revisit guards

Scope: a correctness fix authorized by the master pre-M10 completion task. No
measurement ingestion, positive verification outcome, new state edge or API
contract is activated. Full F06/F07 acceptance remains blocked by comparable
operational evidence and the remaining end-to-end revisit acceptance.

## Existing-history cycle boundary

Use the latest immutable incident transition into REOPENED, or from
NOT_VERIFIABLE/DISMISSED into UNDER_REVIEW, as the start of the current cycle.
REOPENED to UNDER_REVIEW does not start another cycle: work already explicitly
ordered during REOPENED remains eligible. Initial NEW triage remains compatible.

An incident cannot enter IN_PROGRESS using completed/cancelled work. On a revisit,
eligible work must either be created after the cycle boundary or carry an
authorized assignment, acceptance or resumption action after that boundary.
This preserves legitimate reuse of unfinished work. An ordinary note alone does
not qualify old work. Existing assignment, role and M07-B scheduling guards still
authorize the underlying mutations.

VERIFICATION_PENDING additionally requires a submitted/completed work order with
a receipt both recorded and performed after the boundary. A newly recorded copy
of an old reported repair is insufficient. Outcome transitions select reviews
only for eligible current-cycle repairs. Re-reviewing an old repair still appends
history but cannot finish the current incident cycle.

## Timestamp tradeoff

The existing schema has no cycle ID or global immutable sequence. This bounded
fix uses database-created timestamps and strict greater-than comparisons, never
UUID ordering or caller-selected event timestamps. Supported mutations share the
organization transaction advisory lock. PostgreSQL transaction start timestamps
can precede a lock wait, and equal timestamps are possible; such ambiguous rows
fail closed rather than become false current-cycle evidence. An explicit later
assignment/resumption or new receipt resolves ambiguity. A future explicit cycle
relation could remove this conservative limitation but needs a separately reviewed
migration and backfill. No historical rows are rewritten.

## Evidence boundary and checks

The focused `services/api/tests/prem10_revisit_acceptance.py` suite covers stale
completed work, old receipts, newly authored reviews of old receipts, legitimate
new work and unfinished-work resumption, backdated receipt exclusion, immutable
history, transition replay and stale versions. Reopened-state fixture injection
is explicitly synthetic lifecycle setup, never a fabricated measured PASSED or
FAILED result. Executed locally on 2026-10-26 against the separate PostgreSQL database `hydro_disposable_prem10_f07`: the initial five focused cases passed (13.97 s); a separate real resumption/cancellation race and unauthorized citizen attempt passed (1 case, 3.25 s); all eleven existing workflow/concurrency cases passed (22.65 s). The first run before applying existing migrations failed at fixture setup; applying the reviewed migration chain resolved that environment prerequisite. No acceptance assertion was weakened. Final integrated CI is still required.

No M03/M05/M08 historical hash is replaced. The integration change should extend
the additive pre-M10 source manifest for `services/incidents.py`; the integration
owner will finalize manifest linkage and mandatory checks on the accepted head.
