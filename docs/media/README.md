# Reviewed repository previews

These seven unchanged PNG copies make accepted engineering and software evidence visible in the public repository. They total approximately 1.38 MB; each stays below the existing 1 MiB file limit. The [manifest](manifest.json) records exact image checksums, source checksums, captions and reproduction references. The repository checker permits only these exact bytes.

| Preview | Source and qualification |
| --- | --- |
| [Website](website-public.png) | Actual M09 synthetic public-page browser capture; no private resident content |
| [Split collar](guard5-cad.png) | M08 H02 assembled/exploded parametric geometry, not physically fit-tested |
| [Five channels](guard5-channels.png) | M08 H03 A/B/C, EXT and BYPASS; water paths are proposed |
| [Common clock](acoustic-clock.png) | M08 H05 two pickups and one physical ADC clock; recorder unvalidated |
| [Test rig](test-rig.png) | M08 H06 complete supply/return proposal; not an assembled rig |
| [Budget](budget.png) | M08 H07 INR 59,870 estimate, INR 130 margin; 41 prices are not quotations |
| [GUARD-5 comparison](guard5-comparison.png) | M05 figure 07, including unfavorable results and unresolved physical health |

## Reproduce without publishing private evaluation material

From repository root, use the isolated environments and exact commands in [M08 output reproduction](../../hardware/results/README.md), [M05 reproduction](../../simulations/README.md) and [M09 browser execution](../testing/M09_FULL_SYSTEM_ACCEPTANCE.md). Regenerate the source outputs there, inspect them, then copy only the named PNGs above. Generated raw arrays, evaluation truth, seeds, mail, configurations and CAD/STEP bundles stay outside this media folder.

A new render may have different PNG metadata or platform font metrics. Do not silently replace checksums: review the resulting image and source changes together, update the manifest and exact binary allowlist through a PR, and run `python scripts/check_repository.py` and `python scripts/check_repository_media.py`. No source result is changed to match a presentation target. SVG/STEP exports remain available through M08's validated package; bulk payloads do not belong in ordinary Git history.

These are historical accepted previews, not a fresh website audit or new experiment. Every engineering preview retains PROPOSED DESIGN / NOT PHYSICALLY TESTED; the simulation retains its physical-validation caveat. Image rendering is not scientific or hardware validation.
