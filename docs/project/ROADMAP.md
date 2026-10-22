# Roadmap and initial backlog

The M01 request refines the master context's suggested eight-stage grouping into ten milestones. This changes sequencing, not the frozen sensing system. No deadlines or release promises are invented. Each future milestone needs separate owner authorization.

| Milestone | Scope | Exit criteria |
| --- | --- | --- |
| M01 — GitHub Foundation | Repository, documentation, workflow checks and issue organization. | Required source/docs/paths reviewed; integrity passes; private remote synchronized and CI outcome verified. |
| M02 — Website Architecture | Design system, role definitions, API contracts and database schema. | Approve role/tenant matrix, UX/data/API contracts, security/offline model and compatible stack without silently resolving open choices. |
| M03 — Backend Foundation | Authentication, organization data, pipeline records and incident management. | Persistent backend with role/tenant deny tests, validation, recovery/session design and audit evidence. |
| M04 — Frontend Foundation | Navigation, user-specific dashboards and responsive interface. | Integrated role-aware workflows with real backend, accessible loading/error/empty states and browser checks. |
| M05 — Scientific Simulations | Hydraulic, acoustic and GUARD-5 simulation engines. | Reproducible seeds/configs, hidden truth, holdouts, competent baselines and honest coverage/error metrics. |
| M06 — Simulation Integration | Connect simulation outputs to the actual backend and monitoring interface. | Explicit synthetic ingestion/stream/replay, globally visible simulation mode and truth-leakage deny tests. |
| M07 — Maintenance Operations | Citizen complaints, work orders, repair verification and reporting. | Tenant-aware complaint-to-repair loop, offline retries, comparable verification/unverifiable outcomes and exports. |
| M08 — Digital Hardware Engineering | Mechanical CAD, electronics schematics, firmware and final BOM. | Reviewed buildable digital source, clock/channel/fit plans, safety/calibration/power/BOM within cap; untested status retained. |
| M09 — Full-System Testing | Security, correctness, simulation validity, performance and workflow verification. | Executed cross-role/E2E/security/accessibility/scientific checks with reproducible evidence and limitations. |
| M10 — Final Demonstration | Professional video, engineering visuals, recorded website demonstration and SIH presentation. | Labeled 2–3 minute concept animation and genuine software capture, honest evidence ledger and final PPT. |

M01/M02/M05/M08 are approved and merged. M02's complete name is **HYDROOVERITY Website Architecture and Database Design**; its short GitHub title is Website Architecture. Earlier planning gates below are historical; the current milestone status follows.

Create one focused planning issue per milestone, avoiding duplicates. M01 may close only with actual setup evidence; future issue creation does not authorize implementation. Labels identify responsibility. The machine-readable [backlog](../../.github/backlog.json) preserves intended milestone/issue definitions if remote configuration is unavailable. Do not invent due dates, assignees or collaborator permissions.

## Approved M02/M05 integration status

M02 PR #11, M05 PR #12 and M08 PR #13 are merged. M05 remains SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED. No scientific targets or assumptions change through backend implementation.

## M03 current status

The owner separately authorized the complete [M03 request](MILESTONE_03_REQUEST.md). The backend foundation implements 58 of 117 canonical operations and 30 of 57 application tables, with real PostgreSQL/PostGIS, authentication, authorization and a minimal complaint-to-independent-NOT_VERIFIABLE workflow. See [implementation](../engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md) and [executed acceptance](../testing/M03_ACCEPTANCE_RESULTS.md). PR #14 and recovery PR #15 are approved and merged; issue #3 is closed. No production, field or hardware validation is implied.

## M04 current status

The owner authorized the [complete M04 request](MILESTONE_04_REQUEST.md) and approved visual Option 3 for the public site with Option 2 information-architecture inspiration for authenticated workspaces. Work is in progress on `feature/m04-frontend-foundation` from main `e0122f5ee4146e49ae6113a1aa6a5ee444b25973`. See the [implementation record](../engineering/M04_FRONTEND_IMPLEMENTATION_REPORT.md) and [execution ledger](../testing/M04_EXECUTION_LEDGER.md). M04 must pass real integration/browser/visual checks before completion is claimed. Issue #4 remains open; no automatic merge or closure. M06/M07/M09/M10 and animation remain outside this authorization.
