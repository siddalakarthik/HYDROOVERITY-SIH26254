# M03 executed acceptance results

Issue #3; private development software evidence, 21 October 2026. All fixture identities and operational records are SYNTHETIC_INTEGRATION_ONLY. Physical trials: **0**; field trials: **0**. Owner review and merge are pending. M05/M08 scientific results and limitations are unchanged.

## Native environment actually exercised

Windows, Python 3.12.14, FastAPI 0.156.1, Pydantic 2.14.1, SQLAlchemy 2.1.5 (supported pure-Python build), Alembic 1.20.0, psycopg 3.3.6, Argon2 25.1.0, PostgreSQL 17.11 and PostGIS 3.6.2. HTTPS uses the included bounded Python loopback reverse proxy and an explicitly trusted temporary localhost certificate. Full versions are in services/api/requirements-lock.txt; direct-license/runtime decisions are recorded separately.

Official EDB PostgreSQL archive: complete ZIP CRC verified; SHA256 `80379b2c04d51c30225532e0ae04509899141e9957ed096fe749d7fd9df8f82f`. PostGIS extension/DLLs came from the official OSGeo bundle. Migration owner and runtime are separate non-superuser identities; runtime is nonowner and NOBYPASSRLS. Local port 55432 is loopback-only. Docker is absent on this host; native results do not establish container execution.

## Observed validation

| Check | Status and executed evidence |
| --- | --- |
| Backend acceptance against real PostgreSQL/PostGIS | PASS: **45 tests**, 0 failures, 0 errors, 0 skips |
| Canonical positive response conformance | PASS: all **58** implemented operations; requests also use canonical validation |
| Traceability | PASS: 117 = 58 CODE_TESTED + 59 DEFERRED; 30/57 application tables migrated |
| Migrations | PASS: fresh upgrade, populated downgrade/upgrade, head m03_004, guarded destructive downgrade refusal |
| RLS and integrity | PASS: direct runtime SQL cross-tenant read/write denial, transaction-local pool context, composite FKs, append-only audit/history |
| Auth | PASS: Origin/CSRF/no-store/cookie flags; duplicate/concurrent registration; single-use tokens; reset/login race; recovery cooldown; session rotation/expiry/revocation; matching invitations and pending-grant invalidation |
| Governance | PASS: ADMIN has no engineer/evaluator inheritance; exact grants, reauthentication, last administrator, version and immediate suspension/revocation |
| Operational workflow | PASS: complaint -> review -> incident -> assignment -> repair -> independent NOT_VERIFIABLE; tenant/owner/assignment/self-review denial; actual persistent restart |
| Idempotency | PASS: concurrent one-mutation/one-receipt/one-event, conflicting fingerprint, current authorization replay, fault rollback, expiry |
| Private mail and logs | PASS: bounded private adapter, generic delivery failure, no token HTTP retrieval, no credential/body/cookie/token log values |
| Actual loopback HTTPS example | PASS: verified TLS, complete persisted workflow, separate API/proxy processes, actual API restart; scripts stop only their own children |
| Database outage probes | PASS: readiness 503 in 3.001 s; liveness 200; recovered readiness 200 |
| Argon2id local timing smoke | PASS: 7 hash-plus-verify samples; median 84.176 ms, maximum 89.756 ms. Not a load/performance guarantee |
| Independent canonical OpenAPI | PASS: openapi-spec-validator 0.9.0; 154 component metaschemas |
| Independent implemented OpenAPI | PASS: same isolated validator, implemented paths/components only |
| M02 design consistency | PASS: 57 tables, 117 operations, 46 routes, ten wireframes; 0 errors |
| M02 checker regression | PASS: 2 unittest methods including 33 deliberate invalid-design mutations |
| M05 regression | PASS: 38 numerical tests; earlier M03 smoke profile also passed, eight figures generated. No M05 source/config/result changes |
| M08 regression | PASS: 13 focused tests and artifact contract check; estimate INR59,870/headroom INR130 retained. Native ERC/physical tests remain unperformed |
| Dependency compatibility | PASS: pip check |
| Source quality | PASS: Ruff check and format check |
| Repository integrity / whitespace | PASS after final-newline normalization; repeat at publication |
| Docker/Caddy execution | PASS in actual Ubuntu CI: Compose build/start, PostGIS migrations, nonroot API/operator-file denial, verified Caddy TLS and private probe denial. NOT TESTED on this Windows host |
| Remote branch/PR/CI | PASS: PR #14, implementation-head run linked below; all three jobs succeeded |

The final local backend run took 54.60 seconds. Its source digest was `dfe4fb156e15dcc5b198a122783a25983ba1553360646f1da2afe2ec0d5ef38b`; the HEAD at execution was the earlier foundation checkpoint `7049cd20e34e19de4c4e3a3dcf58c5c085723be1` with the completed working tree under test. CI records the exact published head/merge candidate separately. Do not equate that earlier checkpoint alone with the tested full implementation.

Private local evidence is under the existing workspace's `work/m03-acceptance` and `work/m03-private/https-demo`, outside Git. Only sanitized summary JSON files are eligible for the 14-day CI artifact. Database DSNs, passwords, action tokens, cookies, private mail, certificates/keys and raw scientific truth are never included. The operation matrix contains test names and schemas, no fixture IDs or personal data.

One initial M05 regression invocation used the sandbox default temporary directory: 8 tests failed with file-access errors and 30 passed. Rerunning with the dedicated writable TEMP/TMP directory passed all 38; no scientific source or parameter was changed. An initial ad hoc Windows outage probe helper failed an assertion; a separately bounded rerun completed successfully and is the accepted outage result above. A missing final newline in the copied M03 request was corrected before repository validation passed. These intermediate failures are not presented as successful runs.

## Deliberate limits

DEFERRED: the 59 unregistered operations, uploads/photos, external mail, scientific verification/ingestion, evaluation truth, simulation jobs, exports, durable background delivery, multi-instance shared limits and subsequent milestones. NOT TESTED: public deployment, production backup/restore drill, load/soak tests, independent penetration assessment and physical hardware. No security-critical acceptance failure is concealed by these labels. The application refuses production/public configuration.

The minimal workflow accepts only manual source data and NOT_VERIFIABLE verification; it does not attest measured comparability, leak detection accuracy or repair success. Windows processes share one local OS identity; Linux container credential ownership is tested separately in CI. RLS is tenant defense in depth, with ownership/assignment enforced in services. See the [implementation report](../engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md) and [reproduction guide](../../services/api/README.md).

## Published implementation evidence

[PR #14](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/pull/14) is open for owner review; issue #3 remains open. Implementation head `18f7a2a3ca27943132d1e4c927b06d09d5764daa` passed [workflow 39545900642](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39545900642): **repository-integrity**, **m03-backend**, **m08-cad-and-figures**, all SUCCESS. CI tested the PR merge candidate `af18a0b806773d2df36e9f41b50a930069e3ed85`; this does not mean main was merged. CI backend source SHA256: `bd6448bf5a7be751a86781d2e5780c7aa6b30a6e4775beb351cad36d34f5b69b`.

Actual Linux container acceptance: 45 tests, 0 failures/errors/skips; all 58 positive operation projections; independent runtime OpenAPI; full HTTPS workflow and actual API restart; verified Caddy certificate/cookie/Origin boundary; nonroot runtime cannot read owner configuration. Existing M02/M05 checks and full M08 CAD/figure regeneration/package verification also passed. The M03 artifact contains exactly two sanitized JSON summaries: no mail, tokens, credentials, certificates, database exports or scientific truth.

[Download sanitized M03 evidence](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39545900642/artifacts/12321752138), retained for 14 days (expires 4 November 2026). The downloaded ZIP was opened and checked: SHA256 `42c0905111ca6b89a5b741a7d46eced4b62768f80662a714c6f57013e43112b6`, matching GitHub's digest. A convenient local copy is in the existing workspace at `work/m03-ci-39545900642/evidence.zip`, outside Git. [M08 presentation artifact](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39545900642/artifacts/12320629358) was also confirmed uploaded and unexpired.

Additional native reproduction check: the documented operator CLI reused explicitly bound restricted roles, created a new disposable database, applied the full fresh m03_001 -> m03_004 chain and executed the private bootstrap CLI twice. The second bootstrap left the existing password unchanged. No privileged DSN or password was printed.

No unresolved merge conflict or security-critical acceptance failure remains. Native Windows Docker, external delivery, shared-rate infrastructure and the deferred/untested limits above remain unchanged. This evidence update changes documentation only; the final PR head's CI is verified separately before handoff.
