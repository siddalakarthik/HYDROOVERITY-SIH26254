# HYDROOVERITY

**Find the leak. Understand the evidence. Verify the repair.**

Team **TARK** · Team ID **155480** · Smart India Hackathon 2026 · **SIH26254** · Hardware / Clean & Green Technology

Problem setter: **Ministry of Jal Shakti**. Problem statement: **Development of Indigenous Leak Detection Sensor Systems for Operation & Maintenance of Water Supply Pipelines**.

HYDROOVERITY proposes affordable, indigenous, evidence-qualified leak detection, bounded localization and accountable maintenance for water-distribution networks. Treated-water leakage can waste resources, disrupt service and create ingress risk. The system does not directly detect contamination.

## Current status

This repository starts with **M01: documentation, organization and repository checks only**. There is no runnable website, backend, simulator, CAD assembly, PCB or firmware implementation here yet. No license has been selected. The repository is intended to remain private until the owner explicitly authorizes release.

| Evidence category | Current status |
| --- | --- |
| Designed | Functional concept frozen; detailed hardware design and component qualification pending |
| Implemented in software | Repository-integrity tooling only; application implementation pending |
| Simulated | Historical results reported by the supplied context; original artifacts not reproduced here |
| Physically tested | No physical prototype or trials established; context reports 0 physical trials |
| Field validated | Context reports 0 field trials |

See the [evidence register](docs/testing/EVIDENCE_REGISTER.md) for attribution and limits. A successful repository check is not a sensor-performance test.

## How the proposed system works

`HYDRO-WATCH -> [GUARD-5 local joint evidence || HYDRO-EAR eligible-span evidence] -> evidence assessment -> incident -> work order -> repair -> HYDRO-VERIFY`

- **HYDRO-WATCH** uses available pressure, flow, demand/storage context and device health to qualify `OFF`, `FILLING`, `STEADY`, `DRAINING` or `UNKNOWN`. Intermittent supply makes fixed night-flow windows unreliable. Unexplained imbalance is not automatically a leak.
- **GUARD-5** is a removable, non-pressure-bearing collar at an accessible exposed joint. Five independent wetness channels are `COLLAR_A`, `COLLAR_B`, `COLLAR_C`, `COLLAR_EXT` and `COLLAR_BYPASS`. Three protected collection pockets, an outside environmental witness, a separate lower bypass, guards, drainage and external service-challenge ports help investigate water arrival and collection faults. Mechanical separation remains an untested hypothesis.
- **HYDRO-EAR / EAR-PAIR** investigates a surveyed, adequately pressurized, eligible simple span using two matched pipe-contact pickups, analog front ends and one stereo PCM1808-class ADC with one physical sampling clock. It may provide a candidate distance interval when passive signal and path knowledge support it. A portable pair does not continuously pinpoint an entire village.
- **Evidence qualification** retains competing explanations: local joint suspicion, hydraulic abnormality, environmental exposure, collection failure, sensor fault, ambiguous path and insufficient signal. Confirmed wetness is not proof of leak origin. Decisions carry reasons, provenance, uncertainty and next actions.
- **HYDRO-VERIFY** connects investigation, assignment, notes/photos, repair records and comparable before/after checks. A case can close, reopen or remain unverifiable. Citizen reports coexist with sensor evidence without automatically confirming leakage.

Rural networks may combine PVC/HDPE and mixed materials, sparse access, low pressure, unknown customer demand, tanks, pump vibration, rainfall, condensation and unreliable connectivity. These are required test conditions, not exceptions to hide.

## Planned product and engineering outputs

- Public explanation and citizen complaint/status pages; authenticated utility, supervisor, technician and administrator workflows.
- Tenant-aware authentication/authorization, persistent observations, network maps, incidents, work orders, diagnostics, repair verification, reports, audit history and feedback. Mobile/offline notes and retries; visible simulation mode.
- Three reproducible engines: hydraulics with WNTR/EPANET where valid, acoustic parameter sweeps and GUARD-5 water-path/fault logic. Hidden truth, holdouts, baseline comparisons and honest unresolved results.
- FreeCAD-compatible mechanical designs, KiCad electronics, firmware, calibration plans, BOM and safety/power analyses in later milestones.
- A 2–3 minute **CONCEPT ANIMATION / SIMULATED EXAMPLE**, genuine software screen capture and final SIH presentation. Hardware validation remains future work; animation does not replace it.

Provisional stack: Next.js / React / TypeScript / Tailwind, Python FastAPI, PostgreSQL / PostGIS, MapLibre, Recharts or equivalent, Docker Compose, pytest, Vitest and Playwright. Compatibility and integration decisions precede dependency installation. No stack packages are installed by M01.

## Budget and limitations

The potential complete demonstration has a **₹60,000 INR materials ceiling**. Current estimated allocation is **₹56,750**, including **₹5,000 contingency**, leaving **₹3,250 headroom**. This is not a supplier quotation, village installation cost or government reimbursement promise. No procurement is authorized now.

Weak plastic-pipe signals, zero pressure, unknown wave speed, branches/multiple leaks and environmental moisture can prevent diagnosis. EPANET is not a complete filling/transient/water-hammer model. Simplified water-transfer models do not validate manufactured collectors. No measured accuracy, range, battery life, savings or patent novelty is claimed. Read [engineering limitations](docs/engineering/ENGINEERING_LIMITATIONS.md).

## Repository navigation

| Path | Responsibility |
| --- | --- |
| [apps/](apps/README.md) | Future public website and role-specific web workflows |
| [services/](services/README.md) | Future API, ingestion and notification responsibilities |
| [packages/](packages/README.md) | Future shared contracts and configuration |
| [simulations/](simulations/README.md) | Three engines, scenarios, evaluation and result policy |
| [hardware/](hardware/README.md) | Future mechanical, electrical, embedded and calibration work |
| [data/](data/README.md) | Synthetic examples, future schemas and privacy boundaries |
| [docs/](docs/README.md) | Authoritative source, requirements, decisions and evidence |
| [tests/](tests/README.md) | Future application and system tests; none fabricated |
| [scripts/](scripts/README.md) | Dependency-free repository validation |
| [design/](design/README.md) | Future UX, wireframes and design system |
| [animation/](animation/README.md) | Future storyboard and concept-video assets |
| [.github/](.github/README.md) | CI, issue templates, PR template and backlog definitions |

## Validate the foundation

With Git and Python 3.12+ already available, from this repository root run:

```sh
python scripts/check_repository.py
git diff --check
```

The validator checks tracked/unignored files, required paths, local documentation links, source integrity, ignore rules and common credential patterns without printing matched secret values. It is a limited hygiene check, not a comprehensive security audit. There is no application startup command yet.

## Roadmap and contributions

M01 GitHub foundation -> M02 website architecture and database design -> M03 backend -> M04 frontend -> M05 scientific simulations -> M06 simulation integration -> M07 maintenance operations -> M08 digital hardware -> M09 system testing -> M10 final demonstration.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), [SECURITY.md](SECURITY.md), the [documentation index](docs/README.md) and [roadmap](docs/project/ROADMAP.md). Use focused branches and PRs, record decisions, and distinguish executed tests from plans. Follow the [master context](docs/project/HYDROOVERITY_MASTER_CONTEXT.md); its onboarding-only stop instructions are historical and the separate M01 request authorizes this foundation.
