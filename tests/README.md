# Executable validation

Tests are implemented alongside the source they exercise. Passing a subset does not satisfy every original M02 acceptance criterion. The [current register](../docs/testing/PRE_M10_COMPLETION_REGISTER.md) retains the original 40-case denominator and the [M09 report](../docs/testing/M09_FULL_SYSTEM_ACCEPTANCE.md) records executed evidence and limits.

| Location | Executed responsibility |
| --- | --- |
| [unit](unit) | M05 numerical logic, M06 reproduction, M08 source/package consistency |
| [API tests](../services/api/tests) | Real PostgreSQL authentication, tenancy/RLS, workflow, concurrency, scheduling and communications |
| [API traceability tests](../services/api/traceability_tests) | Executed acceptance/source compatibility and repeat-run evidence |
| [Browser scenarios](../apps/web/browser) | Real backend workflows, role denials, desktop/mobile, accessible states and inert hostile text |
| [Frontend package](../apps/web/package.json) | Unit tests, typecheck, lint, formatting and production build |
| [Design checks](../scripts/README.md) | M02/M07 schema/API/permission/route consistency and rejected design mutations |

Run from repository root using the appropriate isolated Python environment, for example `python -m pytest tests/unit/test_m05.py -q` or `python -m unittest discover -s tests/unit -p 'test_m08*.py' -v`. Real database tests require the exactly confirmed disposable database and private operator/runtime configuration described in the [API guide](../services/api/README.md). Do not run them against resident or owner development data.

The four required [CI jobs](../.github/workflows/repository-integrity.yml) also execute real HTTPS restart/recovery and generated CAD/figure checks. `integration/`, `e2e/` and `security/` retain organizational guides; they are not evidence that every planned suite exists. Native browser zoom, full screen-reader certification, long soak and physical/field validation retain explicit limits.
