"""Offline M05 producer. Output only allowlisted observations and detector results.

Run with the scientific environment, never with API credentials. Generator truth
is discarded in this process. The API image must not contain this package, the
generator configuration, or evaluator outputs.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from simulations.common import ROOT, LABEL, clean, digest, write_json
from simulations.hydraulics.model import generate as hydraulic
from simulations.hydraulics.detector import assess as watch
from simulations.acoustics.model import generate as capture
from simulations.acoustics.detector import assess as locate
from simulations.guard5.model import generate as collar
from simulations.guard5.detector import assess as guard
from .observations import watch_series, guard_series, ear_series

HYDRAULIC_NAMES = (
    "Normal operation", "Small modeled leak", "Larger modeled leak", "Demand change",
    "Reduced supply head", "Low pressure", "Supply OFF", "Supply FILLING",
    "Supply DRAINING", "Leak with demand change", "Meter drift and missing samples",
    "Modeled repair sequence",
)
ACOUSTIC_NAMES = (
    "Eligible span — first case", "Eligible span — second case", "Eligible span — third case",
    "Weak acoustic signal", "Wave-speed uncertainty", "Pump interference", "Reflection",
    "Multiple sources", "No pressure", "Weak signal in noise", "Gain and clipping",
    "Distance and attenuation",
)
GUARD_NAMES = (
    "Dry conditions", "Localized wetting A", "Localized wetting B", "Rain", "Dew",
    "Collection obstruction", "Bypass wetting", "Disconnected electrode", "Stuck wet",
    "Water migration", "Weak seepage", "Service challenge", "Drain blockage",
    "Local wetting with rain",
)


def produce():
    cfg = json.loads((ROOT / "simulations/scenarios/final_benchmark.json").read_text("utf-8"))
    # Exactly repeat-zero holdout observations used by the approved M05 runner.
    ts, ns = cfg["holdout_truth_seed"], cfg["holdout_observation_seed"]
    cases = []

    def add(code, name, series):
        cases.append({"code": code, "name": name, "data": series})

    for i, name in enumerate(HYDRAULIC_NAMES, 1):
        code = f"H{i:02}"
        obs, _ = hydraulic(code, ns + i)
        add(code, name, watch_series(obs, watch(obs, cfg["hydraulic"])))
    for i, name in enumerate(ACOUSTIC_NAMES, 1):
        code = f"A{i:02}"
        obs, _ = capture(code, ts + i * 1000, ns + i * 1000)
        add(code, name, ear_series(obs, locate(obs, cfg["acoustic"]), cfg["acoustic"]))
    for regime in cfg["guard"]["regimes"]:
        for i, name in enumerate(GUARD_NAMES, 1):
            code = f"G{i:02}"
            obs, pad, multi, _ = collar(code, ts + i * 1000, cfg["guard"], regime)
            add(code + "-" + regime, name + " / " + regime,
                guard_series(obs, guard(obs, cfg["guard"]), pad, multi))
    reference = json.loads((ROOT / "simulations/evaluation/reference_summary.json").read_text("utf-8"))
    for name, missing in (("comparable_repair", False), ("missing_post_evidence", True), ("incomplete_repair", False)):
        obs, _ = hydraulic("H12", 123, repair_fraction=.6 if name == "incomplete_repair" else 0,
                           missing_post=missing)
        prediction = watch(obs, cfg["hydraulic"])
        before = (obs.time_s >= 1500) & (obs.time_s < 2400)
        after = obs.time_s >= 2700
        valid = np.isfinite(obs.customer_outlet_lpm[after]).all()
        pre = float(np.mean(prediction["residual_lpm"][before]))
        post = float(np.mean(prediction["residual_lpm"][after])) if valid else None
        status = "NOT_VERIFIABLE" if not valid else "PASSED" if post < 1 and pre-post > 1 else "FAILED"
        approved = next(row for row in reference["integrated"] if row["case"] == name)
        assert status == approved["verification"]
        assert np.isclose(pre, approved["before_residual_lpm"], rtol=1e-9, atol=1e-9)
        assert post is None if approved["after_residual_lpm"] is None else np.isclose(
            post, approved["after_residual_lpm"], rtol=1e-9, atol=1e-9)
        cap, _ = capture("A01", 71099, 91099)
        acoustic_prediction = locate(cap, cfg["acoustic"])
        wet, pad, multi, _ = collar("G02", 71099, cfg["guard"], "nominal")
        collar_prediction = guard(wet, cfg["guard"])
        assert acoustic_prediction["outcome"] == approved["acoustic"]["outcome"]
        assert collar_prediction["outcome"] == approved["guard5"]["outcome"]
        add("V-" + name, name.replace("_", " "), {
            "module": "HYDRO-VERIFY", "label": LABEL, "outcome": status,
            "before_residual_lpm": pre, "after_residual_lpm": post,
            "watch": watch_series(obs, prediction),
            "ear": ear_series(cap, acoustic_prediction, cfg["acoustic"]),
            "guard": guard_series(wet, collar_prediction, pad, multi),
            "limitations": [
                "Modeled residual comparison under M05 assumptions, not an operational repair or independent field verification.",
                "Missing comparable post-evidence remains NOT_VERIFIABLE.",
                "Completing a work order never creates a verification outcome here.",
                "Independent WATCH, GUARD-5 and EAR scenario outputs joined as in M05; not a coupled fluid-acoustic model or synchronized field recording.",
            ],
        })
    source_files = [
        "simulations/" + module + "/" + file + ".py"
        for module in ("hydraulics", "acoustics", "guard5") for file in ("model", "detector")
    ]
    sources = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in source_files}
    # Historical aggregates are published M05 results, not per-case hidden labels.
    # These explicit sections retain unfavorable results and denominators.
    aggregate = {key: reference[key] for key in ("label", "profile", "hydraulics", "acoustics", "guard")}
    return clean({
        "schema_version": "M06-observations-1", "source_category": "SIMULATION",
        "label": LABEL, "algorithm_version": "M05-2",
        "configuration_hash": digest(cfg), "algorithm_source_hash": digest(sources),
        "reference_summary_hash": digest(reference), "historical_benchmark": aggregate,
        "cases": cases,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = produce()
    write_json(args.output, output)
    print(f"Exported {len(output['cases'])} observation-only scenarios; SHA256 {digest(output)}")


if __name__ == "__main__":
    main()
