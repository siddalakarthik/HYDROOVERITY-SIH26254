# M07-C communications and feedback acceptance

## Scope

Base main `bb86029cac32e3ddb8a476855b99cf512f023482`; merged PR #20 and main push run [40114320240](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40114320240) independently verified successful for repository-integrity, m03-backend, m04-frontend and m08-cad-and-figures. Reviewed M07-B source is an ancestor. The isolated branch is `feature/m07-c-communications-feedback`.

Eight activated operations: N40–N42, two existing M02 notification operations and three existing M02 feedback operations. **111 total = 103 preserved + 8 M07-C**. Six additive tables (`notification_preferences`, `notifications`, `notification_delivery_attempts`, `background_jobs`, `feedback_items`, `feedback_events`); **51 total**, checked against the actual migrated database. One additive revision, `m07_c_001`. The 161-operation M07 candidate and 168-operation composed scientific design are historical designs; unimplemented designs are not runtime capabilities.

The runtime overlay adds safe category/resource navigation and feedback description to previously unimplemented DTOs. All 103 prior operation definitions and their component schemas are pinned unchanged in `data/schemas/m07c-implementation.json`. Historical M03 matrix classifications remain unchanged; only executed positive test references are refreshed. Historical source manifests remain intact and current source extensions explicitly record baseline/current checksums.

## Delivered behavior and boundaries

- Authenticated inbox with pagination, read receipts, refresh and versioned preferences. Membership provisioning/backfill starts optional alerts disabled with no selected categories; GET does not create records. Asia/Kolkata quiet hours defer optional alerts without changing authoritative case/appointment visibility.
- Atomic business event plus minimal fan-out intent; one durable PostgreSQL queue. Unique event/recipient/template/channel identities, token-fenced leases, competing-claim protection, current recipient permissions/parent ACL/version checks and safe templates. Old pending snapshots are suppressed after subsequent resource changes. An old delivered link is filtered when assignment/access is lost; opening the record independently reauthorizes.
- Delivery means a committed in-app inbox row. Read receipts mean an explicit current-recipient action. Neither proves human attention, attendance or scientific effectiveness.
- Supervisor case delivery audit contains only category/channel/state/count/times/safe error. ADMIN has no automatic resident-case access.
- Own general feedback, owned closed/cancelled service experience ratings, feedback history and current-role/versioned review. Public explanations are separate from stored private severity/assignment metadata. Those private fields are not exposed by the current feedback DTO. No external issue is created. A rating changes no incident, work, repair or scientific verification state.
- Existing workspace navigation/components, mobile layouts, loading/error/refresh behavior and API responses are reused. Images, external delivery and offline storage remain disabled.

## Worker operation

Run from the repository root with the existing isolated backend environment and private loopback runtime configuration:

```text
python services/api/tools/notification_worker.py --runtime-config <absolute-private-runtime.json> --organization <utility-uuid> --supervisor-user <authorized-supervisor-user-uuid>
```

The configured principal must be a currently active supervisor in that utility. The worker uses the non-owner `hydro_app` identity and RLS; no new SECURITY DEFINER function or cross-utility bypass is added. It holds the existing per-utility advisory lock before current membership/role locks. One process handles one explicitly configured utility; it stops if its principal is revoked. The technical 60-second lease and two-second idle poll do not define an operator SLA.

No retry delays are invented. Without `--retry-policy`, the first failed delivery/recovered lease becomes FAILED with `RETRY_POLICY_UNCONFIGURED`. Reviewed private configuration may contain exactly `{"reference":"<reviewed operator decision>","delay_seconds":[<positive seconds>,<positive seconds>]}`. The hard cap is three total attempts including the first. Synthetic tests supply clearly labeled test-only delays; these are not shipped municipal defaults. Quiet-hour deferral consumes no delivery attempt. Database outage leaves the last durable lease/state, with no false delivery claim; restore the database and restart the same scoped worker. No automatic retention/purge process is introduced.

## Reproduction

Use the existing locked environments/dependencies. All credentials and generated acceptance evidence stay outside the checkout. PostgreSQL acceptance tools require explicit confirmation of a `hydro_disposable_*` database and reset that synthetic database only.

```text
python -m alembic -c services/api/alembic.ini upgrade head
python services/api/tools/verify_backend.py --operator-config <private-operator.json> --runtime-config <private-runtime.json> --confirm-disposable-database <hydro_disposable_name> --evidence-directory <absolute-private-evidence>
python scripts/check_m07c.py
python scripts/check_m07b.py
python scripts/check_m06.py
python scripts/check_m07a_implementation.py
python scripts/check_m07_design.py
python scripts/check_repository.py
git diff --check
```

For the frontend, run the existing `apps/web/tools/prepare_browser_fixture.py` with its private operator/runtime inputs and an explicitly marked disposable browser database. This creates synthetic identities, API-authored service/assignment fixtures and a separate test certificate. Set `HYDRO_M04_BROWSER_FIXTURE` and `HYDRO_M04_SCREENSHOTS` to private absolute paths; optional local `HYDRO_BROWSER_PORT` selects the isolated proxy port. Start the existing API/proxy/frontend and the utility-scoped notification worker using `comms_supervisor_user` from the private fixture. In `apps/web`, run `pnpm run contracts`, `pnpm run typecheck`, `pnpm run lint`, `pnpm run format:check`, `pnpm run test`, `pnpm run build`, and `pnpm run test:browser`.

The browser runner preserves the existing login-IP throttle and runs original M04, M07-A, M06 and M07-B suites before M07-C. Tests use the existing single-certificate SPKI test allowlist with `ignoreHTTPSErrors:false`; no machine/user certificate trust is installed or verification globally disabled. The network-outage scenario deliberately aborts one inbox request; functional data and all mutations use real PostgreSQL/API responses. Screenshots use synthetic data only. CI uploads four `M07C-*.png` images for 14 days; the PR will link the verified artifact after upload.

## Executed evidence at this checkpoint

- 84 PostgreSQL tests passed: existing application regressions plus 11 M07-C tests; zero failures/errors/skips. All eight new operations have executed positive response conformance. Actual empty downgrade/upgrade and populated M07-C downgrade refusal passed; 51 tables confirmed.
- 19 existing frontend unit tests, TypeScript, lint and production build passed. Full final browser/CI results are tracked in the review PR, not asserted prematurely here.
- Independent OpenAPI 3.1 validation passed using the existing M02 validator environment. M02/M07 canonical design checks and negative checker mutations passed. 39 unchanged M05/M06 numerical/reproduction tests and 13 M08 focused checks passed.

## Remaining owner-controlled gates

D7 scanner choice/signature policy, isolated decoding/re-encoding resource bounds, licensing and private storage/cleanup/disclosure controls have no independent activation approval. All six attachment routes remain unregistered; no upload UI/storage/CLEAN state is offered. D6 encryption/key custody/consent/disclosure review keeps N10–N12 disabled. D8 retry-delay configuration is absent by default. D10 retention, erasure/holds/backup purge, consent and operator commitments still require review before live release. External email/SMS/push, offline synchronization and public deployment remain disabled. Existing dependency/license limitations remain. No real municipal operating data, physical sensor validation or photo/rating-based repair verification is claimed. M05 unfavorable GUARD-5 results, M06 provenance/truth separation and M08 digital-only limitations remain unchanged.
