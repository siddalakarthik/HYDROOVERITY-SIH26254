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
