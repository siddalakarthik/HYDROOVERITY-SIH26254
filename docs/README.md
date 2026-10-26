# Documentation index

Current baseline: **112 registered operations (111 existing + one gated contact protocol), 53 migrated application tables, `pre_m10_002`**. M04, M06, M07-A/B/C, M08, scoped M09 and focused pre-M10 improvements are merged. Contact intake remains disabled outside explicit synthetic test policy. The original M07 milestone remains open for residual requirements; M10 has not started. The public GitHub repository is distinct from the private-development application.

Begin with the [pre-M10 completion register](testing/PRE_M10_COMPLETION_REGISTER.md), [M09 full-system evidence](testing/M09_FULL_SYSTEM_ACCEPTANCE.md), [M06 synthetic integration](testing/M06_SCIENTIFIC_INTEGRATION.md), [M07-B scheduling acceptance](testing/M07_B_SCHEDULING_ACCEPTANCE.md), [M07-C communications acceptance](testing/M07_C_COMMUNICATIONS_ACCEPTANCE.md) and [reviewed media](media/README.md) and the [current dependency review](testing/CURRENT_DEPENDENCY_REVIEW.md).

[M07 candidate contracts](architecture/m07/README.md) remain a design catalogue, not a claim that every operation is implemented. [Owner decisions D1–D10](project/m07-planning/M07_OWNER_REVIEW_DECISION.md) retain their privacy, offline, media, external-delivery and release gates. Historical report language below describes its execution-time scope.

The [master context](project/HYDROOVERITY_MASTER_CONTEXT.md) is the preserved project specification. The [M01 request](project/MILESTONE_01_REQUEST.md) authorizes this repository foundation and refines its folder layout and milestone sequence. The [source manifest](project/SOURCE_MANIFEST.json) records source hashes. Onboarding-only instructions in the master context are historical; they do not authorize or prevent later separately approved tasks.

| Document | Purpose |
| --- | --- |
| [PROJECT_CHARTER](project/PROJECT_CHARTER.md) | Identity, scope, stakeholders, budget and deliverables |
| [SYSTEM_REQUIREMENTS](requirements/SYSTEM_REQUIREMENTS.md) | SIH expectations traced to capabilities and planned acceptance |
| [SYSTEM_ARCHITECTURE](architecture/SYSTEM_ARCHITECTURE.md) | Frozen system, software boundaries and provisional stack |
| [HARDWARE_STATUS](engineering/HARDWARE_STATUS.md) | Unbuilt hardware and required qualification |
| [SIMULATION_PLAN](testing/SIMULATION_PLAN.md) | Three engines, controls, scenarios and metrics |
| [WEBSITE_REQUIREMENTS](requirements/WEBSITE_REQUIREMENTS.md) | Roles and complete operational workflows |
| [DATA_DICTIONARY](architecture/DATA_DICTIONARY.md) | Proposed entities, provenance and unresolved schema decisions |
| [ENGINEERING_LIMITATIONS](engineering/ENGINEERING_LIMITATIONS.md) | Physical observability, model and claim boundaries |
| [DECISION_LOG](decisions/DECISION_LOG.md) | Frozen, provisional and pending decisions |
| [ROADMAP](project/ROADMAP.md) | M01–M10 scope and exit criteria |
| [EVIDENCE_REGISTER](testing/EVIDENCE_REGISTER.md) | Attributed history, current evidence and future proof |
| [ARTIFACT_POLICY](engineering/ARTIFACT_POLICY.md) | Large/generated/private artifact handling |
| [THREAT_MODEL](architecture/THREAT_MODEL.md) | Initial assets, trust boundaries and planned controls |

Research source claims in the master context are inherited, not independently reverified in M01. The original submitted six-slide deck and historic source/test packages are not included. Do not claim they were inspected or rerun.


## M02 detailed design — approved and merged

- [Product routes](architecture/PRODUCT_INFORMATION_ARCHITECTURE.md) and [role/action matrix](architecture/ROLE_PERMISSION_MATRIX.md).
- [UI system](../design/design-system/UI_UX_DESIGN_SYSTEM.md) and [page specifications / ten wireframes](../design/wireframes/PAGE_AND_WIREFRAME_SPECIFICATIONS.md).
- [Database](architecture/DATABASE_DESIGN.md), [ER source](architecture/m02-database-er.mmd), [provenance](architecture/DATA_CONTRACTS_AND_PROVENANCE.md).
- [API inventory](architecture/API_CONTRACTS.md) and canonical [OpenAPI3.1 JSON](architecture/openapi-design.json).
- [State machines](architecture/DOMAIN_STATE_MACHINES.md), [security](architecture/AUTH_SECURITY_AND_PRIVACY.md), [realtime/offline](architecture/REALTIME_OFFLINE_AND_NOTIFICATIONS.md).
- [Deployment/versions](deployment/DEPLOYMENT_AND_STACK_DECISIONS.md) and [future acceptance plan](testing/M02_ACCEPTANCE_AND_TEST_PLAN.md).

These are proposed implementation contracts, not a running application, executed migration or measured sensor result.

- [M03/M04 staged sequence](project/M03_M04_IMPLEMENTATION_SEQUENCE.md): original planning sequence; current implementation records supersede its historical status language.
- [Final M02 review validation](testing/M02_REVIEW_VALIDATION.md): independent OpenAPI tool/version/commands and design-checker mutation evidence.

M05: [executed simulation evidence, limitations and reproduction](testing/M05_SIMULATION_EVIDENCE_REPORT.md).

M08: [digital hardware engineering report](engineering/M08_DIGITAL_HARDWARE_REPORT.md), [hardware source index](../hardware/README.md), [estimated materials ledger](../hardware/bom/M08_BOM.md). Review package only; no physical validation.

M03: [backend implementation report](engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md), [runtime decisions](decisions/M03_RUNTIME_DECISIONS.md), [acceptance results](testing/M03_ACCEPTANCE_RESULTS.md), [PowerShell/Compose reproduction](../services/api/README.md) and [117-operation/57-table traceability](../data/schemas/m03-implementation-matrix.json). This historical M03 package is merged; execution-time reports remain historical. No public deployment or physical validation.

M03 and recovery PR #15 were subsequently approved and merged at main `e0122f5ee4146e49ae6113a1aa6a5ee444b25973`; issue #3 is closed. The original milestone reports retain their execution-time status.

M04: [authorized request](project/MILESTONE_04_REQUEST.md), [frontend implementation record](engineering/M04_FRONTEND_IMPLEMENTATION_REPORT.md), [execution ledger](testing/M04_EXECUTION_LEDGER.md), [local web guide](../apps/web/README.md), [route/API integration matrix](testing/M04_ROUTE_AND_API_MATRIX.md), [current capability data](../apps/web/src/lib/route-capabilities.json) and [visual QA gate](../design-qa.md). Owner merged PR #16; issue #4 is completed. Historical reports retain their execution-time status and accepted dependency/license limitations.

M07 contracts were owner-merged in PR #17 at `c3f785c4fa2974ec45e473786bca4ea8806e2c7a`. [M07-A implementation and acceptance](engineering/M07_A_IMPLEMENTATION.md) records the authorized service foundation. The [activation manifest](../data/schemas/m07a-implementation.json) distinguishes 70 implemented from 161 designed operations; visit access, preferences, scheduling, media and notifications stay disabled. M07-A was subsequently merged in PR #18; M07-B/C are also merged. Counts and disabled capabilities in that original report describe its execution-time baseline; use the current register for present scope. Public deployment remains disabled.
