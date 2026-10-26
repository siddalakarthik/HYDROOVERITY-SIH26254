# Current frontend dependency review — 26 October 2026

The unchanged frozen frontend lockfile was audited again with `pnpm audit --json`.
The registry returned zero active advisories at every severity for 395 total
dependency entries. This is a registry snapshot, not a security certification or
a claim that unknown vulnerabilities do not exist. No package was installed,
upgraded, overridden or exempted, and no lockfile change was made.

The earlier M04 audit genuinely reported one high-severity development-only
`braces <=3.0.3` advisory through the Next ESLint tooling. Preserve that historical
finding and its accepted execution-time limitations. The
[official GitHub advisory GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
records withdrawal on **23 October 2026**, following a reassessment of practical
exploitability. The zero-advisory registry response is consistent with that change;
it does not demonstrate a package fix. The advisory still lists no patched version.

| Evidence | SHA256 |
| --- | --- |
| Unchanged `apps/web/pnpm-lock.yaml` | `7da0e33941c4100aef1a2a859b792bd9e350780ea0a38e079a2fe11663374c60` |
| Current raw registry audit, retained outside Git | `c9e770e9c4b611823141bb7c44370e3c117dd928c48a8478c9b929f28359eaaf` |
| Historical M04 raw audit, retained outside Git | `4daf3c70f2dd61c3340b937314a917e9dd1a9d19a249cb57ef80f4264236efd2` |

The machine-readable [review snapshot](../../data/schemas/pre-m10-dependency-review.json)
records the command, counts and source. Reproduce from repository root with
`cd apps/web` followed by `pnpm audit --json`, retaining output outside Git. Results
may change as the registry publishes or withdraws advisories. The existing CI
production-dependency audit remains enforced; no ignore rule was added.

Licensing remains separate. The owner has not selected a project license, and the
[installed third-party notices](../../apps/web/THIRD_PARTY_NOTICES.md) still apply.
Optional Sharp native binaries include LGPL-3.0-or-later and Apache-2.0 declarations;
preserve upstream notices and review redistribution obligations for the actual
target-platform bundle. This audit does not grant redistribution rights or resolve
legal obligations. DEP-01 therefore remains BLOCKED for the owner/license review.

Backend scientific packages, hardware dependencies and system tools were not
re-audited by this frontend command. Existing scientific/physical limitations,
public-deployment gates and historical M09 evidence are unchanged.
