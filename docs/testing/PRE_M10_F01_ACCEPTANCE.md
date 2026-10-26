# Pre-M10 F01: complaint notification acceptance

Legacy complaint creation, review and follow-up now enqueue minimal, deduplicated complaint targets in the existing transactional in-app queue. They do not create service requests or incidents. Residents explicitly opt into `COMPLAINT_PROGRESS`; existing preferences and the default opt-out remain unchanged. Generic messages link to the currently authorized complaint timeline.

The worker checks current recipient membership, permission, complaint ownership and queued version. Inbox listing and read-receipt replay recheck current authorization. Read and delivered states remain distinct. Existing three-attempt behavior, CSRF, idempotency, RLS, organization transaction locks and deployment gates remain intact.

## Compatibility and migration

- Runtime remains **111 operations and 51 application tables**. Three notification schema enums gain one category; preference maximum category count increases from four to five. The complete previous OpenAPI is reconstructed and compared with its frozen digest, rejecting unrelated changes.
- Additive migration `pre_m10_001` follows `m07_c_001`, widening only existing notification resource/category checks. It never enrolls existing residents automatically.
- Downgrade acquires exclusive locks and refuses when complaint notification preferences, queued targets or notification records exist. It never deletes consent, receipts or history to force rollback.
- Historical M02/M07 contracts and M09 reports stay unchanged. The exact 18-file source amendment is separately pinned; scientific source is outside its allowlist.

## Executed local validation, 2026-10-25

- Thirteen focused real-PostgreSQL cases passed, including duplicate submission/body conflict, replay, worker contention, default opt-out, stale versions, tenant/owner isolation, session/membership/permission revocation, atomic audit rollback, queued ownership changes, clean migration roundtrip, populated downgrade refusal and preservation of prior service notification history.
- The existing backend suite initially produced 83 passes and one outdated downgrade-error assertion: the new data-preservation guard is reached before the older forward-only guard. The assertion now names the exact new refusal and still checks the unchanged migration head. It passed alongside all thirteen focused cases (**14 passed**).
- Nineteen frontend unit tests, TypeScript, lint and production build passed. Repository integrity, M02/M07 design, M07-A/B/C, M06, M09 source boundaries and seven baseline amendment regressions passed.
- The added real browser scenario opts in, submits a complaint, waits for the actual worker, opens the owned report from the inbox and checks mobile reflow/accessibility. Execution and all four final CI gates remain required; no browser result is claimed here before execution.

## Reproduction and evidence

Use the existing isolated backend dependencies and operator-generated disposable database configuration. `services/api/tools/verify_prem10_f01.py` accepts the same `--operator-config`, `--runtime-config`, `--confirm-disposable-database` and `--evidence-directory` arguments as the backend acceptance runner. The database must start with `hydro_disposable_`, and evidence must stay outside the repository. Run after upgrading to the current head. It executes `services/api/tests/prem10_complaint_acceptance.py` explicitly; this file is separate from historical test totals.

The backend CI job runs this tool and uploads only its sanitized summary. The frontend CI job executes the existing communications workflow with the additional real complaint scenario and uploads `PREM10-F01-complaint-inbox-mobile.png`. Both artifacts retain evidence for fourteen days. No credentials, resident data or scientific truth are published.

The original F01 status remains BLOCKED pending final reviewed execution. All physical, media, offline, external delivery, privacy and public deployment limitations remain applicable.

## Integration update, 2026-10-26

All 84 existing backend tests passed in the final local rerun. The standalone runner passed all 13 focused cases and produced its sanitized summary. PR25 initial CI passed backend, repository/scientific and CAD jobs. The new browser assertion counted rows immediately after Refresh had cleared them for loading; it now waits for the real successful inbox response and completed render before counting, without extending the timeout or changing application behavior. Exact-head CI is required again.

Merged green main `15cd3a10e25b9d78ab154c93ee8b19f42367171e` into this branch using a normal merge. Both the repository-media check and F01 checks remain in CI. Main's four jobs passed in run 40222558826. Source manifests retain the exact original-to-current chain; the workflow revision includes the reviewed presentation check.

CI run 40260564424 exposed runner drift: ubuntu-latest selected Python 3.14, for which frozen wntr==1.4.0 has no binary wheel. Repository integrity now uses ubuntu-24.04 and explicit python3.12 virtual environments, preserving every scientific dependency and result. This is environment reproducibility repair, not a scientific model change.
