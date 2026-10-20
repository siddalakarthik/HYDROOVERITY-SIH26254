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

M01 completed and verified. M02 is authorized for design on its feature branch and awaits owner review through issue #2; no M03 implementation is authorized. Later milestones remain planned. M02's complete name is **HYDROOVERITY Website Architecture and Database Design**; its short GitHub title is Website Architecture.

Create one focused planning issue per milestone, avoiding duplicates. M01 may close only with actual setup evidence; future issue creation does not authorize implementation. Labels identify responsibility. The machine-readable [backlog](../../.github/backlog.json) preserves intended milestone/issue definitions if remote configuration is unavailable. Do not invent due dates, assignees or collaborator permissions.

## Approved M02/M05 integration status

M02 design is owner-approved and PR#11 merged. M05 implementation is owner-approved as SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED evidence; its PR#12 integrates the approved M02 main and must pass both validation suites before merging. Earlier pending-review wording records historical gates and does not override this approval. M03/M04/M06/M07/M08/M09/M10 remain unstarted and require separate authorization. No scientific targets or assumptions change through integration.
