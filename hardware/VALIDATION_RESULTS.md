# M08 executed digital validation

DIGITAL DESIGN / NOT PHYSICALLY VALIDATED. Local execution on 2026-10-20, Windows, Python 3.12.14. See the [engineering report](../docs/engineering/M08_DIGITAL_HARDWARE_REPORT.md) for reproduction and limits. Actual PR/CI status belongs to the PR checks; this local record does not predict a CI result.

| Check | Actual result |
|---|---|
| CadQuery 2.8.0 / OpenCascade 7.9.3.1.1 | 25 valid one-solid parts, genuine STEP export/reimport; preserved solid count, volume and bbox within documented numerical tolerance |
| Part / pipe interference | Zero pairs and zero pressure-pipe/fitting reference intersection above 0.0001mm³ |
| Access / opening / drain | Ø8 driver envelope clears; sampled half opening clears; independent tube outlet lumens open. No physical motion/flow proof |
| Electrical / BOM contract checker | 2 ADCs, 8 inputs, 5 distinct wetness paths, GPIO reservations, clock mode, voltage/power arithmetic, 41 unique BOM lines, total ₹59,330 / headroom ₹670 |
| Four schematic drafts | Structural parser, component counts, labels, exact 371 pin/net ledger and selected converter pin maps agree. Native opening/ERC unavailable |
| Focused negative tests | 8 passed: baseline and rejection of sixth channel, GPIO collision, bad clock, over-cap cost, pressure overvoltage, unauthorized rig operation, broken schematic structure |
| Foundation integrity / limited secret hygiene | Passed; scanned actual tracked/unignored files and local documentation links |
| M02 design consistency | 57 tables,117 API operations,46 routes,ten wireframes; zero errors; 33 deliberate invalid mutation cases rejected |
| Independent OpenAPI | openapi-spec-validator0.9.0, jsonschema4.26.0: OpenAPI3.1 and154 component metaschemas pass; tuple positive/negative checks pass |
| M05 numerical regression | 38 passed. Initial run had8 temp-directory PermissionErrors/30passes; after TEMP/TMP pointed to workspace, all38passed. No simulation source or assertion changed |
| Approved M05 preservation | Git diff against approved main is empty for simulations, tests/unit/test_m05.py and M05 evidence report |
| Figures / provenance | Seven2560×1440 PNG/SVG plates plus supplementary I²S timing detail; SHA256 source manifest, visual review and artifact consistency check passed |
| Whitespace | git diff --check passed before publication |

Unavailable / not performed: FreeCAD-native validation, native KiCad open/ERC, PCB checks, real firmware build/capture, print fit/retention/strength, pressure safety and all physical/field performance experiments. Some exact protection parts/module details are explicitly unselected. These are approval gates, not passed tests. No failed physical trial has been concealed because no such trial occurred.
