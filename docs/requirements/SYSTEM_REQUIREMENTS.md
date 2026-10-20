# System requirements and SIH traceability

Status: requirements only; no application or sensor acceptance is claimed. Source: [master context](../project/HYDROOVERITY_MASTER_CONTEXT.md), sections 1–11.

| ID | Supplied SIH expectation | Planned HYDROOVERITY capability | Planned acceptance evidence |
| --- | --- | --- | --- |
| SIH-01 | Detect and accurately locate leakages in pipelines | WATCH sector screening; GUARD-5 joint-local observations; EAR candidate interval on eligible spans | Holdout detection/confident-error/coverage results; future controlled physical trials |
| SIH-02 | Provide real-time alerts and monitoring | Timestamped observation ingestion, state qualification, alert and freshness workflows | Stream/reconnect/stale-data tests, alert latency with stated conditions |
| SIH-03 | Be energy-efficient and cost-effective | Selective collars, reusable investigation pair, power budget and ₹60,000 demo cap | Reviewed BOM/quotations and power estimates; later measurements |
| SIH-04 | Integrate with existing water-supply infrastructure | Non-pressure-bearing external collar, accessible acoustic mounts and topology metadata | Digital fit/interface review; later approved rig/installation qualification |
| SIH-05 | Support remote monitoring and maintenance planning | Multi-role portal, incidents, work orders, offline notes and repair verification | Tenant-aware end-to-end investigation-to-closure tests |

## Derived engineering requirements

| ID | Requirement | Planned verification |
| --- | --- | --- |
| ENG-01 | Exactly five independently measured collar channels; EXT distinct from BYPASS | Schematic/channel review and future injection/crosstalk tests |
| ENG-02 | OFF/FILLING/STEADY/DRAINING/UNKNOWN with explainable transitions | State scenarios including legitimate draw/storage and sensor drift |
| ENG-03 | Routine stable-period qualification must preserve urgent wetting/fault observations | Filling/draining alert regression cases |
| ENG-04 | Two acoustic channels share one physical sampling clock | Clock/pin review; future timing capture/calibration |
| ENG-05 | Qualified intervals and explicit abstention; no coordinate at zero pressure without evidence | Near-A/center/B sign tests, noise/branch/multipath holdouts |
| ENG-06 | Simulated, lab, field and manual provenance remain distinguishable | Contract/storage/export/authorization tests |
| ENG-07 | Truth does not enter detector inputs or regular APIs | Blind-input and tenant/API leakage tests |
| ENG-08 | Repairs need comparable operating evidence or an unverifiable outcome | Incomplete/successful repair and noncomparable-window scenarios |
| ENG-09 | Privacy, tenant isolation and backend role enforcement | Cross-role/cross-tenant deny tests and upload/auth threat review |
| ENG-10 | No fabricated results; reproducible configs, seeds, denominators and failures | Evidence/source review and rerun records |

## Outcomes and acceptance policy

Early identification, reduced non-revenue water, improved O&M and reliable service are intended outcomes, not measured achievements. Define thresholds, eligibility, uncertainty calibration, denominators and holdouts before experiments. Aspirational physical targets in the master context remain future goals and must not drive cherry-picked synthetic results.

M01 verifies only repository integrity. Later tests must cite requirement IDs, commit, environment, inputs and actual results. Consult [website requirements](WEBSITE_REQUIREMENTS.md), [simulation plan](../testing/SIMULATION_PLAN.md) and [limitations](../engineering/ENGINEERING_LIMITATIONS.md).
