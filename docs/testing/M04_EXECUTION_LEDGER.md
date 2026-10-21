# M04 execution ledger

Status: IN PROGRESS. No M04 completion, visual QA pass, browser pass, public deployment or CI pass is claimed in this initial record.

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
