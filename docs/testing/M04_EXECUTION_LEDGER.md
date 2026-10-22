# M04 execution ledger

Status: DELIVERED FOR OWNER ENGINEERING AND VISUAL REVIEW in PR #16. Implementation-head CI passed all four jobs; no merge or public deployment is authorized. Entries below preserve execution history, including failures and acceptance items that were pending at the time. The final verified evidence is recorded at the end.

## Executed preparation

- Fetched main and created isolated `feature/m04-frontend-foundation` worktree from `e0122f5ee4146e49ae6113a1aa6a5ee444b25973`; other milestone worktrees preserved.
- Authenticated GitHub read confirmed main at that SHA, baseline run 39588590017 succeeded with all three jobs, issue #3 closed and #4 open.
- Exported the implemented-only OpenAPI and generated all 46 route capability classifications; `tools/contracts.py --check` passed.
- Prepared separate real PostgreSQL/PostGIS `hydro_disposable_m04` fixtures with native M03 dependencies. No M03 database reset or database-role password change.
- Started the M04 API and optional HTTPS frontend proxy on loopback with private runtime configuration outside Git.
- Python compileall of M04 tools passed.
- First repository check demonstrated an oversized 4 MiB CAD SVG; the web copy was replaced with the unchanged reviewed 356 KiB PNG. Source CAD and original SVG are preserved.

## Dependency resolution failures retained

The registry initially advertised versions whose dependency metadata was temporarily unavailable to npm: axe Playwright 4.14.0 required unresolvable axe-core ~4.14.0, and Next ESLint 16.4.2 initially could not resolve its same-version plugin. The axe adapter was changed to published 4.11.1, ESLint to compatible 9.39.5, and registry metadata refreshed. Exact final resolution, audit and build results remain pending. A failed resolution is not a successful install.

## Pending acceptance

Exact lockfile installation, type/lint/format checks, production build, unit/component suites, real-browser positive/negative workflow, mobile widths, axe checks, reference-vs-render visual QA, runtime persistence evidence, regression checks, dependency/license report, performance measurements and actual PR CI/artifacts.

No physical or field experiment is included. Verification remains NOT_VERIFIABLE for manual-only evidence. M05 results and unfavorable GUARD-5 outcomes are unchanged.

## Executed regression checks during implementation

- Repository foundation integrity: PASS after the exact reviewed PNG checksum/signature exception; no broad binary allowance.
- M02 design consistency: PASS, 57 tables / 117 operations / 46 routes / ten wireframes.
- M02 checker: two test methods and 33 deliberate mutation cases PASS.
- Independent canonical OpenAPI: PASS, 154 component metaschemas and JSON Schema tuple bounds.
- M03 real PostgreSQL acceptance run 1: 45 passed in 68.94 seconds; run 2: 45 passed in 67.23 seconds. Both retain all 58 implemented positive projections.
- Both strict traceability checks PASS; 37 targeted traceability regressions PASS. Current backend source digest matches executed acceptance: `d90e79c9676a5fd5e3c9909c5f8b849db21b6b7064ed592659fac425600ad230`.
- Independent implemented OpenAPI validation PASS.
- M05: initial sandbox-temp run failed eight cases with WinError 5. Rerun with the established workspace TEMP/TMP passed all 38 in 10.19 seconds. No source or simulation parameters changed.
- M08: consistency PASS, 13 focused tests PASS. BOM remains INR59,870 / INR130 margin; native ERC unavailable and physical tests not performed. Full CAD regeneration is not yet rerun locally in M04; the existing CAD CI job is preserved.
- Existing services/api, simulations and hardware tracked source verified byte-unchanged against the M04 base. Existing three CI job bodies preserved; an additional isolated M04 job is under construction.
- M04 public status endpoint verified through the real local proxy with explicit certificate verification. Frontend rendering is still pending installation.

The initial ESLint 9 selection was found unsupported, and the packaged Next lint configuration retains a legacy React plugin excluding ESLint 10. The implementation now selects supported ESLint 10 with the official Next plugin, compatible TypeScript ESLint and React Hooks plugins directly. Actual package installation and tool execution remain pending; these are compatibility decisions, not a claimed lint pass.

M08 regeneration also passed locally: four schematics / 371 connections, 25 CAD parts with STEP round trips and zero detected interference pairs, seven 2560×1440 PNG/SVG plates, and artifact consistency. An ezdxf cache-directory warning affected optional cache persistence only; no physical fit, native ERC or hardware trial is implied.

Frontend syntax smoke check: all 26 TS/TSX source/test files parsed successfully with the exact downloaded Babel parser after correcting one malformed membership generic. This is not TypeScript checking or runtime evidence.

The first frozen install downloaded 312 of 325 platform-relevant packages, passed the lockfile supply-chain verification, then failed with timeout code 23 before TypeScript, Prettier and Next became usable. Cache contents are retained. A later exact-icon correction pins lucide-react 1.59.0 (published 17 October), avoiding the same-day 1.61.0 release-age exception. The earlier lockfile is preserved outside Git; the corrected lockfile is being regenerated under the unchanged release-age policy. No policy relaxation or lifecycle-script execution is used.

## M04 dependency recovery and first executable checks

- Corrected exact lock regenerated offline from cached registry metadata under the unchanged pnpm release-age policy. Frozen installation completed: 325 platform packages; lifecycle scripts disabled. Slowest remaining download was the official Rolldown Windows binding.
- Added explicit cached GeoJSON declarations; removed an incompatible test-only jest-dom/Vitest augmentation in favor of native typed assertions. Source remains strict TypeScript. `skipLibCheck` excludes upstream declaration internals (Next's URLPattern declarations require newer DOM aliases); it does not disable application type checking. No previously passing repository gate changed.
- Generated actual M03 browser types: PASS. TypeScript application check: PASS. ESLint with zero warnings: PASS. Vitest: 16 tests across two files PASS (5.47 seconds on the final rerun).
- Turbopack production build failed twice at local PostCSS child-process IPC, including outside the sandbox. Supported Webpack builder compiled and completed TypeScript; final tracing result is pending. The documented build command now explicitly selects Webpack consistently for local use and CI.
- Browser negatives added for ownership, forged Origin, reassignment, last-administrator and immediate session revocation. These remain unexecuted until browser acceptance completes.

Production build with supported Webpack: PASS. Actual loopback Next server returned HTTP 200; the rendered public homepage was opened and visually inspected. First real Chrome workflow run stopped at an axe `link-in-text-block` finding on a breadcrumb before report submission; links inside prose were underlined and the production build passed again. Full workflow rerun is in progress, not yet a pass.

Installed license inventory contains 302 package entries, with no unknown/unlicensed declarations. Notices include MPL-2.0 tools, CC-BY-4.0 caniuse data and optional native Sharp binaries declaring Apache-2.0 AND LGPL-3.0-or-later; redistribution must retain upstream obligations. This is dependency inventory, not legal certification.

Actual registry audit: one HIGH development-only `braces <=3.0.3` finding through `@next/eslint-plugin-next > fast-glob > micromatch`, GHSA-vfj7-8cjw-p6xm; registry reported no published patched version. The lint command uses repository-owned fixed patterns; no public runtime glob endpoint is exposed. This remains an explicit owner-review risk, not a clean-audit claim. No finding is suppressed.

Browser rerun passed the citizen create/follow-up/ownership projections and supervisor overview accessibility, then stopped on an ambiguous test locator shared by the filter and create forms. The locator was scoped to the actual incident creation form. No passing workflow is claimed yet.

## Browser execution and rendering corrections

The cross-role workflow passed on installed official Chrome 155.0.8059.85 against the certificate-verified loopback application and real PostgreSQL. The run covers resident create/follow-up/ownership, supervisor triage/link/review, assignment, mobile technician actions/repair/submission, independent NOT_VERIFIABLE, governance/tenant switching, logout/back navigation and security denials. No unexpected console or page errors remained. The browser-safe summary is outside Git in the dedicated evidence directory.

The first map run exposed MapLibre 6's bundled `import.meta.url` worker fallback; a visible canvas alone was insufficient. The package worker is now emitted as a same-origin hashed Webpack asset. A post-fix screenshot shows the authorized synthetic line and its two junctions; the test waits for the map's rendered-idle marker. No external basemap is used.

The second browser scenario has executed real zone/two-junction/pipe creation, versioned pipe edit, offline read recovery, forced WebGL fallback, not-found and deferred route behavior. Account registration/verification reached a preserved rate limit; the test now handles this explicitly instead of waiting forever for a login POST blocked by CSRF bootstrap. Full second-scenario acceptance remains pending.

Browser tooling: pinned Playwright 1.64.1 Chromium 156 download is still completing. Local Chrome fallback is explicit in configuration and documentation; CI retains the pinned Chromium default. These browser versions are not conflated.

## Completed local browser acceptance

Both expanded real-browser scenarios passed in 1.9 minutes. Account coverage includes actual utility lookup, citizen registration, private token verification, login, profile edit, current-session revocation, recovery/reset and invitation acceptance. Real asset creation/edit, offline read recovery and forced WebGL fallback passed. The backend rate limit was observed and waited out; no limiter was disabled. All records remain synthetic.

The final production build also includes the demonstrated mobile geometry refit and concise workspace breadcrumbs. The first scenario passed again with keyboard skip/navigation/Escape checks and mobile report-form accessibility. A final loaded-directory capture was independently inspected. Actual main remains e0122f5ee4146e49ae6113a1aa6a5ee444b25973 and issue #4 remains open. Final branch publication/CI and artifact verification follow; no merge is authorized.

## PR publication and CI recovery

PR #16 opened at `91df69606488dc7df0308ad647afebb3b32cf733`. Actual run 39653117419 passed repository/M02/OpenAPI/M05/M08 integrity, full M08 CAD/figures/artifact and M03 backend jobs. The new M04 job correctly rejected Vite 8.3.5 because it was published the same day, inside pnpm's default release-age cutoff. No M04 CI artifact existed from that failed run.

Correction: explicitly pin compatible Vite 8.3.4, published 8 October according to the official registry. The exact prior pnpm-generated package entry was restored from the preserved pre-recovery lock, its integrity independently matched the official version metadata, and all transitive snapshot dependencies were unchanged. The normal frozen install/policy gate is being rerun; no release-age setting, exception or security check was relaxed. Failed attempts to use pnpm add were blocked by the original lock's rejected same-day entry and retained in local diagnostic logs.

The corrected release-age check passed all 395 entries during online verification; an initial snapshot-reference omission was detected and fixed before publication. The fully corrected offline reinstall linked the three cached Vite-dependent packages but could not complete policy re-verification because full @redocly/openapi-core metadata is unavailable offline. This environment limitation is not a policy bypass or a claimed frozen-install pass. Actual Linux CI remains the final install/policy proof for the corrected head.

Corrected-head local recovery completed: normal frozen installation passed all 395 supply-chain entries with lifecycle scripts disabled (62.1 seconds). Strict TypeScript and all sixteen Vitest tests passed again with explicit Vite 8.3.4. Temporary missing-module attempts occurred while the failed install was relinking dependencies; they were rerun after links and policy validation completed. No application source, M03 backend, M05 scientific result or M08 hardware source changed in this correction.

Actual run 39654813829 on 59fb71d passed frozen Linux install, compile/type/lint/format/unit/build and production advisory checks. Its disposable database fixture step failed because the Docker image's temporary initialization socket satisfied pg_isready before the final TCP listener was ready. The M04-only workflow now waits for an authenticated TCP SELECT 1 before operator preparation. Existing backend, design, simulation and CAD jobs remain unmodified. No M04 artifact from this failed run is claimed.

## Verified implementation-head CI

Implementation commit `55b046346399f227f1ba11afecf533f9f5c33828` passed [run 39655482362](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39655482362): repository-integrity, m03-backend, m08-cad-and-figures and m04-frontend all concluded success. The authenticated TCP readiness correction resolved the disposable-fixture startup failure without changing application, backend, scientific or hardware source.

The M04 job executed frozen installation, generated-contract checks, strict TypeScript, zero-warning lint, formatting, sixteen unit/component tests, the production build, the production dependency audit and both real PostgreSQL/PostGIS browser scenarios. The existing design, OpenAPI, numerical simulation, backend and CAD checks remained enabled and passed. Local visual comparison, mobile captures and keyboard checks passed; `design-qa.md` records the scoped audit.

The successful workflow uploaded [HYDROOVERITY_M04_BROWSER_EVIDENCE](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/39655482362/artifacts/12369674792), with 14-day retention. It contains explicitly captured synthetic screenshots and safe JSON summaries, not private fixture configuration, tokens, evaluation truth or seeds. Later documentation-only commits must still pass their own PR CI; the PR is the current-head status authority.

The one disclosed HIGH development-only braces advisory remains unresolved. Production dependency audit reported no known vulnerabilities. Automated accessibility checks and local timing are limited software evidence, not certification or field performance. Owner engineering/visual acceptance remains pending; issue #4 stays open and main is unchanged.
