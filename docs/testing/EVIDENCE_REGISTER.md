# Evidence register

Baseline: M01, 20 October 2026. Source: [preserved master context](../project/HYDROOVERITY_MASTER_CONTEXT.md). This is an evidence inventory, not a results dashboard.

| ID | Claim / artifact | Evidence status and limits |
| --- | --- | --- |
| E-001 | Master context and separate M01 request | DOCUMENTED: preserved source text with SHA-256 manifest |
| E-002 | Submitted six-slide SIH presentation | DOCUMENTED indirectly by master-context section 2; original deck absent, not independently inspected |
| E-003 | 184 Python tests, 5 frontend tests, 17 browser checks, 6 package checks, EPANET 2.2 model | HISTORICAL REPORTED RESULTS ONLY: attributed to master-context sections 2/14; original code/logs unavailable and not rerun in M01 |
| E-004 | 30.1–38.9 m acoustic interval | SIMULATED historical example reported in context; not a physically located leak |
| E-005 | 1 L/min × 8 h/day = 480 L/day | Hypothetical illustration, not measured recovered water |
| E-006 | Frozen architecture and planned ₹56,750 materials allocation | DOCUMENTED design/estimate; hardware and quotations not verified |
| E-007 | Website, APIs, three engines, CAD, PCB, firmware | PLANNED here; no working implementations delivered in M01 |
| E-008 | Hardware/field performance | UNKNOWN / UNESTABLISHED; context reports physical trials 0 and field trials 0 |
| E-009 | Repository checks and GitHub setup | Verify actual M01 commands/CI/remote state in the setup report; these establish repository hygiene only |
| E-010 | Novelty, lifespan, contamination detection, village-wide pinpointing, field savings | Not established or outside claimed scope; never inferred from software tests |

## Evidence vocabulary and future record format

Use DOCUMENTED, SIMULATED, CODE-TESTED, HARDWARE-TESTED, FIELD-VALIDATED and UNKNOWN with source, acquisition context, date, commit/config, executed command/procedure, output artifact/hash, denominator, reviewer and limitations. Design files and HIL stubs are not HARDWARE-TESTED. Laboratory measurements are not FIELD-VALIDATED. Keep status on individual claims, not a blanket success label.

Future physical targets remain aspirations: GUARD-5 ≥90% event recognition / ≤5% misleading environmental declarations under a declared trial; accepted acoustic ≥80% within 1 m on a qualified approximately 10–15 m physical span with useful coverage and low confident error. No such results exist here.

Imported historical artifacts must be inspected, licensed and linked before reproduction claims. New results must retain failures, excluded/unresolved cases, provenance and full evaluation settings. Do not rewrite historic claims as tests this repository passed.

## M05 software evidence — issue #5

Three simulation engines executed in a separate branch from main7590a65. See [M05 report](M05_SIMULATION_EVIDENCE_REPORT.md) and simulations/evaluation/reference_summary.json for complete denominators and unfavorable outcomes.38 numerical tests passed;8 PNG/SVG figures generated and inspected; repeated PPT numerical outputs matched. This establishes CODE-TESTED software and SIMULATED model results only. Physical collector behavior, passive leak audibility, field reliability and savings remain UNKNOWN/UNESTABLISHED. M05 merge/publication approval is separate; no later milestone begins automatically.
