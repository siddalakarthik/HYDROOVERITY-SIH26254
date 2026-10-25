# Roadmap and initial backlog

The M01 request refines the master context's suggested eight-stage grouping into ten milestones. This changes sequencing, not the frozen sensing system. No deadlines or release promises are invented. Each future milestone needs separate owner authorization.

| Milestone | Scope | Exit criteria |
| --- | --- | --- |
| M01 â€” GitHub Foundation | Repository, documentation, workflow checks and issue organization. | Required source/docs/paths reviewed; integrity passes; private remote synchronized and CI outcome verified. |
| M02 â€” Website Architecture | Design system, role definitions, API contracts and database schema. | Approve role/tenant matrix, UX/data/API contracts, security/offline model and compatible stack without silently resolving open choices. |
| M03 â€” Backend Foundation | Authentication, organization data, pipeline records and incident management. | Persistent backend with role/tenant deny tests, validation, recovery/session design and audit evidence. |
| M04 â€” Frontend Foundation | Navigation, user-specific dashboards and responsive interface. | Integrated role-aware workflows with real backend, accessible loading/error/empty states and browser checks. |
| M05 â€” Scientific Simulations | Hydraulic, acoustic and GUARD-5 simulation engines. | Reproducible seeds/configs, hidden truth, holdouts, competent baselines and honest coverage/error metrics. |
| M06 â€” Simulation Integration | Connect simulation outputs to the actual backend and monitoring interface. | Explicit synthetic ingestion/stream/replay, globally visible simulation mode and truth-leakage deny tests. |
| M07 â€” Maintenance Operations | Citizen complaints, work orders, repair verification and reporting. | Tenant-aware complaint-to-repair loop, offline retries, comparable verification/unverifiable outcomes and exports. |
| M08 â€” Digital Hardware Engineering | Mechanical CAD, electronics schematics, firmware and final BOM. | Reviewed buildable digital source, clock/channel/fit plans, safety/calibration/power/BOM within cap; untested status retained. |
| M09 â€” Full-System Testing | Security, correctness, simulation validity, performance and workflow verification. | Executed cross-role/E2E/security/accessibility/scientific checks with reproducible evidence and limitations. |
| M10 â€” Final Demonstration | Professional video, engineering visuals, recorded website demonstration and SIH presentation. | Labeled 2â€“3 minute concept animation and genuine software capture, honest evidence ledger and final PPT. |

M01/M02/M05/M08 are approved and merged. M02's complete name is **HYDROOVERITY Website Architecture and Database Design**; its short GitHub title is Website Architecture. Earlier planning gates below are historical; the current milestone status follows.

Create one focused planning issue per milestone, avoiding duplicates. M01 may close only with actual setup evidence; future issue creation does not authorize implementation. Labels identify responsibility. The machine-readable [backlog](../../.github/backlog.json) preserves intended milestone/issue definitions if remote configuration is unavailable. Do not invent due dates, assignees or collaborator permissions.

## Approved M02/M05 integration status

M02 PR #11, M05 PR #12 and M08 PR #13 are merged. M05 remains SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED. No scientific targets or assumptions change through backend implementation.

## M03 current status

The owner separately authorized the complete [M03 request](MILESTONE_03_REQUEST.md). The backend foundation implements 58 of 117 canonical operations and 30 of 57 application tables, with real PostgreSQL/PostGIS, authentication, authorization and a minimal complaint-to-independent-NOT_VERIFIABLE workflow. See [implementation](../engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md) and [executed acceptance](../testing/M03_ACCEPTANCE_RESULTS.md). PR #14 and recovery PR #15 are approved and merged; issue #3 is closed. No production, field or hardware validation is implied.

## Current accepted milestones and remaining work

M04 was owner-merged in PR #16; issue #4 is completed. M06 synthetic integration was merged in PR #19; issue #6 was closed after combined M09 acceptance. M07-A/B/C were merged in PRs #18/#20/#21, but issue #7 remains open: offline, secure images, comparable operational verification and other original acceptance gaps are not completed by a passing implemented subset.

M09 PR #22 merged at `d772045ba6d44ddd1bbee1e4baf890c5786628d5`; all four main CI jobs passed and issue #9 is closed within its testing/evidence scope. Pre-M10 foundation PR #23 merged at `848c1c8a1dbf72f980c1f58454a41d0bd332eab8`, with four post-merge jobs passing. It corrects the live migration label and establishes the [completion register](../testing/PRE_M10_COMPLETION_REGISTER.md).

Current implementation is 111 operations/51 tables. Original M02 acceptance remains 21 PASS, 13 BLOCKED and 6 NOT IMPLEMENTED. See the register for each original requirement, required tests and owner-controlled gates. M08 remains digitally checked, not physically tested; M05 evidence and unfavorable results are unchanged.

The owner authorized focused pre-M10 software completion, documentation, website quality and hardening with exact-head review/CI and post-merge CI. This does not activate public deployment, waive D6–D10, authorize purchases or begin M10. Issue #10 remains open for a separate final readiness decision.
