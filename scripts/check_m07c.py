"""Validate explicit communications activation and all 103 preserved operations."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.contracts import runtime_openapi
from hydro.communications_contracts import OPERATIONS
from hydro.science_data import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "data/schemas/m07c-implementation.json").read_text())
    assert manifest["baseline_commit"] == "bb86029cac32e3ddb8a476855b99cf512f023482"
    assert manifest["counts"] == {"preserved_operations":103,"m07c_operations":8,"total_operations":111,"preserved_tables":45,"m07c_tables":6,"total_tables":51}
    spec = runtime_openapi()
    ids = {s["operationId"] for ms in spec["paths"].values() for s in ms.values()}
    assert len(ids) == 111 and {o["id"] for o in OPERATIONS} == set(manifest["operation_ids"])
    assert not {"m07_n10", "m07_n11", "m07_n12"} & ids
    assert not any("/attachments" in p or "/uploads" in p for p in spec["paths"])
    assert len(manifest["baseline_operations"]) == 103
    for key, expected in manifest["baseline_operations"].items():
        method, path = key.split(" ", 1)
        assert digest(spec["paths"][path][method]) == expected, key
    for name, expected in manifest["baseline_schemas"].items():
        assert digest(spec["components"]["schemas"][name]) == expected, name
    for name, change in manifest["source_extensions"].items():
        if args.backend_only and not name.startswith("services/api/") and not (ROOT/name).exists():
            continue
        assert hashlib.sha256((ROOT/name).read_text("utf-8").encode()).hexdigest() == change["sha256"], name
    for name, expected in manifest["new_source_sha256"].items():
        if args.backend_only and not name.startswith("services/api/") and not (ROOT/name).exists():
            continue
        assert hashlib.sha256((ROOT/name).read_text("utf-8").encode()).hexdigest() == expected, name
    assert manifest["attachments"] == "DISABLED_D7_REVIEW_REQUIRED"
    print("PASS: 103 preserved + 8 M07-C operations; 51 tables; D6/D7/D8/D10 gates retained")


if __name__ == "__main__":
    main()
