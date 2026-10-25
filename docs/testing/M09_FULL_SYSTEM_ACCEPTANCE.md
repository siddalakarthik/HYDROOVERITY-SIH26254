# M09 full-system acceptance review

## Decision and source boundary

This is executed **private-development software evidence**, not public-release,
hardware, field, electrical or accessibility certification. No new runtime
operation, migration, dependency, scientific parameter or physical claim is added.
All 277 accepted text-source pins and the complete implemented OpenAPI remain
unchanged; [baseline manifest](../../data/schemas/m09-acceptance-baseline.json)
and [checker](../../scripts/check_m09.py) enforce this.

Accepted main: `500a349299ceb79994d618cc0208dca9b2fb6ed0` (PR #21).
PRs #11–#21 were independently confirmed merged; no implementation PR was open.
[Main push run 40170280662](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40170280662)
completed successfully with repository-integrity, m03-backend, m04-frontend and
m08-cad-and-figures before M09 changes. Local clean main was fast-forwarded
41 commits, then an isolated `feature/m09-full-system-acceptance` worktree created.
Existing feature worktrees/private configurations were preserved.

Actual runtime: **111 operations / 51 application tables**, revision `m07_c_001`.
Operations: 58 M03 + 12 M07-A + 7 M06 + 26 M07-B + 8 M07-C. The composed
168-operation/75-table design is a separate catalogue, not implemented scope.
The test runtime remains a non-owner, non-superuser, non-BYPASSRLS principal.

Local evidence was executed from accepted main plus the new acceptance source;
each M09 summary records its test/tool digests. The final review commit and
exact-head CI results are recorded in the PR, avoiding a self-referential commit
hash in this file. Owner acceptance requires **all four final CI jobs green**.

## Environment and executed procedures

Windows 11 build 26300, Python 3.12.14, Node 24.21.0, Chrome 155.0.8059.85,
PostgreSQL 17.11 / PostGIS 3.6.2; 16 logical CPUs. Existing pinned Python and
frontend environments were reused. [Environment manifest](m09-environment.json)
records dependency and nonsecret fixture hashes. CI uses its existing Ubuntu,
PostGIS image and Playwright Chromium, and records browser/runtime versions.

Only `hydro_disposable_m09`, `hydro_disposable_m09_browser` and
`hydro_disposable_m09_demo` were initialized locally. The existing PostgreSQL
server was stopped at entry and started without resetting any other database.
The outage probe refuses connections only to its exact, marked disposable
database and restores it in `finally`; it never stops the shared PostgreSQL
server. Child processes are scoped to their own PIDs. Runtime credentials,
tokens, private mail, certificates, raw logs and screenshots remain outside Git.

Local evidence directories (relative to the task workspace, **not this checkout**):

- `work/m09-baseline` and `work/m09-baseline-repeat`: independent legacy runs.
- `work/m09-independent-reviewed`: explicit M09 scenarios and source digests.
- `work/m09-https-demo`: genuine HTTPS manual-repair/independent-review workflow.
- `work/m09-https-probe`: verified HTTPS timing and real outage/restart evidence.
- `work/m09-browser-evidence`: genuine synthetic screenshots and browser timings.

| Executed group | Result | Scope |
|---|---|---|
| Existing PostgreSQL acceptance | 84 passed per run | Auth, governance, RLS, FK, state/receipt/migration/security, M06 and M07-A/B/C |
| Independent M09 PostgreSQL suite | 12 passed | Integrated chain, live inventory, all69 safe exports/frames, scheduling races, worker processes and hostile DTOs |
| Scientific numerical/reproduction | 39 passed | Existing 38 M05 tests plus all69 M06 reproduction test |
| M08 source consistency | 13 passed | BOM, channels, interfaces, geometry/source/package checks; final CI regenerates CAD/figures |
| Existing real browser scenarios | 7 passed | M04 account/operations, service foundation, science, dispatch, communications |
| New M09 browser scenarios | 2 passed | 16 reduced-motion public views, keyboard/reflow, persisted hostile-text escaping |
| Frontend unit/component tests | 19 passed locally | Typecheck, zero-warning lint, formatting and production build passed; final CI retained |
| Traceability regression | 37 required with two independent evidence files | Historical coverage/contract drift detector; final CI remains mandatory |
| Real HTTPS recovery and measurement | passed | 60 reads, API process stop/restart, actual disposable DB connection outage |

The command inventory below and CI provide reproducibility; test counts are not
a percentage of all original planned capabilities.

## Business and transactional findings

The new integrated scenario runs one persisted chain: authenticated resident,
explicit supervisor acceptance, independently triaged incident, investigation
work/link/eligibility review, authorized synthetic shift/policy/window, visit
request/confirmation, manual check-in/finish, technician findings, submitted work,
supervisor completion, safe service closure, notification delivery/read, resident
rating and supervisor feedback review. The visit does not complete work; work and
feedback never create a repair or successful verification. Investigation closes
with **NOT_APPLICABLE**, not manufactured repair evidence. A separate actual
HTTPS manual repair workflow retains independent **NOT_VERIFIABLE** across a real
API restart; unsupported PASSED/FAILED operational assertions are rejected.

Competing residents/supervisors obtain exactly one booking/allocation. Additional
races cover original cancellation versus replacement confirmation, window
withdrawal, two current sessions accepting a stale alternative, and legacy
assignment versus rescheduling. Tests assert the durable winner and allocation
count, rather than merely observing an exception. Existing tests also cover
exclusive cross-utility enrollment, PostgreSQL exclusion, replacement rollback,
role loss, unsafe shift withdrawal and ledger bypass. An overrun remains a manual
event and preserves the future allocation. Interleavings are bounded examples,
not exhaustive concurrency verification or production-scale load.

Persisted worker tests distinguish queued events, delivered inbox records and
explicit human read commands. Actual OS worker processes restart between queued
events; an expired lease without reviewed retry policy fails honestly. Existing
tests exercise competing claims, duplicate events, current roles/parents,
reassignment, quiet hours/preferences, stale versions and exactly **three total
attempts** under an explicitly synthetic retry policy. No external delivery or
default operational retry delay is enabled.

## Security and data isolation

Executed tests cover anonymous/expired/revoked sessions; reset races and token
replay; invitation identity/grant restrictions; CSRF/Origin; cookie rotation;
throttling; current role and assignment; same/cross-tenant foreign IDs; resident
ownership; receipt authorization; RLS and transaction-local pool context;
parameterized filters, immutable history, safe errors/logs and private DTO fields.
Assertions inspect response content and database effects as well as status.
The all69-recording boundary test imports approved snapshots through three
explicitly authorized synthetic engineers to respect unchanged member/IP limits.
Exports equal the pinned safe snapshots; frame pages contain no forbidden truth,
seed, hidden position, evaluator label or private artifact path. Existing tests
also check SSE, source spoofing, invalid/poisoned catalogues, tenant and role loss.
The browser stores hostile HTML/script-like text as inert text, including after
reload at 320px. No dialog or injected element executes.

Uploads/downloads and public contact submission are not implemented. Simulation
export is safe JSON, not a spreadsheet export; CSV export-injection certification
is inapplicable. A sealed evaluator/object-store ACL subsystem is not implemented.
No independent third-party penetration test was performed. The accepted M04 HIGH
development-only `braces` advisory and dependency/license limitations (including
Sharp LGPL notices and undecided project license) remain disclosed; dependencies
were not changed and no clean all-dependency-audit claim is made.

## Scientific review

All 69 pinned M06 observations reproduce at the existing absolute/relative
`1e-8` tolerance; modeled verification residual tolerance remains `1e-9`.
The catalogue/config/source digests are unchanged. These cover 12 hydraulic,
12 acoustic, 42 GUARD-5 observations and three modeled repair outcomes.
HYDRO-WATCH supply-state/water-balance qualification, gaps/faults and demand/leak
ambiguity remain modeled. HYDRO-EAR uses one modeled common clock, eligible spans,
uncertainty and abstention; it does not establish passive leak audibility or exact
physical crack location. GUARD-5 retains exactly A/B/C/EXT/BYPASS and five UNKNOWN
electrical-health states without supervision evidence. No field adapter or
operational positive sensor verification was invented.

Historical M05 PPT benchmark remains visible: **190/264 eligible acoustic captures
accepted; 74 unresolved; 20 accepted intervals exclude truth**. The nominal
GUARD-5 F1 **0.714** remains below pad **0.778** and multizone **0.824**. These are
unchanged historical synthetic results, not newly executed field experiments or
superiority claims. Full frozen PPT benchmark regeneration was not repeated;
numerical/reproduction tests and source pins were independently reexecuted.
Evaluation truth and seeds remain outside ordinary dashboard/public artifacts.

## Measured performance and browser review

Private loopback production build, five warm-up reads, three repetitions of
20 authenticated service-list reads, concurrency four: **60 samples, zero HTTP
errors, 3.123s total, 19.21 requests/s, p50 67.56ms, p95 170.25ms**. Body size was
2011 bytes. P99 is deliberately unreported: 60 observations do not support a
stable tail estimate. At the later database snapshot: two connections and zero
waiting locks. This does not measure peak lock demand or identify SQL slow-query
plans. Two real worker deliveries plus four process launches/idle/lease recovery
took 5.46s; this is not steady-state worker throughput.

Sixteen sequential public navigations across 1440/768/640/320px had TTFB
7.6–33.4ms and DOMContentLoaded 31.1–194.9ms. One earlier cold home sample was
231.5ms TTFB / 425.1ms load, eight JavaScript requests / 490201 encoded bytes.
This small mixed-page sample has no percentile or production extrapolation.
The 69 replay frame pages at limit2 measured 1547–1998 bytes. No CPU/memory
sampling, long soak, network emulation, production-sized dataset or SLA validation
was performed; host CIM resource access was unavailable.

Existing desktop/mobile role journeys and new tablet/320px reflow passed automated
axe checks on exercised screens. Reduced motion, labels, visible keyboard focus,
native skip-link sequential navigation, safe missing-route response and map/chart
text alternatives were exercised. Genuine screenshots were inspected. 640/320px
reflow represents the layout constraint of 200/400% on a1280px viewport; it is
**not an executed native browser zoom test**. Full screen-reader/manual assistive
technology certification and exhaustive WCAG conformance remain unverified.
Browser navigation outage/reload and actual API/DB outage are distinct tests.

## Traceability, defects and remaining gates

[Machine-readable traceability](m09-traceability.json) maps all40 original M02
cases and eight M09 risk groups to executable source and scoped observations.
Original M02 disposition: **21 PASS, 13 BLOCKED, 6 NOT IMPLEMENTED, 0 FAIL**.
BLOCKED means the *whole original requirement* includes deferred functionality;
passing implemented subsets are explicitly recorded. The eight M09 risk groups
pass within their stated bounds. This is not full acceptance of every future
roadmap feature.

No critical/high/medium runtime defect was demonstrated in these runs. One LOW
historical evidence defect remains disclosed: `demo_backend.py` hardcodes
`migration_head=m07_a_001` in its summary although the actual current database is
`m07_c_001`. The unchanged legacy script's label must not be used as live inventory;
the new M09 inventory and HTTPS probe query the actual revision/table count. Its
workflow/restart/NOT_VERIFIABLE assertions pass. Correcting the historical pinned
tool/source-manifest chain is deferred; no functional database behavior is affected.

Execution/fixture failures were retained outside Git and corrected without
weakening product checks: inaccessible default Windows pytest temp directory
(task-private temp used); an omitted explicit origin in a private demo input;
initial new-test receipt/table/label/path assumptions; native skip-link destination
assertion corrected to its actual next keyboard target; and a diagnostic all69
run correctly throttled when three sessions shared one member (three separately
authorized synthetic engineers used, limits unchanged). The traceability suite
also correctly refused two local runs with different test-tool source digests;
same-head independent repetitions remain mandatory in final CI. None is claimed as a
product defect or a clean first-attempt run.

Release gates remain: D6 visit-access encryption/key custody/consent; D7 scanner,
processing/licensing/private storage; D8 external adapters and reviewed retry
delays; D9 offline synchronization; D10 approved retention, erasure/holds and
operator commitments. Public deployment is fail-closed. Scheduling stays disabled
without actual reviewed shifts/skills/areas/durations/buffers/policies. No valve
actuation route is present.

M08 is digitally source/CAD checked, not physically fit-tested. KiCad connectivity
drafts have no native ERC; complete field firmware/validated acoustic recorder do
not exist. All41 BOM prices are estimates, not quotations. ₹59,870 leaves only
₹130 procurement margin; the proposed pressure range is poorly suited to sensitive
low-pressure work. GUARD-5 physical collection remains unverified. Owner/hardware
tasks remain electrode/collection/migration/blockage/rain/bypass challenges,
power/excitation safety, real pressure/flow calibration, common-clock phase/timing,
pickup mounting/passive audibility, controlled leak/no-leak and real comparable
before/after measurements. No purchase or physical test was performed.

Issues1–5 and8 remain completed. M06 issue6 is eligible for owner closure against
its implemented synthetic ingestion/replay/mode/truth-boundary scope. Keep M07
issue7 open (offline/comparable operational evidence/deferred scope), M09 issue9
open pending owner review, and M10 issue10 open. No issue is closed by this PR.

## Reproduction and CI evidence

From the repository root, with the existing Python3.12 locked backend environment
and an operator-provisioned **exactly confirmed** disposable PostgreSQL/PostGIS
database, run:

```text
python services/api/tools/verify_backend.py --operator-config <private/operator.json> --runtime-config <private/runtime.json> --confirm-disposable-database <hydro_disposable_name> --evidence-directory <outside-Git/evidence1>
python services/api/tools/verify_backend.py --operator-config <private/operator.json> --runtime-config <private/runtime.json> --confirm-disposable-database <hydro_disposable_name> --evidence-directory <outside-Git/evidence2>
python -m pytest services/api/traceability_tests -q --acceptance-evidence <outside-Git/evidence1/acceptance-summary.json> --acceptance-evidence <outside-Git/evidence2/acceptance-summary.json>
python services/api/tools/verify_m09.py --operator-config <private/operator.json> --runtime-config <private/runtime.json> --confirm-disposable-database <hydro_disposable_name> --evidence-directory <outside-Git/m09>
python scripts/check_m09.py
python scripts/check_repository.py
python scripts/check_m02_design.py
python scripts/check_m07_design.py
python scripts/check_m07c.py
git diff --check
```

Use the existing dedicated synthetic browser-fixture preparation and HTTPS
startup documented in the workflow. Local M09 used a private copy of the existing
fixture script with only ROOT and its disposable-name allowlist adapted; no
application source was changed. Run the existing `node tools/browser-suite.mjs`
first from `apps/web`, then
`node node_modules/@playwright/test/cli.js test browser/m09-acceptance.spec.ts`.
Keep the current private-fixture and screenshot environment variables and existing
certificate/SPKI model; no OS trust/certificate or broad TLS bypass is introduced.
After browser tests, run the M09 HTTPS probe using that marked disposable fixture:

```text
python services/api/tools/m09_https_probe.py --fixture-directory <outside-Git/browser-private> --operator-config <private/operator.json> --confirm-disposable-database <hydro_disposable_browser_name> --output-directory <outside-Git/probe-private>
```

CI preserves all four mandatory jobs and prior checks, adds explicit M09 runs,
and uploads only allowlisted sanitized JSON/PNG evidence for14 days:
`HYDROOVERITY_M09_INDEPENDENT_ACCEPTANCE`,
`HYDROOVERITY_M09_BROWSER_AND_RECOVERY`, existing combined browser/backend
evidence and the regenerated M08 package. Private runtime JSON, certificates,
process logs, mail and evaluator data are never included. Actual upload links and
all four job conclusions must be verified in the PR before owner acceptance.
No merge, public deployment, issue closure or M10 work is authorized by this report.
