# M05 simulation evidence report

**All results are simulated. Physical sensor performance and field reliability remain unverified.**

HYDROOVERITY / Team TARK / SIH26254; issue #5. Three engines executed locally under Python3.12.14: WNTR1.4.0 with EPANET2.2 PDA, NumPy2.5.4, SciPy1.18.1, Pandas3.0.6, Matplotlib3.11.2, pytest9.1.1. Exact wheels are pinned in simulations/requirements-m05.txt. No hardware or field trial occurred. The dedicated M05 branch starts from stable main7590a65 and contains no M02 changes.

## Models and limits

Hydraulics: seven nodes (reservoir plus six junctions), six branched pipes, demand at D1/D2/D3; Hazen–Williams roughness130 (assumed, not measured), pipe lengths100–150m and diameters65–150mm. Controlled reservoir head30m represents a supply boundary, not a calibrated pump curve. EPANET2.2 pressure-driven demand has minimum0m, required15m and exponent0.5; emitter coefficient Cd A sqrt(2g), Cd0.62, SI units. Two candidate emitter nodes L1/L2 and areas1e-7/5e-6m². The sector boundary is inlet IN minus the sum of terminal customer-meter edges C1/C2/C3. Customer demand is already included there; never subtract twice. Storage is absent for solved snapshots. OFF/FILLING/DRAINING signals are labeled phenomenological abstractions, not a pressurized EPANET solution or trapped-air/water-hammer simulation. Independent operating points are cached, not fabricated by subtracting array values.

Hydraulic observations contain time, available pressure/inlet/customer flows, pump command, storage-known flag, meter uncertainty and validity. Truth labels never enter either detector. Meter noise sigma0.25L/min and pressure noise sigma0.005bar are assumed. The fixed baseline ORs declared pressure-drop/inlet-rise/residual thresholds; WATCH qualifies measured state, pressure, validity/storage context, adapts a nonanomalous residual EWMA and requires3 samples. It reports unexplained-loss suspicion, not proven leak origin. All thresholds are in the frozen benchmark configuration. The initial fixed reference uses the first10 samples and is vulnerable to OFF/FILLING startup; this is a limitation of this specific baseline, not evidence that every fixed detector is inferior. With meters at all terminal outlets, demand is known here; results do not transfer to unknown customer demand/storage. Faults/pressure collapse retain an independent review lane.

Acoustics: one common4096Hz sample grid,2s records, stochastic80–1000Hz source, fractional spectral delays, frequency-dependent attenuation, distinct endpoint noise and sensor filtering/gain, coherent pump tones, multipath, multiple sources and clipping. Nominal speed250–450m/s and span15m (10–25m for A12) are illustrative assumptions, not measured material constants. Whole-record filtered correlation and GCC-PHAT use identical immutable captures; qualified inference adds four-window consistency, peak ratio, RMS/correlation, path/clock/pressure gates, timing/length/speed bounds and abstention. No trained classifier or measured probability is claimed. Peak windows are dependent and intervals are engineering bounds, not calibrated confidence intervals. FFT delays use a periodic finite record; they omit nonlinear source physics, actual transducer coupling, plastic-pipe dispersion modes and nonstationary propagation. Simple coherent pump/multipath models cannot represent all real signatures.

GUARD-5: exactly A/B/C/EXT/BYPASS,1s lumped-volume steps for180s,0.18mL wet threshold,12%/step nominal drainage, bounded evaporation and optional compartment migration. Input equals retained+drained+evaporated within numerical tolerance. Collection/rain-intrusion assumptions vary from unfavorable0.2/0.4 through nominal0.6/0.12 to favorable0.9/0.02 with seeded efficiency variation. Local leak rate0.15mL/s, low-volume0.001mL/s, external rain0.25mL/s and service injection0.04mL/s for10s are assumptions requiring future calibration. No 3D geometry or validated CFD is represented. Protected wetness without EXT yields LOCAL_SUSPECT; EXT supports environmental/ambiguous interpretation and BYPASS without protected wetness supports a collection review. These rules can be wrong. All unsupervised channels retain UNKNOWN electrical health; supervised disconnect control only carries an explicitly available DISCONNECTED observation.

The pad receives one retained-volume wet bit; the conventional multizone baseline receives three independent unguarded volume/wet observations and uses an environmental witness veto. Both have the same threshold/drainage and underlying input water as GUARD-5, but their physical transfer models intentionally differ: the pad collects all incident water; unguarded multizone divides external water between two zones; GUARD-5 assumes protected capture/witness/bypass routing. Faults are applied to equivalent baseline channels too. The third conventional zone has no separate incoming route in this simplified geometry; it adds no useful information. This limits claims about real competing systems. Service awareness is exclusive to the proposed design; its maintenance event may be a wetness alarm to baselines. Present baseline outputs as candidate leak declarations for scoring, not certified products.

## Executed catalogue and methodology

All H01–H12, A01–A12 and G01–G14 execute in development and holdout sets. H01 normal demand; H02 small leak; H03 larger leak; H04 demand rise; H05 source-head change; H06 low pressure; H07 OFF; H08 recovery; H09 draining; H10 leak+demand; H11 noise/drift/missing values; H12 repair. A01–03 source near A/center/B; A04 weak SNR; A05 wrong assumed speed; A06 pump; A07 multipath; A08 two sources; A09 no pressure; A10 weak source; A11 gain/clipping; A12 span/attenuation. G01 dry; G02 local A; G03 local B; G04 rain; G05 condensation; G06 blockage; G07 bypass; G08 disconnected; G09 stuck wet; G10 migration; G11 collector miss; G12 service; G13 partial drain block; G14 rain+local leak. G03 uses B; a separate C-only fitting scenario is not included. Service-port tests show response, not healthy collection geometry.

Development seeds17011/37013. Original prototype holdout71023/91033 was inspected during smoke/baseline correctness work, so it is not described as a fully blind final validation. Those preliminary results remain in ignored results/prototype_review. Final holdout81023/101033 was fixed in final_benchmark.json after those corrections; original thresholds were preserved without tuning. Final PPT profile uses8 hydraulic repeats/case (noise variation),24 acoustic repeats/case (source speed/position plus noise),12 collar repeats/case/regime (collection variation). Counts:96 hydraulic scenario-events per algorithm,288 acoustic captures (264 eligible,24 no-pressure excluded with reason),504 collar scenario/regime events per detector. These are conditional synthetic trials, not a random sample of real networks. Repeated trials share one geometry/model and do not justify population-wide accuracy. Stress profile exists but was not executed; optional animation was deferred.

Truth is restricted to generator return objects, evaluator modules and evaluation result files. Observation dataclasses omit label/position/seed, detectors do not import generator models, captures are immutable, and all methods receive the same recordings. Scenario IDs/truth-bearing example bundles and manifests belong to privileged local evaluation, never an ordinary dashboard. Detector settings are passed as threshold subsets; complete generator configs/seeds must not be sent to client inference. No deployed credential/OS permission enforcement is claimed for these local files.

## Executed numerical results

| Hydraulic method | TP | FP | FN | TN | Precision | Recall | F1 | Median detected delay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fixed | 24 | 56 | 8 | 8 | 0.300 | 0.750 | 0.429 | 0s |
| WATCH | 24 | 8 | 8 | 56 | 0.750 | 0.750 | 0.750 | 120s |

Leak detection is counted only when an alarm overlaps the true leak period; pre-event alarms are counted separately (fixed80 sample alarms; WATCH0). Nonleak false alarms are per scenario-cycle, not per independent sample:56/64 nonleak cycles fixed vs8/64 WATCH,64 nominal simulated nonleak hours per detector. WATCH is unresolved for21.04% of sample periods. H02 small leak is missed, H11 drift generates false suspicion. No-leak H01 and demand-rise H04 pass the WATCH controls. No solver failure occurred in the benchmark; maximum solved balance error 3.1e-06L/min. Injected solver failure is tested separately and becomes INVALID_SOLVER_RESULT.

Acoustics: 190/264 eligible captures accepted (71.97%); 74 unresolved. Conditional Wilson95% interval for coverage 66.27%–77.04%. Accepted-case median error 0.000797m and P95 0.9285m. Such tiny nominal-model median errors are artifacts of a shared idealized source/transfer law and do not establish submillimetre real hardware precision. 184/190 accepted cases within1m (96.84%); 184/264 of ALL eligible cases correctly located within1m (69.70%), with unresolved counted as not located. All-case success Wilson interval 63.90%–74.93%. No finite point error is invented for unresolved cases. **20 accepted intervals exclude truth**, so qualification is not a reliability guarantee. Baseline CC/PHAT all-eligible median errors 0.000780/0.001443m; both always return an in-search-range candidate under pressure and cannot express this abstention policy. They are not outperformed on median error merely because qualification rejects difficult cases.

Unmodeled relative channel skew0.25/1/4ms produced approximately0.039/0.158/0.634m error on the declared control capture. All were still accepted: common-clock acquisition and characterized analog delays matter. Wrong-speed A05 generates confident errors. Pump/multiple-source captures can abstain. Binomial intervals are conditional on independent RNG trials of this fixed design; model uncertainty is much larger than their statistical width.

| GUARD condition (168 events each detector) | Detector | TP | FP | FN | TN | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| unfavorable | pad | 84 | 36 | 12 | 36 | 0.778 |
| unfavorable | multizone | 84 | 24 | 12 | 48 | 0.824 |
| unfavorable | guard5 | 35 | 12 | 61 | 60 | 0.490 |
| nominal | pad | 84 | 36 | 12 | 36 | 0.778 |
| nominal | multizone | 84 | 24 | 12 | 48 | 0.824 |
| nominal | guard5 | 60 | 12 | 36 | 60 | 0.714 |
| favorable | pad | 84 | 36 | 12 | 36 | 0.778 |
| favorable | multizone | 84 | 24 | 12 | 48 | 0.824 |
| favorable | guard5 | 60 | 12 | 36 | 60 | 0.714 |

Nominal GUARD-5 reduces false declarations12 vs multizone24 but misses36 vs12 local leaks; its F1 is lower. Under unfavorable capture it misses61/96 local events; apparent gains disappear. Collection-blockage sensitivity is poor: nominal0/24 flagged; unfavorable3/24. All168/regime events retain unknown electrical health. Nominal service challenge12/12 response observed, but that does not prove electrode health, drain behavior or real collector efficiency. Mass-accounting error <= 1.75e-13mL. Stuck wet is an important false suspicion; disconnected dry is not identified without supervised evidence. No claim of GUARD-5 superiority is supported.

Integrated output joins actual independent engine results into three labeled simulated event timelines: comparable intervention PASSED; remaining modeled leak FAILED; missing post-repair data NOT_VERIFIABLE. Verification uses measured-synthetic residuals, not repair truth labels. The same operating head/demand/noise validity is used for comparable windows. This is an exported illustration, not a coupled hydraulic-to-acoustic energy model, persistent incident backend or real worker action.

## Tests, reproduction and traceability

38 numerical/unit tests passed locally,0 failed at final execution. Coverage includes EPANET balance, controlled demand/OFF cases, explicit solver invalidity, TDOA signs/midpoint/fractional delay, signal/path/clock/pressure/invalid-capture gates, speed sensitivity, five channels/mass/fault/service behavior, seed and detector-input separation, immutable common recordings, timing bias and metric denominators. Tests verify software/model consistency only. Two full PPT runs are compared by check_m05_reproducibility.py: all numerical outputs must match exactly on this environment; case counts, source hashes and1920×1080 PNG/SVG pairs are checked. Cross-platform floating-point/solver results may differ slightly; use physical tolerances from tests rather than promising byte-identical files across OS. Foundation/whitespace checks and publication status are recorded in the completion note.

Working Python executable: `C:\Users\siddala karthik\Documents\Codex\2026-10-20\you-are-joining-my-engineering-project\work\m05-py312\Scripts\python.exe`. The old3.14 environment with3.12 binary wheels was preserved, not reused. A fresh environment was created with bundled Python3.12.14; ensurepip was unavailable, so the bundled pip's --python target installed fresh matching wheels. Matplotlib cache and solver TEMP were redirected into workspace directories because the default font cache lacked write access. Import/version checks and actual EPANET runs, rather than install status, established recovery.

Portable setup from repository root, with a working Python3.12 interpreter:

```text
python3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r simulations/requirements-m05.txt
.venv/Scripts/python.exe -m pytest tests/unit/test_m05.py -q
.venv/Scripts/python.exe -m simulations.run_all --profile smoke
.venv/Scripts/python.exe -m simulations.run_all --profile ppt
.venv/Scripts/python.exe -m simulations.run_all --profile ppt --output simulations/results/reproduce
.venv/Scripts/python.exe scripts/check_m05_reproducibility.py simulations/results/ppt simulations/results/reproduce
.venv/Scripts/python.exe -m simulations.figures simulations/results/ppt
python scripts/check_repository.py
git diff --check
```

Linux uses .venv/bin/python. On Windows the helper scripts/run_m05.ps1 accepts -Python with the exact absolute executable and -Profile; it redirects Matplotlib cache. Set TEMP/TMP to a writable workspace directory if required. No GPU, cloud, website, database or M02 contract implementation is needed. Typical PPT execution took seconds/tens of seconds on this machine; no measured hardware power/throughput claim follows.

Generated results stay ignored under simulations/results. Small curated summary is committed at simulations/evaluation/reference_summary.json; source configs/scripts and dependency locks regenerate raw arrays and figures. Per-run manifest records executable/platform/dependencies/config+hash/algorithm version/source hash/current Git commit. Before source is committed, the commit identifies the baseline; source hash identifies the uncommitted implementation. A postcommit rerun records the final source commit. Evaluation raw truth and seeds are never ordinary dashboard exports. Optional stress and animation were not run.

Eight PNG/SVG pairs, with captions and traceability JSON, are in simulations/results/ppt:

1. 01_hydraulic_network — saved EPANET network/pressure/emitter truth.
2. 02_supply_timeline — H12 pressure/flows plus H04/H06/H09 controls.
3. 03_hydraulic_benchmark — all hydraulic holdout confusion counts.
4. 04_acoustic_localization — saved A01 recording/correlation/interval and evaluator truth.
5. 05_acoustic_reliability — per-case acoustic acceptance/wrong intervals/error.
6. 06_guard5_timelines — G02 local, G04 rain, G06 blockage and G12 service five-channel data.
7. 07_guard5_comparison — all regimes' false/missed counts, unknown-health disclosure.
8. 08_integrated_verification — actual joined engine outputs, simulated interventions and all three verification outcomes.

Every figure is generated from saved summary/evaluation/examples files; renderer performs no new simulation. Figure source hashes are in figure_traceability.json. PNGs are1920×1080; SVG text/paths are editable. Keep captions/limitations when inserting in slides. For six slides prefer01 (real network),04 (physics),05 (coverage/wrong decisions),06 (distinct five channels),08 (verification);03 can replace01 if numerical detection comparison is central. Do not hide the acoustic20 wrong intervals or GUARD-5 missed-event tradeoff.

## Claims and references

Safe PPT claim: three executable reproducible software simulation engines; EPANET pressurized balance; fair same-input acoustic methods with coverage and errors; assumed five-path water accounting and negative comparisons; an independent simulated verification outcome. All depend on declared assumptions.

Prohibited claim: measured detection accuracy, physically located leak, validated collar collection, tap-proven passive audibility, universal plastic-pipe wave speed, field reliability/savings, patent novelty, commercial superiority, battery lifespan or real repaired pipeline. Hardware construction, supervision electronics, actual sensor/clock/analog delay characterization, passive source audibility, geometry/drain tests and blind controlled/field trials remain required. ₹60,000 materials ceiling remains; no purchase occurred.

Primary references support model choices, not our chosen coefficients or claimed performance:

- [EPA WNTR hydraulic simulation](https://usepa.github.io/WNTR/hydraulics.html): EPANET2.2 and pressure-dependent demand validity.
- [EPA EPANET2.2 manual](https://usepa.github.io/EPANET2.2/): hydraulic head/flow, emitters and analysis limits.
- [Almeida et al.,2014, acoustic pipe/sensor filtering experiment](https://pubmed.ncbi.nlm.nih.gov/24658622/): filtering matters in plastic-pipe leak signals; our synthetic transfer is not a reproduction of that test.
- [In-situ wave-velocity research](https://www.sciencedirect.com/science/article/pii/S0022460X15004976): variable effective speed/attenuation constrain localization. The250–450m/s sweep is illustrative rather than a universally supported pipe-material range.

Unresolved implementation scope: no rapid two-phase hydraulics, no calibrated probability/confidence, no validated source spectral model, no full collar physics, no cloud/backend integration. These limitations are retained rather than replaced with favorable manufactured percentages.
