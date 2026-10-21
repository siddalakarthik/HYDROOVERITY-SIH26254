# M03 acceptance results — in progress

Issue #3. These are executed software checks against explicitly synthetic disposable data. M03 is not complete or production certified. Hardware and field validation remain unestablished.

## Foundation checkpoint

Executed 21 October 2026 on Windows, Python 3.12.14, PostgreSQL 17.11 and PostGIS 3.6.2. Separate `hydro_migrator` owner and restricted `hydro_app` runtime; private loopback port 55432. The official PostgreSQL archive passed complete ZIP CRC validation; SHA256 `80379b2c04d51c30225532e0ae04509899141e9957ed096fe749d7fd9df8f82f`. Core PostGIS DLLs and extension SQL came from the official OSGeo bundle. Native execution only; Docker is absent.

| Check | Actual result |
| --- | --- |
| Fresh isolated Python environment, resolved dependency lock and pip compatibility | PASS |
| Native PostgreSQL/PostGIS connection and extension creation | PASS |
| Alembic fresh upgrade to m03_001 | PASS |
| Non-owner/NOBYPASSRLS runtime, database/migration readiness | PASS |
| Direct SQL A/B RLS denial and transaction-local context reset | PASS |
| Cross-tenant composite FK rejection and runtime audit mutation denial | PASS |
| Foundation pytest snapshot | PASS: 3 tests |
| Repository integrity and Git whitespace | PASS |
| Docker/container execution | NOT TESTED: unavailable on this host |
| Full authentication, operational workflows, migration recovery and CI | NOT TESTED at this checkpoint; implementation continues |

The working tree also passed two initial authentication smoke tests before this foundation snapshot: secure preauth/CSRF/anonymous denial and real administrator login/no engineer inheritance. Their complete source and broader acceptance remain the next checkpoint.

Disposable reset requires matching `HYDRO_TEST_DATABASE_CONFIRM` and a database name beginning `hydro_disposable_`; test fixtures refuse unknown databases. Database credentials and private development mail are outside Git.
