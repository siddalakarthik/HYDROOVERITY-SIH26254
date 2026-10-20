# M08 proposed calibration and physical qualification

DIGITAL DESIGN / NOT PHYSICALLY VALIDATED. No tests below have been performed. No rig operation or purchase is authorized. All actual components, ratings, pump curve, relief capacity/setpoint, containment, electrics and local supervision require review first. Nominal 0.5/1.0/1.5 bar and 1.8 bar relief are contingent examples, not selected operating conditions.

| Subsystem | Future method | Required evidence / rejection |
|---|---|---|
| Pipe / fitting / collar | Caliper OD, fitting length, pipe straightness; dry assembly, screw access, repeated removal and print tolerance check | Zero pressure-pipe alteration; clearance and pad compression recorded; no unsupported preload claim |
| Pressure | Traceable suitable low-range reference; zero, ascending/descending points, repeatability, temperature and hysteresis | Residuals + uncertainty in bar; sensor FS mismatch acknowledged; reject saturation, supply-off backfeed or unbounded error |
| Bulk flow | Timed weighed/volumetric collections at several flows, repeated directions if applicable | K-factor and low-rate resolution; never extrapolate to microleak accuracy |
| Five electrical wetness paths | Known resistors, dry insert, conductive films, cable open/short, EOL faults and swapped harness | Both polarity raw values, loading/settle time, leakage/current; quantify ambiguous failures, do not label EOL as electrode health |
| Conductivity / temperature | Measured water conductivity and temperature sweep, contaminated/dried surfaces | Threshold stability, fouling/corrosion and false-wet rate; controlled duty-cycle balance |
| Mechanical collection | Independently weighed leak input and five separated catch paths at multiple positions/rates | Collection fraction, escape/unaccounted mass, wetting latency, missed events; rejection denominators fixed before testing |
| Acoustic analog | Common electrical signal; frequency sweep and amplitude steps with known source impedance | Channel gain/phase mismatch, noise, clipping, alias leakage and fixed delay; measured passband, not assumed RC alone |
| Clock / capture | Scope/logic analyzer SCKI/BCLK/LRCLK and I²S framing; long SD recordings; separate L/R injection | Frequency/jitter bounds, exact frame counts, channel order, no dropouts; fail closed on overflow |
| Effective wave speed | Several known separations and controlled excitations on actual assembled span | Fit speed + uncertainty for pipe/support/fluid state; tap timing does not establish leak detectability |
| Passive leak investigation | Blind held-out controlled leak/no-leak conditions with independent reference | Accepted fraction, error denominators, confident mistakes, false alarms and UNRESOLVED cases; no synthetic physical accuracy claims |

Randomize repeated challenge positions, collar orientation, leak strength, rain/runoff direction, supply state and acoustic nuisance conditions. Pre-register holdout conditions and thresholds before inspecting their truth. Measure input and every discharge by gravimetry with tare, evaporation/time correction and checked scale linearity; 0.01 g display resolution is not accuracy. Return contaminated challenge water only to the lab reservoir, never a utility system. Publish all failed collections and boundary conditions.

Electrical self-test injects a known circuit condition and verifies acquisition only. A maintenance water-path challenge places a controlled quantity at the designated entry port and observes capture and discharge. It does not validate every real leak direction. Both require explicit state and results, not a single HEALTHY flag.

GUARD-5 risks and proposed hypotheses:

| Failure concern | Proposed geometry / practice | Remaining uncertainty |
|---|---|---|
| Water misses selected sectors | Three inward-facing collectors, wider replaceable wick trials and separate bottom BYPASS | Angular gaps remain; wick can divert water or retain old wetness |
| Cross-region migration | Partition end walls and independent drain tubes | Surface films and printing defects can bridge regions |
| Orientation failure | Mark Z horizontal, gravity −Y, top alignment; keyed installation procedure | Out-of-level pipe and upside-down installation require rejection/testing |
| Drain before electrode activation | Electrode close to pocket entry; trial wick/dwell insert | Carrier is a holder envelope; final electrode/wick placement still needs detail design and weak-flow tests |
| Blockage | Removable holders, visible drains, challenge access and BYPASS witness | BYPASS may remain dry even with an ineffective collector |
| Rain ingress | Split shell with end drip guards and independent EXT | Drip guards are not a validated seal; horizontal runoff can enter end openings |
| Very weak leak | Characterize wetting threshold and retained volume; return UNRESOLVED when unsupported | Surface tension, evaporation and fouling can prevent activation |
| Maintenance compromises protection | Axial challenge ports offset from holders, removable service parts | Port closure, seals, attachment retention and repeated reassembly are release gates |

M05 nominal synthetic result remains **GUARD-5 missed 36/96 local leak cases versus 12/96 for multizone**. No mechanical improvement here is fitted back into M05 or claimed to reduce those counts. CAD alone proves neither capture efficiency nor environmental discrimination.

Pickup comparison: selected budget candidate Murata 7BB-27-4L0 is a passive piezo diaphragm, not a calibrated pipe-leak sensor. It needs high-input-impedance conditioning and strain-protected insulated coupling. PVDF contact film could be trialled with an appropriate high-impedance/charge interface; an IEPE accelerometer would require different constant-current conditioning and a budget review. Neither alternative is silently substituted. Identical mounts, contact force, coupling material and cable loading must be characterized. No claim of universal weak plastic-pipe leak audibility is supported.
