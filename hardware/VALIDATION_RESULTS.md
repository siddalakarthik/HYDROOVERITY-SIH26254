# M08 executed digital validation

DIGITAL DESIGN / NOT PHYSICALLY VALIDATED. Local execution on 2026-10-20, Windows, Python 3.12.14. See the [engineering report](../docs/engineering/M08_DIGITAL_HARDWARE_REPORT.md) for reproduction and limits. Actual PR/CI status belongs to the PR checks; this local record does not predict a CI result.

| Check | Actual result |
|---|---|
| CadQuery 2.8.0 / OpenCascade 7.9.3.1.1 | 25 valid one-solid parts, genuine STEP export/reimport; preserved solid count, volume and bbox within documented numerical tolerance |
| Part / pipe interference | Zero pairs and zero pressure-pipe/fitting reference intersection above 0.0001mm³ |
| Access / opening / drain | Ø8 driver envelope clears; sampled half opening clears; independent tube outlet lumens open. No physical motion/flow proof |
| Electrical / BOM contract checker | 2 ADCs, 8 inputs, 5 distinct wetness paths, GPIO reservations, clock mode, voltage/power arithmetic, 41 unique BOM lines;24m full-loop pipe and2 leak stations, total ₹59,870 / headroom ₹130 |
| Four schematic drafts | Structural parser, component counts, labels, exact 371 pin/net ledger and selected converter pin maps agree. Native opening/ERC unavailable |
| Focused negative tests | 9 passed: baseline and rejection of sixth channel, GPIO collision, bad clock, over-cap cost, pressure overvoltage, unauthorized rig operation, undercounted return line, broken schematic structure |
| Foundation integrity / limited secret hygiene | Passed; scanned actual tracked/unignored files and local documentation links |
| M02 design consistency | 57 tables,117 API operations,46 routes,ten wireframes; zero errors; 33 deliberate invalid mutation cases rejected |
| Independent OpenAPI | openapi-spec-validator0.9.0, jsonschema4.26.0: OpenAPI3.1 and154 component metaschemas pass; tuple positive/negative checks pass |
| M05 numerical regression | 38 passed. Initial run had8 temp-directory PermissionErrors/30passes; after TEMP/TMP pointed to workspace, all38passed. No simulation source or assertion changed |
| Approved M05 preservation | Git diff against approved main is empty for simulations, tests/unit/test_m05.py and M05 evidence report |
| Figures / provenance | Seven2560×1440 PNG/SVG plates plus supplementary I²S timing detail; SHA256 source manifest, visual review and artifact consistency check passed |
| Whitespace | git diff --check passed before publication |

Unavailable / not performed: FreeCAD-native validation, native KiCad open/ERC, PCB checks, real firmware build/capture, print fit/retention/strength, pressure safety and all physical/field performance experiments. Some exact protection parts/module details are explicitly unselected. These are approval gates, not passed tests. No failed physical trial has been concealed because no such trial occurred.

## Final presentation-delivery review corrections

Reviewed base: `3e5fcbb3fba1653b3c6ce3b50a71ecbd958e6986`. The missing runner path in `hardware/results/README.md` was replaced by the actual schematic/CAD/figure/check/package scripts. CAD, OpenAPI and scientific commands are assigned to their separate isolated environments. The existing Python3.12 CAD environment and pinned requirement installation command were verified; all documented generation and package/verify commands ran from the repository root.

Local validation after these corrections: 25 CAD solids and STEP checks, seven PNG/SVG plates plus timing detail, artifact consistency, **13 focused tests** (nine engineering plus four archive-integrity cases), repository integrity, M02/33 mutation cases, independent OpenAPI/154 metaschemas, **38 M05 tests**, M05 smoke and whitespace checks passed. M05 source/configuration/evidence and the reviewed mechanical/electrical/BOM/rig inputs are unchanged. Smoke output stayed outside the presentation package and ordinary public/dashboard artifacts.

Visual inspection of the seven-figure contact sheet and individual details found presentation overlap in H04's flow routing and H06's safety/relief labels. Only arrow routing, caption position and device-box drawing order were corrected; there is no hardware redesign. The five wetness channels, one physical shared-clock stereo ADC, complete12m supply/12m return, ₹59,870 total/₹130 residual and every proposed/untested label remain visible. A supplementary text-boundary audit found no figure-frame text clipping. The contact sheet is an overview; individual high-resolution images are the PPT assets.

`hardware/package_m08.py` builds an explicit allowlisted ZIP, writes SHA256 checksums for every payload, verifies its contents without extraction and rejects corruption, uncovered extra files and traversal names. No environments, credentials, personal files, diagnostic `debug.step` or evaluation truth are included. The workflow builds/verifies before uploading with14-day retention. Actual upload availability must be confirmed in the resulting run; this document does not substitute for the artifact listing. The ₹130 residual is still a procurement risk. None of the physical/native-ERC/firmware/quotation limitations above has been removed.
