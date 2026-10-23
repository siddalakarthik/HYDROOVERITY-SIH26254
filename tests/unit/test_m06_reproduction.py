"""Reproduce all 69 approved observation-only cases using unchanged M05 engines."""
import json
import math

from simulations.common import ROOT
from simulations.integration.produce import produce


def equivalent(actual, expected, path="root"):
    if isinstance(expected, float):
        assert isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-8), path
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            equivalent(actual[key], expected[key], path + "." + key)
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, (a, b) in enumerate(zip(actual, expected)):
            equivalent(a, b, path + f"[{index}]")
    else:
        assert actual == expected, path


def test_all_observation_and_detector_results_reproduce():
    regenerated = produce()
    root = ROOT / "data/samples/m06"
    index = json.loads((root / "catalogue.json").read_text())
    assert len(regenerated["cases"]) == len(index["case_codes"]) == 69
    for case in regenerated["cases"]:
        equivalent(case, json.loads((root / (case["code"] + ".json")).read_text()), case["code"])
    equivalent(regenerated["historical_benchmark"], index["historical_benchmark"])
    assert regenerated["configuration_hash"] == index["configuration_hash"]
    assert regenerated["reference_summary_hash"] == index["reference_summary_hash"]
