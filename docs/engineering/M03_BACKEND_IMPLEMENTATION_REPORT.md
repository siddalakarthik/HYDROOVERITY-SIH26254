# M03 backend implementation report

Issue #3; branch `feature/m03-backend-foundation`; based on approved main `5f46c3834131196ee2d5c25a779438dd8b77539d`. Scope is the separately authorized [M03 request](../project/MILESTONE_03_REQUEST.md). M02/M05/M08 remain approved foundations. No M04, M06, M07, M09 or M10 work, public deployment, procurement or hardware trial is included. Owner review and merge remain required.

## Implemented behavior

The application in `services/api` is a real FastAPI application with synchronous SQLAlchemy Core/psycopg transactions against PostgreSQL/PostGIS. There is no SQLite fallback, fake account database or catch-all success handler. Explicit service modules own authentication, tenant access, administration, assets, complaints, incidents, work orders, repairs, evidence and verification. Parameterized repositories accept only static internal table identifiers. Static Alembic migrations are separate from runtime configuration; the runtime has neither ownership nor superuser/RLS-bypass privileges.

The canonical API target remains 117 operations. The [machine-readable matrix](../../data/schemas/m03-implementation-matrix.json) records method, route, permission, request/response schema, primary table, status and executed positive-response tests for every operation. The implemented subset is:

| Domain | Implemented |
| --- | ---: |
| Authentication | 8 |
| Current user | 5 |
| Public | 2 |
| Organization | 1 |
| Water zones | 4 |
| Pipeline assets: junctions and pipes | 8 |
| Evidence | 3 |
| Incidents | 6 |
| Work orders | 7 |
| Repairs | 2 |
| Verification | 2 |
| Complaints | 5 |
| Administration | 5 |
| **Total** | **58** |

**59 operations are DEFERRED.** Uploads/photos, intake/contact submissions, feedback, notification delivery, device/firmware/observation/acoustic endpoints, supply windows/access points, simulation jobs/outputs/evaluation, scientific algorithms, reporting exports and realtime/offline synchronization are not advertised as working. Deferred routes return ordinary route/method denial. Internal liveness/readiness and development-only implementation OpenAPI are infrastructure routes, excluded from canonical counts; the HTTPS proxy blocks `/internal`.

## Database and migration boundaries

Thirty of the canonical 57 application tables are migrated (PostGIS extension and Alembic metadata are additional infrastructure). The complete implemented/deferred table list is in the matrix. Thirteen foundation tables cover organizations, global users, memberships, roles, permissions, role/permission assignments, sessions, invitations, recovery tokens, audit logs, idempotency receipts and domain events. Seventeen operational tables cover zones, junctions, pipes, complaints/history, incidents/history/links/evidence, work orders/actions, repair/verification history and evidence/assessment links.

Same-tenant composite FKs, enum/value checks, positive finite lengths, geographic coordinate validation, unique normalized identity/tenant memberships, optimistic versions, immutable histories and runtime grants protect persistence. Future scientific/attachment FKs are guarded NULL until their real parents and tenant constraints exist. `m03_001` establishes the subset; `m03_002` adds stricter value constraints; `m03_003` rejects nonfinite lengths; `m03_004` retains private complaint review reasons. Downgrades preserve operational records; removing the foundation is refused, and removing populated private review history is refused. Tests exercise populated downgrade/upgrade and these guards. No migration drops an existing table to hide data loss.

RLS uses transaction-local organization context, cleared with transaction completion. Direct application-principal SQL is tested for cross-tenant read/write denial, FK rejection and history mutation denial. Global identity repositories necessarily cross organizations; membership discovery uses a restricted SECURITY DEFINER function with fixed search path and revoked PUBLIC execution. Tenant RLS protects tenant separation; citizen ownership, assignment and role decisions also require the service layer. An attacker able to execute arbitrary SQL as the application identity is outside the guarantee of actor-level RLS; this is defense in depth, not a claim that database access alone authenticates an HTTP user.

Junction/pipe geometry is WGS84. Pipe endpoints must match their referenced junctions and zone. PostGIS geography calculates geodesic geometry length in metres; surveyed length remains separate, and discrepancies require review. Moving a junction already referenced by a pipe is blocked. No unknown network topology, hydraulic condition or pipe property is inferred.

## Authentication and authorization

The eight auth operations are CSRF bootstrap, registration, email verification, login, logout, recovery request, password reset and invitation acceptance. Users have global normalized email identity and Argon2id password hashes (19 MiB, two iterations, one lane). Passwords and raw tokens are not stored in session/receipt tables. Opaque 256-bit session and action secrets use SHA256 verifiers. Sessions have 30-minute idle, 12-hour absolute and 10-minute privileged reauthentication limits; preauth expires after 10 minutes.

Cookies are `__Host-hydro_session`, Secure, HttpOnly, SameSite=Lax, Path=/ and no Domain. All POSTs, including anonymous auth flows, require exact Origin and synchronizer CSRF. All responses use no-store. Login rotates the session; logout cleans recognized sessions even when expired; reset consumes once and revokes all sessions. Concurrent reset/login cannot leave an old-password session. Registration grants only CITIZEN after verification; duplicate requests cannot change an existing password or staff grants. Recovery responses remain generic, with a 60-second cooldown and 30-minute single-use actions. Invitation acceptance requires the matching verified global identity, reads server-stored roles, rechecks issuer authority and membership status, and does not require an existing target membership. Invitation replay fails; session rotation preserves original expiry/reauth time. Lost-response recovery uses login/current memberships rather than replaying secrets.

ADMIN has explicit governance permissions and no inherited engineer/evaluator capability. Role changes, suspension and pending-grant invalidation revoke access immediately. The last active administrator is protected. Recent reauthentication is checked before privileged receipt replay. Citizens see only their own complaint projection and public updates; internal review reasons never appear in that projection. Technicians access only currently assigned work; reassignment also denies prior idempotency receipt replay. Nested references and current authority are checked before any replay or mutation.

Rate limits count failures and use daily HMAC keys, bounded memory, at most 24-hour retention and fail-closed capacity limits. Login/recovery enforce IP and account limits; registration, reset/verify/invite and general operations have their specified bounded scopes. This is a single API process development implementation. Multi-instance shared limits, external auth mail delivery and production operations require further work; configuration refuses public release.

Private development mail is delivered after database commit to a bounded directory outside Git, with no public retrieval route. Delivery failure remains generic and retry issues a new verifier; it does not undo committed identity history or expose a token in the response. On Windows it inherits the private parent ACL; Linux directories/files use restricted modes. No external emails were sent during acceptance.

## Transactions, retries and audit

Tenant business writes require UUID idempotency keys. Actor, tenant, HTTP method, canonical route, path parameters and canonical body form a fingerprint. Seven-day receipts commit atomically with the mutation, audit record and safe outbox event. PostgreSQL advisory/row locks serialize competing requests. Tests prove concurrent retries create one mutation, receipt and event; injected faults roll everything back. Changed fingerprints conflict; stale versions and nested/tenant IDs fail. Replay returns a current authorized projection, preserving revocation and reassignment, rather than a stale sensitive response cache. Authentication/global writes reject business idempotency headers and never cache secret-bearing responses.

Audit and domain event payloads use safe metadata and are append-only for the runtime. Governance reasons stay in the scoped admin audit projection; complaint review reasons stay private. Logs omit request bodies, query values, cookies, credentials and tokens. Citizen follow-ups retain their full 2,000-character contract limit. Manual assessments and evidence cannot fabricate sensor provenance or scientific confidence. There is no ordinary evaluation truth/seed route or table in this implementation.

## Executed operational example

Synthetic accounts in two organizations exercise the actual flow: citizen submits a private complaint; supervisor reviews and links a manual incident; supervisor creates and assigns a work order; the assigned technician accepts it, records work and submits a manual repair; a separate supervisor records `NOT_VERIFIABLE` with false comparability flags and an explicit limitation. The incident remains `NOT_VERIFIABLE`; work completion never resolves it automatically. Another organization, another citizen, a former assignee and the repair worker (even when also a supervisor) are denied inappropriate reads/writes. PASSED/FAILED verification is rejected while scientific comparison is unimplemented. Immutable history, safe public updates and linked evidence persist across an actual API process restart.

This sequence runs both in real PostgreSQL integration tests and through actual certificate-verified loopback HTTPS. These are synthetic operational software records, not measured hydraulic, acoustic or collector evidence. M05's unfavorable GUARD-5 results and M08's physical limitations are unchanged.

## Contract corrections requiring review

The implementation exposed four narrow M02 inconsistencies, recorded in the [runtime decision log](../decisions/M03_RUNTIME_DECISIONS.md): optional directory membership versions for governed edits; explicit immutable repair ETag 1; the public update projection's message limit matching the accepted 2,000-character follow-up; and a private nullable complaint review reason for unlinked complaints. Canonical design, migration, projection and focused tests agree. No new scientific field, route, role or hardware architecture is introduced.

## Reproduction, evidence and limits

See the [PowerShell/Compose guide](../../services/api/README.md) and [acceptance ledger](../testing/M03_ACCEPTANCE_RESULTS.md) for exact commands, observed environments and CI status. Direct dependencies and resolved transitive versions are locked; Ruff is isolated as a quality dependency. Licenses are recorded in the decision log. Linux containers use a separate nonroot runtime and root-only operator files. The native Windows processes share the local operator's OS identity and are intended for private development only.

M04 can consume these 58 real routes and their session/CSRF, ETag, UUID retry, pagination and permission contracts. M06 still needs explicit simulation ingestion, job/stream execution, scientific provenance and evaluator isolation. M07 still needs photo handling, richer maintenance/offline/reporting integration and scientifically comparable verification; M03's minimal operational path does not complete that milestone. External delivery, durable background consumers, production backup/restore drills, shared rate limiting, load testing and independent security assessment remain untested or deferred. No production-readiness claim follows from passing CI.
