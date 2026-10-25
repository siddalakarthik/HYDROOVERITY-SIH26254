# Service implementation

The [FastAPI application](api/README.md) currently contains **111 implemented operations and 51 migrated application tables**. PostgreSQL/PostGIS persists identity, tenancy, complaints, incidents, work, service requests, scheduling, synthetic scientific observations, in-app notifications and feedback. It enforces RLS, current role/ownership checks, CSRF, version preconditions, idempotency and audit history.

| Responsibility | Current implementation | Remaining boundary |
| --- | --- | --- |
| API | [Domain services](api/hydro/services), [migrations](api/migrations) and [tests](api/tests) | Public/production activation remains disabled |
| Scientific ingestion | [M06 evidence](../docs/testing/M06_SCIENTIFIC_INTEGRATION.md), observation-only synthetic replay | No physically validated device adapter or ordinary-client evaluator truth |
| Notifications | [Durable in-app worker](api/hydro/notification_worker.py), [M07-C acceptance](../docs/testing/M07_C_COMMUNICATIONS_ACCEPTANCE.md) | No external email/SMS/push or secure-image activation |
| Scheduling | [M07-B acceptance](../docs/testing/M07_B_SCHEDULING_ACCEPTANCE.md) | Requires actual authorized utility policy, enrollment, skills, areas and shifts |

These responsibilities do not imply separate microservices. Reuse the operator/runtime separation and disposable-database confirmation in the API guide. Never reset an unrelated database or expose operator credentials to the API process. Historical reports retain their original counts; [M09 acceptance](../docs/testing/M09_FULL_SYSTEM_ACCEPTANCE.md) and the [completion register](../docs/testing/PRE_M10_COMPLETION_REGISTER.md) describe the combined baseline.
