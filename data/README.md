# Data contracts and safe examples

This folder contains reviewed versioned schema/catalogue files, implementation inventories and explicit source-revision manifests. Historical M03/M07/M09 inventories retain their execution-time scope; the [current completion register](../docs/testing/PRE_M10_COMPLETION_REGISTER.md) and [generated implemented API](../apps/web/contracts/implemented.openapi.json) identify runtime availability.

| Folder | Responsibility |
| --- | --- |
| `demo/` | Explicitly synthetic, privacy-safe demonstration fixtures; no implied field validation. |
| `schemas/` | Versioned contracts, provenance and compatibility/implementation catalogues. A proposed contract is not an implemented endpoint. |
| `samples/` | Small synthetic examples; no actual citizen or field data. |

Restricted evaluation truth, generator seeds, credentials, private raw acceptance output and database files stay outside ordinary public/dashboard artifacts and Git. The sealed evaluator boundary remains incomplete. Follow [AGENTS.md](../AGENTS.md) and the [artifact policy](../docs/engineering/ARTIFACT_POLICY.md).
