# Documentation index

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

- [M03/M04 staged sequence](project/M03_M04_IMPLEMENTATION_SEQUENCE.md): original planning sequence; M03's current implementation is documented below. M04 remains unstarted.
- [Final M02 review validation](testing/M02_REVIEW_VALIDATION.md): independent OpenAPI tool/version/commands and design-checker mutation evidence.

M05: [executed simulation evidence, limitations and reproduction](testing/M05_SIMULATION_EVIDENCE_REPORT.md).

M08: [digital hardware engineering report](engineering/M08_DIGITAL_HARDWARE_REPORT.md), [hardware source index](../hardware/README.md), [estimated materials ledger](../hardware/bom/M08_BOM.md). Review package only; no physical validation.

M03: [backend implementation report](engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md), [runtime decisions](decisions/M03_RUNTIME_DECISIONS.md), [acceptance results](testing/M03_ACCEPTANCE_RESULTS.md), [PowerShell/Compose reproduction](../services/api/README.md) and [117-operation/57-table traceability](../data/schemas/m03-implementation-matrix.json). Published for owner review; not merged automatically. No public deployment or physical validation.
