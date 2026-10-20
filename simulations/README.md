# HYDROOVERITY scientific simulations

SIM-HYDRAULICS, SIM-ACOUSTICS and SIM-GUARD-5 are implemented and executed for M05. **All results are SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED.**

Use Python3.12 in an isolated environment and install requirements-m05.txt. From repository root:

```text
python -m pytest tests/unit/test_m05.py -q
python -m simulations.run_all --profile smoke
python -m simulations.run_all --profile ppt
python -m simulations.run_all --profile stress
```

The smoke run exercises every primary scenario once, PPT uses8 hydraulic/24 acoustic/12 collar repeats, and stress increases repeat counts. Stress is optional and has not been executed. Windows script scripts/run_m05.ps1 accepts -Python and -Profile, with a writable Matplotlib cache. See the [evidence report](../docs/testing/M05_SIMULATION_EVIDENCE_REPORT.md) for exact local paths, setup commands, versions, numerical results, all failure modes and limitations.

Generated outputs are ignored under results; eight1920×1080 PNG/SVG pairs plus captions are in results/ppt after the PPT run. Run `python -m simulations.figures simulations/results/ppt` to regenerate them solely from saved data. The committed evaluation/reference_summary.json is a small reviewed result summary. Other raw waveforms/truth/examples remain local and must never become ordinary dashboard exports.

Generator models produce observation-only dataclasses and separate truth; detectors accept only observations and threshold settings; evaluator modules own truth comparison. final_benchmark.json fixes independent development/final holdout seeds and preserves original thresholds; benchmark.json is preserved groundwork. No M02 schema/branch is imported, no live ingestion/backend is implemented, and no hardware is validated.
