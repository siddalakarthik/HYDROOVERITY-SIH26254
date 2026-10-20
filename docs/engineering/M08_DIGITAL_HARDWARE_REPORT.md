# M08 digital hardware engineering report

**DIGITAL DESIGN / NOT PHYSICALLY VALIDATED.** HYDROOVERITY, Team TARK, SIH26254. Review package for issue #8, based on approved main `131e9276d975d08156b77f967d4535316a0d4125`. No purchasing, construction, pressure operation, firmware deployment or physical experiment occurred. M08 remains subject to owner review; this report is not fabrication approval.

## 1. Frozen system and evidence boundary

WATCH qualifies hydraulic pressure/flow and intermittent supply state; GUARD-5 observes accessible-joint wetness through exactly A/B/C, EXT and BYPASS; portable EAR investigates with two channels on one physical sampling clock. Evidence qualification retains faults, provenance, uncertainty and UNRESOLVED abstention. VERIFY records repair and post-repair evidence. Temperature/humidity are context. No sixth wetness channel, new project version, website implementation or later milestone is introduced.

Approved M05 remains simulation-only. Its nominal GUARD-5 missed **36/96** local leak cases versus **12/96** for multizone. All simulation source, parameters, seeds and evaluation results remain unchanged. Raw evaluation truth remains outside ordinary dashboard/public artifacts. This digital model neither overturns that unfavorable result nor establishes collection efficiency, rain discrimination, acoustic audibility or physical localization accuracy.

## 2. GUARD-5 mechanical envelope

`hardware/guard5-collar/envelope.json` defines mm parameters: horizontal Z pipe axis, gravity −Y, pipe OD32, assumed fitting maximum OD45 × length60, body OD76 × length112, inner shell radius35.5, collector radii24–34 and length70. End bore diameter33.6 gives 0.8 radial clearance to bare pipe; collectors give 1.5 radial clearance to the fitting envelope. Actual pipe/fitting caliper survey is mandatory. No printed geometry replaces or penetrates a pressure-bearing component.

Two shell halves have a 0.6 seam gap, four Ø4.4 clearance holes for M4×20 candidate screws at X=±47/Z=±44 and external drip guards. Adjustable external straps and soft removable pads on bare pipe are the attachment concept; screw torque must not be used to clamp the pressure fitting. Pad geometry, preload and strap routing need detail design. Open cable-tie lugs provide an external strain-relief envelope. Final harness bends and connector sealing are unverified.

Three separate inward-entry sectors A10–80°, B100–170°, C235–305° leave angular coverage gaps. Each has independent walls, a removable holder envelope, a Ø3 axial maintenance port offset 15° from its holder and its own 5OD/3ID tube at Z30. EXT is an outside exposure tray on a shelf; BYPASS is a separate bottom witness under a Z0 escape slot. Normal drain tubing does not empty into either witness. Gravity arrows describe intent, not a CFD result. Final electrode seating, wicks, pocket retention, witness fasteners, tube retention and challenge-port closures remain detail-design gates. Do not manufacture directly from these envelopes.

Service sequence: free cables/tubes and detach witnesses; remove fasteners; separate shell halves; lift collectors; slide the probe carriers from their sockets. End lips prevent extracting holders axially through a closed shell. Final supports/retainers and tools must be tested on a dry assembly.

## 3. Actual CAD execution and scope

CadQuery **2.8.0**, cadquery-ocp **7.9.3.1.1**, Python **3.12.14** executed locally in an isolated environment. No FreeCAD/OpenSCAD/Blender/KiCad application was found. Editable parametric `guard5.py` genuinely regenerates **25 valid one-solid parts** and an assembly, including two distinct metal electrode strips in clearance sockets for each of the five channels. Each part was exported as STEP, reimported and checked for validity, solid count, volume and bounding box. STEP is FreeCAD-compatible exchange geometry; no native FCStd document or FreeCAD run is claimed.

Digital checks: zero pairwise overlap above 0.0001 mm³; zero pipe/fitting reference intersection above that threshold; nominal clearances; Ø8 driver access over 25 mm at four fasteners; shell opening sampled at 1/5/15/30/60 mm after loose parts are detached; open lumen at each drain outlet. These sampled envelopes are not continuous-motion, strength, seal, hydraulic-flow or manufacturing-tolerance proofs. Tube bore continuity is analytic; pocket capture efficiency is untested.

The first audit detected an EXT shelf overlap and driver/drip-guard clash; both were corrected in geometry. STEP healing caused a maximum approximately 0.552 mm³ volume difference in a roughly 52,000 mm³ part. The recorded numerical acceptance is ≤0.002% volume and <0.001 mm bounding-box change, with preserved solid count; this is an exchange-format audit tolerance, not print tolerance. Final raw measurements are in generated `geometry_checks.json`.

Proposed mitigations and remaining failure modes are tabulated in `hardware/calibration/VALIDATION_PLAN.md`. In particular A/B drainage may empty before elevated holder surfaces wet. Wick or electrode placement must be revised through controlled weak-flow tests; no favorable result is assumed. Region bridging, out-of-level mounting, blocked drains, runoff through end openings and stale retained moisture remain plausible failures.

## 4. WATCH electronics and compatibility

`interfaces.json` holds exact GPIO and ADC assignments. Two ADS1115IDGST-compatible 3.3 V converters at 0x48/0x49 supply eight multiplexed inputs: two pressures, exactly five wetness channels and one divided rail monitor. SDA GPIO8/SCL GPIO9; flow GPIO4/5; powered DS18B20 GPIO6; probe excitation GPIO12/13. Boot, USB and N8R8 PSRAM pins are reserved. SHT31 0x44 is contextual. No simultaneous WATCH sampling claim.

SEN0257 is a 5 V, 0.5–4.5 V voltage-output candidate, not a current loop. A 20k/20k 0.1% divider and 1 µF filter produce 0.25–2.25 V (2.5 V at 5 V output fault), within a powered 3.3 V ADC. ±4.096 V PGA does not extend input supply limits. Its 0–16 bar span is poorly matched to the proposed low-pressure rig: 1%FS = 0.16 bar. Calibration or a separately reviewed lower-range part is necessary. Supply-off/transient protection and output loading remain gates.

SEN0217 pulse signals use a proposed NPN translator and 3.3 V collector pull-up; real module output behavior, transistor package and switching must be confirmed. Bulk meters cannot reference microleak rate. Pressure/flow harness pin numbering is the proposed harness contract, not verified supplier cable colors.

Five wetness paths use 47k in each excitation leg, a distal 100k EOL and paired polarity scans. The unloaded short-current bound is ~35.1 µA/channel. EOL supervises a circuit path only; corrosion, probe faults beyond the resistor, wet cable and collector failure remain ambiguous. High source impedance, ADC loading and clamp leakage require measurement. Dry is never proof of healthy electrodes or no leak.

Four **editable KiCad-format connectivity drafts**, `watch`, `wetness`, `ear`, `power`, and a generated **371 pin/net CSV ledger** are supplied. Embedded generic passive-pin blocks permit independent editing without external symbol libraries. Structural S-expression/component/label checks are possible; native KiCad opening and electrical-rule checks **did not run**. These are not production schematics or a fabrication-ready PCB. Low-leak clamp MPNs, oscillator/module pinouts, power-protection ratings, analog filtering/noise and footprint/package review are explicit unresolved gates.

## 5. EAR acoustic design

Two candidate Murata 7BB-27-4L0 passive piezo diaphragms with identical removable mounts feed two matched TLV9064IPWR quad-opamp paths at 5 V. Each path: 1 MΩ bias input follower → noninverting gain11 → two buffered 3.3k/10nF RC poles (~4.82 kHz each) → 1 µF AC coupling/1k series into PCM1808. Bias is nominal 2.5 V. Converter input is nominal 3 Vpp at 5 V; real gain/clipping, bias transients and source loading must be checked. Two RC poles plus converter filtering do not establish sufficient alias rejection or a flat usable passband.

PCM1808PW analog 5 V/digital 3.3 V; MD1=MD0=HIGH gives master 256fs; FMT=LOW selects I²S. **One external 12.288 MHz 3.3 V oscillator → SCKI**; stereo ADC outputs 3.072 MHz BCLK and 48 kHz LRCLK. ESP32-S3 receives BCLK GPIO15, WS GPIO16 and DIN GPIO17 in standard RX slave mode, with MCU clock output disabled. This implements the proposed physical common-clock architecture in connectivity, not executable firmware. A random PCM1808 marketplace module is not approved without checking exposed straps and rails. Clock MPN/jitter and actual board compatibility remain gates.

At 48k stereo frames/s, 24 valid bits in 32-bit slots require 384kB/s; ten seconds is 3.84MB (2.88MB packed). 64KiB buffering spans only 170.7ms. N8R8 PSRAM does not prove DMA or SD throughput. Channel order, startup, dropped frames, overflow and hashes must be checked; missing/ambiguous capture cannot yield a supported location. Metadata schema and future enforcement rules are supplied. Alternate PVDF/IEPE pickup tradeoffs, cable shielding, matched mounting and wave-speed calibration are documented. No cheap-piezo universal weak-leak claim or physical centimetre accuracy is supported.

## 6. Power and complete demonstration BOM

Proposed isolated 24V/5A supply with master/reverse/transient protection, separately fused DC pump stop branch and protected 24→5V/3A buck. WATCH/EAR peak allowances 0.65/0.85A at 5V total 7.5W; with 48W pump and assumed 85% buck efficiency, ~2.37A at 24V. Actual inrush and noise are unmeasured. Local board regulators supply separate 3.3V rails; no parallel outputs or USB backfeed. Power schematic is a protection/connectivity draft; fuse, TVS, reverse-protection, ferrite and buck ratings are unselected gates. Qualified isolated mains/RCD provision and dry electronics placement remain necessary.

All **41 essential materials lines** cover rig, safety, reference, WATCH, GUARD-5, EAR, clock/storage/controllers and power. `hardware/bom/M08_BOM.md` is the readable ledger; CSV/JSON include quantities, assumptions, substitutions and source/status fields. Components **₹54,870**, contingency **₹5,000**, total **₹59,870**, headroom **₹130**. Compared with previous ₹56,750 allocation, +₹3,120. All prices **ESTIMATED_NOT_QUOTED** on 2026-10-20; no verified supplier price. Technical URLs are datasheets, not quotations. Taxes/shipping must fit reserve and headroom; actual affordability is unresolved. No unsafe deletion of safety parts to fit cap. Recurring local electricity ~₹37.44/month, optional data ₹100–300/month and consumables ₹500/quarter are separate assumptions outside materials cap.

## 7. Rig and future validation

75L vented tank, candidate SEAFLO SFDP2-012-035-21 24V pump, strainer and manifold feed four 3m OD32 sections (12m accessible acoustic span) with contained replaceable leak stations at 6/9m; collar at6m, EAR endpoints0/12m, supply/return pressure and flow. Budget includes a full12m return (24m hardpipe total) plus3m local pump/bypass hose, rated valves/fittings, supports, reservoir return and containment. This is separate from M05's distribution network.

Unisolatable mechanical relief and adjustable bypass return directly to tank. Pump pressure switch is not a relief valve. Nominal PN10 procurement class does not establish the assembled weakest-part rating. Proposed 0.5/1/1.5bar points and 1.8bar relief are conditional examples only. Pump free-flow/shutoff endpoints are not a pressure-flow curve; pressure rating, actual flow, relief capacity and safe assembly review must precede any operation. No municipal network connection or printed pressure joints. Reference leak rate by weighed capture with checked scale/timer; 0.01g display resolution is not accuracy. No physical operation was performed or authorized. A final loop audit corrected an initial return-pipe undercount: +₹1,620 for9m extra pipe; −₹180 for one tee, −₹500 for two valves and −₹400 for one fewer cartridge (unit allowance conservatively rises to₹450). Two controlled stations remain; the inlet service valve is omitted, requiring full draining before intake service. Return throttle, bypass and independent relief remain. Net +₹540 over the initial M08 draft; no vendor price was reduced to force the cap.

The validation plan covers pressure/flow calibration, conductivity/temperature, wetness faults, gravimetric collector mass balance, blind holdouts, acoustic gain/phase/alias behavior, physical clocks, lossless capture and effective wave speed. Electrical self-test and water-path challenge are separate states and neither establishes universal leak detection.

## 8. Firmware and M02 readiness

`hardware/firmware/INTERFACE_READINESS.md` defines schedules, units, quality mapping, watchdog, stale/fault handling, service connections, storage and power. M02 scalar ObservationInput fields and four quality enums are preserved. Trusted adapter identity must supply laboratory/field provenance; clients do not assert source/environment/truth. Waveforms use a separately authorized artifact flow; no API change or running adapter exists. No production-ready or build-tested firmware is claimed.

## 9. Figures, checks and reproduction

`hardware/render_m08.py` regenerates **H01 architecture, H02 assembled/exploded CAD, H03 cutaway/water paths, H04 WATCH, H05 shared-clock EAR, H06 rig, H07 budget**. Each is 2560×1440 PNG plus editable SVG with the proposed/untested label. Captions and per-source SHA256 manifest are generated under `hardware/results/ppt/`. H03 radial panel is a parameter layout; longitudinal panel is an actual BRep material slice. Additional native STEP parts/assembly are under `hardware/mechanical-cad/exports/`. Generated binaries and local figures are intentionally ignored, reproducible and included in the local review bundle.

From repository root, use a separate Python3.12 environment:

```text
python -m pip install --only-binary=:all: -r hardware/requirements-m08-cad.txt
python hardware/electronics/generate_schematics.py
python hardware/mechanical-cad/guard5.py
python hardware/render_m08.py
python scripts/check_m08.py --artifacts
python -m unittest discover -s tests/unit -p test_m08_checks.py -v
python scripts/check_repository.py
python scripts/check_m02_design.py
python scripts/test_m02_design_checker.py -v
python -m openapi_spec_validator --schema 3.1 docs/architecture/openapi-design.json
python scripts/validate_openapi_design.py
python -m pytest tests/unit/test_m05.py -q
git diff --check
```

Keep OpenAPI, M05 scientific and CAD environments separate; use their existing pinned requirement files. On restricted desktops set MPLCONFIGDIR to a writable local cache. CAD requirements record core resolved versions; optional CadQuery visualization dependencies are not imported by this project. `check_m08.py` checks capacity, pins, rails, clock mode, power arithmetic, cost, rig status, draft connectivity and artifact provenance; nine focused tests reject dangerous consistency changes and undercounted return plumbing. It cannot establish native ERC or physical safety. Actual execution results and CI status are recorded in `hardware/VALIDATION_RESULTS.md` and the PR.

## 10. Review gate and PPT-safe claims

Safe: inspectable parametric design, genuine STEP exchange checks, proposed matched common-clock acquisition, complete estimated materials ledger and explicit qualification plan. Strongest limited-slide choices: H02, H03, H05, H07; H01 provides system context if space allows.

Prohibited: fabricated prototype, tested pressure safety, calibrated sensor accuracy, verified capture efficiency/rain rejection, proven leak audibility/localization, KiCad ERC pass, measured power or supplier-quoted budget. M08 cannot be approved as fabrication-ready until retention/electrodes/port closures and real fit, protection details, native schematic review, exact modules/clock, ratings and quotations are resolved. All physical performance gates remain future work. Do not merge or close issue #8 automatically.
