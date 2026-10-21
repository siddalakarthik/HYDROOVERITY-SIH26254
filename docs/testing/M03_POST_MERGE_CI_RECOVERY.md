# M03 post-merge traceability recovery

Scope: issue #3, merged PR #14, failed main [run 39547948759](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39547948759). Correction branch: `fix/m03-post-merge-traceability`, isolated from main `cb7e9bd1e0bcb2be5489b15342ce18606b2382e4`. Do not merge this correction or close issue #3 without owner review. No application handler, permission, database constraint, migration, M05 parameter/result or M08 hardware source changes.

## Observed root cause

The checked-in matrix stores every test that happened to receive a 2xx response. `test_reset_login_race_never_leaves_old_password_session` deliberately permits the racing old-password login to return either 200 (login committed first, then reset revokes it) or 401 (reset committed first). Both are correct. The collector's `200 <= status < 300` condition adds an authentication_post_auth_login reference only in the first ordering. Exact matrix equality therefore depends on a permitted concurrent outcome.

Two independent, ordinary clean-checkout runs passed all 45 tests and reproduced the committed mapping. A third full 45-test diagnostic run delayed only the real reset request by 300 ms in that one test. All 45 tests and all 58 operation projections still passed, but the unchanged checker reproduced `Implementation matrix drift`. All three runs used backend source SHA256 `bd6448bf5a7be751a86781d2e5780c7aa6b30a6e4775beb351cad36d34f5b69b`. The observed diff was exactly:

```json
{
  "classification": "POSITIVE_RESPONSE_EVIDENCE",
  "operation_id": "authentication_post_auth_login",
  "added_test": "services/api/tests/test_auth.py::test_reset_login_race_never_leaves_old_password_session",
  "removed_tests": [],
  "changed_operation_metadata": [],
  "changed_counts": {},
  "changed_table_statuses": []
}
```

The controlled scheduling probe did not fabricate responses, change credentials/results, modify source, or relax assertions. It delayed one actual HTTP request while running the original acceptance procedure. The accepted race outcomes and subsequent old-session denial were unchanged. Its script and full generated evidence are retained outside Git in the existing workspace under `work/m03-recovery`; the safe diff above is sufficient to review the changed mapping.

PR and merged-main trees were identical. The PR happened to produce the mapping already in the matrix; another legal scheduling outcome can produce the extra reference. This is a reproducibility defect, not evidence of a failed backend security test. The failed historical CI did not upload its runtime mapping, so that exact historical mapping cannot be recovered. The diagnosis is supported by reproducing the same assertion under the identical source hash and isolating one scheduling-sensitive reference.

`PYTEST_CURRENT_TEST` supplies the same test node ID in both reproduced outcomes; its string did not change. These tests join their concurrent requests before the test returns, and pytest runs the test functions sequentially. The demonstrated instability is the successful-response condition, not an observed cross-test identity leak. The collector remains the single runtime source of mappings and now also records actual collected node IDs so evidence cannot name an uncollected test.

## Smallest behavioral correction

Preserve the free-running reset/login race, its 200-or-401 assertion, and the final denial of the old session. Then require login with the replacement password to succeed. This strengthens the password-reset test and guarantees an actual positive login response from that test in either ordering. Regenerate the matrix only from the corrected, successful 45-test run. The committed matrix changes by one added test reference; all 117 operations, permissions, schemas, classifications and table mappings remain unchanged.

The checker retains strict equality. It now rejects missing/unknown/deferred positive operation IDs, missing/nonexistent/uncollected test references, duplicate references, invalid/failed/skipped evidence, fewer than 45 accepted tests, and wrong counts/classifications. Actual collection metadata is checked against executable test functions. Metadata, count, table, evidence-reference and ordering differences produce explicit safe diagnostics. No secrets, request bodies, personal data, fixture IDs or scientific truth enter the diff.

## Reproduction and negative regressions

Run from the repository root with the existing isolated backend interpreter. Private operator/runtime files and all generated evidence remain outside Git. `verify_backend.py` resets only the explicitly confirmed disposable database.

```powershell
# Repeat the backend guide's verify_backend.py command with separate directories:
# --evidence-directory <private>/evidence and <private>/evidence-repeat
& $py services/api/tools/traceability.py --check --evidence "$private/evidence/acceptance-summary.json"
& $py services/api/tools/traceability.py --check --evidence "$private/evidence-repeat/acceptance-summary.json"
& $py -m pytest services/api/traceability_tests -q --acceptance-evidence "$private/evidence/acceptance-summary.json" --acceptance-evidence "$private/evidence-repeat/acceptance-summary.json"
# Read-only diagnosis of retained older evidence; does not certify or rewrite it:
& $py services/api/tools/traceability.py --diagnose --evidence "$private/older-evidence/acceptance-summary.json"
```

Regression fixtures load two actual independently executed acceptance files; they do not construct invented passing endpoint coverage. Negative cases deliberately mutate copies and must be rejected. They cover stable regeneration/order normalization, repeated-run equality, missing/unknown evidence, wrong permission/status/table, table removal/duplication, invalid or failed acceptance, unexecuted references, canonical API drift, count/order drift and the exact observed evidence-only difference.

CI retains all original design/simulation/CAD jobs, runs the original 45 backend tests twice in independent pytest processes with per-test database resets, checks both outputs, executes the targeted negative regressions, then continues Ruff, dependency compatibility, independent runtime OpenAPI, real HTTPS/process restart and Caddy cookie/TLS/private-probe checks. The 14-day M03 artifact now contains three sanitized summaries: both acceptance runs and the HTTPS workflow. It contains no private mail, credentials, keys, database export or scientific truth.

Executed final counts, independent-run equality and observed PR CI/artifact conclusions are recorded in the PR and final engineering handoff. Native Windows Docker remains unavailable; actual Linux Compose/Caddy execution must pass in PR CI. No rerun alone substitutes for this fix, and no later milestone is started.

## Executed local validation, 21 October 2026

Corrected run 1: 45 passed in 61.27 seconds. Corrected run 2: 45 passed in 58.93 seconds. Both have zero failures/errors/skips, all 58 implemented projections and byte-equivalent operation-to-test mappings. Both strict traceability checks passed. The separate targeted suite passed all 37 tests, including the negative rejection cases; its valid inputs were those two actual acceptance outputs.

M02 consistency passed (57 tables/117 operations/46 routes/ten wireframes); its two checker test methods and 33 mutations passed. Independent canonical OpenAPI passed all 154 component metaschemas, and independent implemented OpenAPI passed. M05 passed 38 numerical tests. M08 passed 13 focused tests, regenerated 25 CAD parts with STEP round trips and no detected interference pairs, regenerated seven PNG/SVG plates and verified its package/checksums. CAD remains digital-only, native KiCad ERC remains unexecuted, and the INR59,870 estimate/INR130 margin remain unchanged. Ruff, pip compatibility, repository integrity and whitespace checks passed. The real certificate-verified HTTPS workflow and actual API process restart also passed locally, retaining NOT_VERIFIABLE. Actual PR Compose/cookie/probe/upload conclusions are verified before final handoff.

Native repeated-run backend source SHA256: `d90e79c9676a5fd5e3c9909c5f8b849db21b6b7064ed592659fac425600ad230`. Private outputs remain under `work/m03-recovery` in the existing workspace; no private runtime files are committed. No remaining local checker failure is suppressed by regenerating the matrix: its reviewed delta is exactly one actually executed positive reference, and all negative drift checks still fail as required.
