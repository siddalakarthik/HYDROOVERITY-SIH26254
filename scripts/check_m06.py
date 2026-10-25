"""Check the M06 overlay without rewriting the accepted M02/M03/M07 contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.communications_contracts import OPERATIONS as COMMUNICATIONS
from hydro.contracts import runtime_openapi
from hydro.science_contracts import OPERATIONS
from hydro.science_data import load_catalogue, digest
from hydro.scheduling_contracts import ACTIVE as SCHEDULING


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-only", action="store_true")
    args = parser.parse_args()
    current = json.loads((ROOT/"data/schemas/m07c-implementation.json").read_text())
    manifest = json.loads((ROOT / "data/schemas/m06-implementation.json").read_text())
    assert manifest["baseline_commit"] == "1da657d59bccdb6b66fb7dd66cb9f8310c3e7931"
    spec = runtime_openapi()
    ids = {s["operationId"] for methods in spec["paths"].values() for s in methods.values()}
    assert len(ids - SCHEDULING - {o["id"] for o in COMMUNICATIONS}) == 77 and len(OPERATIONS) == 7
    scheduling = json.loads((ROOT / "data/schemas/m07b-implementation.json").read_text())
    assert manifest["counts"] == {"preserved_operations": 70, "m06_operations": 7, "total_operations": 77,
                                  "preserved_tables": 35, "m06_tables": 1, "total_tables": 36,
                                  "scenario_recordings": 69}
    assert set(manifest["operation_ids"]) == {o["id"] for o in OPERATIONS}
    for key, expected in manifest["baseline_operation_hashes"].items():
        method, path = key.split(" ", 1)
        assert digest(spec["paths"][path][method]) == expected, key
    assert len(manifest["baseline_operation_hashes"]) == 70
    matrix = json.loads((ROOT / "data/schemas/m03-implementation-matrix.json").read_text())
    for operation in matrix["operations"]:
        operation.pop("positive_response_tests", None)
    assert digest(matrix) == manifest["m03_classification_hash"], "M03 classification or contract changed"
    for name, expected in manifest["baseline_schema_hashes"].items():
        assert digest(spec["components"]["schemas"][name]) == scheduling["schema_deltas"].get(name,expected), name
    for name, expected in manifest["frozen_file_hashes"].items():
        if args.backend_only and not (ROOT / name).exists():
            continue
        # Canonical text hashes ignore checkout-specific CRLF conversion only.
        assert hashlib.sha256((ROOT/name).read_text("utf-8").encode()).hexdigest() == expected, name
    for name, expected in manifest["m07a_file_extensions"].items():
        if args.backend_only and not name.startswith("services/api/"):
            continue
        assert hashlib.sha256((ROOT/name).read_text("utf-8").encode()).hexdigest() == current["source_extensions"].get(name,{}).get("sha256",scheduling["source_extensions"].get(name,{}).get("sha256",expected)), name
    pins = json.loads((ROOT / "data/schemas/m06-observation-pins.json").read_text())
    catalogue = load_catalogue(ROOT / "data/samples/m06", pins["catalogue_sha256"])
    assert len(catalogue["cases"]) == 69
    forbidden = {"truth", "seed", "truth_seed", "observation_noise_seed", "hidden_label", "position_m", "artifact_path", "password"}
    def inspect(node):
        if isinstance(node, dict):
            assert not forbidden.intersection(node), forbidden.intersection(node)
            for value in node.values(): inspect(value)
        elif isinstance(node, list):
            for value in node: inspect(value)
    inspect(catalogue)
    assert not {"EvaluationResult", "SimulationRun", "RunOutput"}.intersection(spec["components"]["schemas"])
    print("PASS: 70 unchanged operations + 7 M06; 36 migrated tables; 69 pinned observation recordings; scientific and privacy boundaries preserved")


if __name__ == "__main__":
    main()
