# M06 scientific integration review

Baseline: `1da657d59bccdb6b66fb7dd66cb9f8310c3e7931` (merged PR #18).
All four post-merge jobs passed in run 39995544866 before implementation.

## Runtime scope and compatibility

The existing engineer workspace adds the scenario lab and recording details on
`/app/{org}/simulations` and `/app/{org}/simulations/{id}`. It imports verified
M05 observations into PostgreSQL and exposes charts, qualification, missing-data
gaps, an evidence waterfall, provenance, historical comparisons and replay/export.
The modeled repair cases include M05's independent WATCH, GUARD-5 and EAR outputs,
with the uncoupled-model limitation visible.

**77 operations = 58 M03 + 12 M07-A + seven M06. 36 migrated tables = 35 + one.**
Historical M02/M07 catalogues remain unchanged: 161 designed operations / 74 tables;
the explicit M06 overlay brings combined design totals to 168 / 75. The historical
M03 implementation matrix continues to describe its original 58 operations.
Only its positive-response test references are refreshed from actual acceptance;
classifications and contract metadata are checked against the baseline.

All seven endpoints share `/api/v1/orgs/{organization_id}/scientific-replays`:

| Method | Suffix | Behavior |
|---|---|---|
| GET | `/catalogue` | 69 supported scenario descriptions |
| POST | (none) | Atomic selected-scenario import with UUID Idempotency-Key |
| GET | (none) | Tenant history, offset/limit pagination |
| GET | `/{run_id}` | Observation-only scientific detail |
| GET | `/{run_id}/frames` | Deterministic bounded replay |
| GET | `/{run_id}/events` | Bounded SSE provenance, observations, checkpoint |
| GET | `/{run_id}/export` | Authorized JSON snapshot with provenance |

All require a current ENGINEER membership and explicit simulations.read/write
permission; ADMIN does not imply ENGINEER. Import also requires CSRF and a UUID
idempotency key. Keys are scoped to tenant and membership, serialized by transaction
lock, and reauthorized on retry. Different content returns 409. Immutable records
have no mutable transitions and therefore no If-Match update contract.
Every replay page and SSE batch rechecks access. SSE resumes using next_offset;
it is a bounded recorded feed. The UI uses JSON pages and browser acceptance also
consumes SSE. RLS is forced, with tenant/current-role checks and creator ownership
on insert. Composite foreign keys, immutable history, atomic audit and SIMULATION
domain events apply. No operational incident, work order, repair or verification
record is created. Empty downgrade is allowed; populated downgrade is rejected.

## Scientific boundary

`data/samples/m06` contains 69 pinned observation-only recordings: 12 hydraulic,
12 acoustic, 42 collar cases across three regimes and three modeled repair outcomes.
These reproduce repeat-zero M05 observations, not a newly randomized benchmark.
Published PPT aggregates retain their original denominators and unfavorable results:
190/264 acoustic results accepted, 74 unresolved and **20 accepted wrong intervals**;
nominal GUARD-5 F1 **0.714**, pad **0.778**, multizone **0.824**.

The offline producer has no API credentials. It exports explicit observations and
detector results, discarding generator truth. Seeds, private evaluator rows, exact
hidden acoustic source positions, unapproved geometry and filesystem paths are
excluded. The API image excludes generators, the producer and evaluator files.
The full catalogue, individual cases and historical aggregate content are pinned;
unknown fields are rejected. Operator overrides cannot authorize changed datasets.
Setting science_catalogue_path to null disables import with an explicit 503.

All five collar health values remain UNKNOWN. Missing measurements remain gaps.
Acoustic waveform previews are subsampled; inference uses full recordings. Only
qualified candidate intervals are shown, without exact crack claims. Modeled
PASSED/FAILED/NOT_VERIFIABLE are distinct from operational verification. Imported-at
is not evidence freshness. Simulation provenance survives navigation, replay and export.

## Reproduction and acceptance

From the repository root using the existing isolated scientific environment:

```text
python -m simulations.integration.produce --output <private-work-directory>/m06-catalogue.json
python -m pytest tests/unit/test_m06_reproduction.py -q
```

The reproduction test compares all 69 recordings with absolute/relative tolerance
1e-8, retaining exact categorical results and aggregate content. The producer
checks three modeled verification outcomes and residual values against M05 at
1e-9 tolerance. Byte hashes identify the stored export; tolerance accommodates
platform roundoff during independent regeneration. No M05 model/configuration changes.

With the isolated API environment and explicitly confirmed disposable PostgreSQL
database, use the existing backend acceptance runner and these focused commands:

```text
python -m alembic -c services/api/alembic.ini upgrade head
python -m pytest services/api/tests/test_science.py -q
python scripts/check_m06.py
python scripts/check_m07a_implementation.py
python apps/web/tools/contracts.py --check
```

The full backend runner requires positive mappings for all 58 legacy, 12 service
and seven scientific operations. Tests cover concurrent idempotency, current role
revocation, RLS/tenant denial, CSRF, immutable history, rollback protection, missing
catalogue, truth injection and unfavorable outcomes. Browser acceptance covers
import/replay/export, all modules, all verification outcomes, denial, mobile 390px
layout and axe WCAG checks. Unit tests check missing samples are not interpolated.
Existing M04/M07-A browser workflows and M02/M05/M08 checks remain in CI.

All four mandatory jobs are retained. CI adds numerical reproduction, scientific
backend checks and a separate sanitized M06 PNG artifact with 14-day retention.
Final execution results and exact review SHA are recorded in the pull request.

## Limitations and owner review

Imports synchronously persist verified recordings. They do not claim freshly
executed queued jobs; canonical M02 worker/lease ingestion and evaluator endpoints
remain deferred under distinct routes. There is no arbitrary-code interface.
History lists use offset pagination and concurrent imports can shift pages;
immutable replay frame offsets remain stable. No retention/deletion UI is enabled.
Public release, physical validation, visit access, scheduling, media and all D1–D10
privacy/deployment gates remain unchanged. Dependency/license limitations remain.
This package is for owner review; do not merge or close issue #6 automatically.
