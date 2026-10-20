# Simulation plan

Status: M05 engines and primary software experiments are implemented/executed; see [M05 evidence](M05_SIMULATION_EVIDENCE_REPORT.md). All outputs are **SIMULATION**, with physical performance unvalidated. [Master context](../project/HYDROOVERITY_MASTER_CONTEXT.md), section 10, controls scope.

## Engines

| Engine | Inputs/assumptions | Planned outputs and controls |
| --- | --- | --- |
| SIM-HYDRAULICS | WNTR/EPANET pressurized network, pump/tank, branches/material/diameter/length, demand and modeled leaks | Flow/pressure/state observations; leak vs demand/storage cases; topology and false-alarm controls; solver validity disclosed |
| SIM-ACOUSTICS | Hidden source position; signal level/bandwidth; effective speed/path; attenuation, transducer response, phases, clipping/noise, pump correlation, reflections/branches and multiple sources | Identical-recording filtered correlation/GCC-PHAT baselines; qualified multi-window intervals, quality reasons and abstentions |
| SIM-GUARD-5 | Assumed A/B/C/EXT/BYPASS transfers, arrival delays, retention/evaporation, thresholds, faults, blockage, rain/dew and seepage | Channel observations and diagnostic outcomes; single pad vs unguarded multizone vs full guarded/service-test comparisons |

Hydraulics does not validate fast two-phase filling, trapped air or water hammer. GUARD-5 coefficients are assumptions, not CFD or manufactured geometry validation. Synthetic acoustic success cannot establish weak plastic-leak audibility. Low pressure may remove passive signal completely.

## Orchestrator and reproducibility

Create restricted TRUTH first; emit limited OBSERVED records through the same validated ingestion boundary used by the application. Never send leak position/label to the detector or regular APIs. Preserve deterministic seed, run ID, config/hash, scenario/algorithm versions, commit/environment, time base, units, calibration assumptions and complete outcomes. A replay must reproduce observations/evaluation within a declared numerical tolerance.

Use distinct tuning and blind holdout seeds/conditions; predeclare thresholds, eligibility, interval construction and evaluation denominators. Test truth exclusion explicitly. Regular engineer/citizen views do not get unrestricted ground truth; privileged evaluation access needs explicit authorization and audit.

## Mandatory catalogue

No leak; weak pinhole; longitudinal slit; loose joint; fully pressurized leak; low/zero pressure; filling/draining; normal customer draw; pump noise; external rain; condensation; blocked collector path; electrode disconnect; stale sensor; multiple leaks; mixed material/branch; insufficient acoustic signal; false confident correlation; incomplete repair; successful repair.

## Evaluation

Report event precision/recall and false positives/negatives; false alarms per observed hours/cycles; accepted/unresolved fractions and eligible coverage; confidently wrong accepted locations; median/P95 location error with all-case and accepted-case denominators; correct-within-distance on both populations; confidence calibration; incident latency and repair completion. Separate simulated power/resource estimates from measurements. Retain failures and exclusions with reasons, not favorable-only trials.

Future physical aspirations only: GUARD-5 recognition ≥90% with ≤5% misleading environmental declarations under a predeclared controlled trial; acoustic accepted locations ≥80% within 1 m on a roughly 10–15 m qualified physical span, with useful coverage and low confident error. These are not M01 acceptance results or guaranteed targets for synthetic generation.

Commit small configs/manifests and reviewed summary tables; raw generated results follow the [artifact policy](../engineering/ARTIFACT_POLICY.md). M01 created no experiment results. M05 results and their limitations are documented in the linked evidence report.
