# Decision log

Baseline date: 20 October 2026. Record owner-approved changes with rationale, alternatives, affected requirements/evidence and revisit criteria. Do not silently alter frozen decisions.

| ID | Decision / status | Reason and revisit condition |
| --- | --- | --- |
| D-001 | HYDROOVERITY, Team TARK, SIH26254 — frozen | Preserve submitted identity/mission; only explicit owner-approved correction |
| D-002 | WATCH + five-channel GUARD-5 + EAR-PAIR + evidence + VERIFY — frozen functional architecture | Submitted continuity and complementary evidence; substantive change requires written proposal/owner approval |
| D-003 | A/B/C, independent EXT and BYPASS; non-pressure-bearing external collar — frozen | Distinguish collection/environmental failures; geometry remains a testable hypothesis |
| D-004 | Single physical clock for stereo acoustic acquisition — frozen | Avoid independent wireless capture-clock ambiguity; alternatives need timing proof and owner review |
| D-005 | Explicit supply states, uncertainty/abstention and separate urgent lane — frozen | Intermittent supply/observability; refine thresholds through declared experiments |
| D-006 | ₹60,000 materials ceiling, current estimated ₹56,750 incl. contingency — constraint | Voluntary total demo-material cap; quotes/BOM reconcile before any approved purchase |
| D-007 | Digital-first; no current build/purchases — owner decision | Website/simulation/digital engineering before final presentation; construction needs new authorization |
| D-008 | Private `siddalakarthik/HYDROOVERITY-SIH26254`, main, license undecided — M01 authorized | Clear authenticated owner and explicit request; no Pages/collaborator invitations/public release |
| D-009 | M01 request's detailed folders and M01–M10 order — current plan | Supersedes suggested layout/eight-stage grouping in master context; does not change sensing architecture |
| D-010 | TypeScript frontend/Python backend-science; named stack provisional | User direction and scientific ecosystem; version/hosting/integration review in M02 before installs |
| D-011 | Ingestion/notifications folders are logical responsibilities — organization only | No requirement for independent microservices/deployments; deployment topology pending M02 |
| D-012 | Read-only minimal repository CI; no fake app tests — M01 | Check actual foundation only; expand checks when code exists |

## Pending decisions / gates

| ID | Choice needed | Gate |
| --- | --- | --- |
| P-001 | Role/tenant matrix, session/CSRF/password recovery, retention/uploads | M02 before auth/schema implementation |
| P-002 | Canonical evidence/incident/repair enums; UNVERIFIABLE vs NOT_VERIFIABLE | M02 before migrations/API contracts |
| P-003 | Water-balance boundary and demand/storage accounting | Before hydraulic inference |
| P-004 | Versions, chart library, realtime transport, local/hosting and offline conflict policy | M02 before dependency installation |
| P-005 | Collar dimensions/material/orientation; dry/disconnect supervision | M08 detailed mechanical/electrical design |
| P-006 | Pickups, front-end values, actual ADC clock/MCLK, sample rate, buffers/pins | M08 acquisition design |
| P-007 | Thresholds, eligibility, uncertainty calibration, holdouts and denominators | M05 before experiments/tuning |
| P-008 | Detailed 26-line BOM, source artifacts, quotations and ratings | Before procurement or historical reproduction claims |
| P-009 | Software/assets license and public-release terms | Explicit owner choice before public release |

No Docker Compose services, database migrations, stack packages or detailed hardware designs are created in M01. Local foundation tooling uses Python standard library only. The new roadmap keeps dependent milestones independently authorized.

## M02 proposed decisions — issue #2, awaiting owner design review

| ID | Choice and reason | Alternative / consequence |
| --- | --- | --- |
| D-013 | Global user + tenant memberships + explicit scoped grants | Per-tenant duplicate identities rejected; no global super-admin UI |
| D-014 | FastAPI opaque server sessions, same-origin proxy, CSRF | Independent NextAuth/JWT store rejected to avoid competing auth |
| D-015 | PostgreSQL17/PostGIS3.5 normalized graph and composite tenant FKs; RLS defense in depth | Client filtering rejected; pool/runtime-role complexity must be tested |
| D-016 | NOT_VERIFIABLE canonical; evidence/incident/task/outcome separate | Closing work never means passed science; M01 terms mapped in state document |
| D-017 | Credential-derived origin + restricted truth schema/object roles and sealed truth seed | Writable source field/public seed reconstructing truth rejected |
| D-018 | SSE + bounded durable replay, polling fallback | WebSocket bidirectionality unnecessary initially |
| D-019 | Minimal encrypted offline assigned-task drafts, current authorization on sync | Full offline GIS and distributed last-write-wins rejected |
| D-020 | Private quarantined uploads, safe derivatives, per-parent ACL | Public buckets/original image serving rejected |
| D-021 | Same-origin web/API, one DB and optional leased worker, private objects | Mandatory ingestion/notification microservices rejected |
| D-022 | OpenAPI3.1 JSON, UUID IDs, typed errors, idempotency/version guards | Duplicate YAML contract and arbitrary status PATCH rejected |
| D-023 | Role-focused dense accessible light UI, ten structured wireframes | Decorative metrics, fake live data and unlicensed copied assets rejected |

P-001/P-002/P-004 software design choices are now proposed in the linked M02 contracts, awaiting review before M03. P-003 boundary accounting design excludes customer demand already included in measured outflow; actual sector metering remains future configuration. P-005/P-006/P-007/P-008/P-009 remain unresolved for their hardware/science/source/license gates. No physical threshold, sensor model, wave speed, collector performance or detection accuracy was frozen here. Deployment providers/recurring budget, final retention/legal policy, evaluator grant procedure, tile license and exact patched dependency lockfiles need review before their real deployment/implementation use. No actual grants/purchases occur in M02.

## M02 final review corrections — awaiting owner merge approval

| ID | Decision | Rationale / deployment gate |
| --- | --- | --- |
| D-024 | Authentication has operation-specific noncached retry semantics, global identity scope and single-use token consumption; tenant business receipts exclude auth and secrets | Prevent session resurrection/token bypass; M03 must prove race, lost-response, CSRF and replay behavior. Global self-service uses reauthorized final-state updates. Credential issuance rejects secret replay. |
| D-025 | Public contact is one global private project-team inbox, one proposed table, 30-day deletion | Anonymous messages cannot fabricate tenant memberships. Fixed server ownership, no public retrieval; designated operator/access/retention procedure must be configured before enabling intake. |
| D-026 | Independent pinned OpenAPI validator plus focused design regression checks | Standards conformance and project security invariants need distinct checks. Isolated review-tool installation is explicitly authorized by the final M02 review request; no application framework/server/database is installed or implemented. |

The four slices in M03_M04_IMPLEMENTATION_SEQUENCE.md sequence the existing M03–M10 roadmap; they do not authorize or claim future milestone implementation.

## M05 authorized simulation decisions (issue #5)

M05 runs independently from stable main7590a65, without merging M02. Python3.12 isolated environment; WNTR1.4/EPANET2.2 PDA and SI emitter leaks; NumPy/SciPy/Pandas/Matplotlib/pytest only as needed, exact resolved versions locked before benchmark execution. No GPU/framework or deployment.

The sector boundary is IN minus C1+C2+C3 terminal customer meter flows. Customer demand is already included at those outlets and is never subtracted again; no storage in the pressurized model. Controlled source head represents a pump/supply-boundary change, not a measured pump curve. OFF/FILLING/DRAINING are labeled state abstractions, not solved two-phase transients.

Acoustics uses fractional delays on a common sample grid, assumed dispersive/attenuating transfer functions and explicit speed uncertainty; no measured plastic-pipe audibility claim. GUARD-5 uses conserved lumped volumes, uncertain collection/rain-transfer assumptions, separate EXT/BYPASS and honest unknown supervision.

Benchmark thresholds are fixed in simulations/scenarios/benchmark.json before evaluation. Development and holdout truth/observation seeds are disjoint; detector interfaces have no truth or generator seed. Any later algorithm change must change its version/hash and rerun all cases, never silently select favorable holdouts. All results remain SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED.

## Approved M02 + M05 integration

The owner approved M02 design at89fb8ff and M05 simulation evidence atad48373. M02 PR#11 merged at63c660b. M05 originally developed independently from main7590a65; integration now merges that approved M02 main into M05 without altering simulation source, configs, thresholds, baselines, results or scientific caveats. The historical pending-review statements above describe their original review gates; this approval resolves the M02 design gate only. No later milestone implementation is authorized. Both independent validation environments remain separate in the combined CI workflow.
