# Future Python service responsibilities

Status: planned; M01 creates organization only. No implementation or validation is implied.

| Folder | Responsibility |
| --- | --- |
| `api/` | Domain API, auth, persistence and audit. |
| `ingestion/` | Versioned observation validation and future adapters; synthetic provenance explicit. |
| `notifications/` | Future scoped delivery, retry and outcome tracking. |

Follow [AGENTS.md](../AGENTS.md) and the [documentation index](../docs/README.md) before development.

These logical folders do not mandate separate deployable microservices. M02 will settle deployment boundaries.
