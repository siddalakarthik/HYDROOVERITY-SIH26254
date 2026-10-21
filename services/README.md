# Python service responsibilities

M03 implements the private [API foundation](api/README.md). Ingestion and external notifications remain deferred. Executed checks and limitations are in the [M03 acceptance report](../docs/testing/M03_ACCEPTANCE_RESULTS.md).

| Folder | Responsibility |
| --- | --- |
| `api/` | Domain API, auth, persistence and audit. |
| `ingestion/` | Versioned observation validation and future adapters; synthetic provenance explicit. |
| `notifications/` | Future scoped delivery, retry and outcome tracking. |

Follow [AGENTS.md](../AGENTS.md) and the [documentation index](../docs/README.md) before development.

These logical folders do not mandate separate deployable microservices. M03 uses one API process, private PostgreSQL/PostGIS and an HTTPS proxy.
