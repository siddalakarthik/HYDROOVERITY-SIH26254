"""Record/check the complete canonical target against the tested M03 subset."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))

from hydro.contracts import INVENTORY, OPERATIONS
from hydro.repository import TABLES

TARGET = ROOT / "data/schemas/m03-implementation-matrix.json"


def matrix(tests):
    enabled = {op["id"] for op in OPERATIONS}
    operations = []
    for op in INVENTORY:
        active = op["id"] in enabled
        operations.append(
            {
                **{
                    k: op[k]
                    for k in (
                        "id",
                        "group",
                        "method",
                        "path",
                        "request",
                        "response",
                        "permission",
                        "table",
                    )
                },
                "status": "CODE_TESTED" if active else "DEFERRED",
                "positive_response_tests": sorted(tests.get(op["id"], [])) if active else [],
            }
        )
    tables = json.loads((ROOT / "data/schemas/m02-database-design.json").read_text())["tables"]
    return {
        "milestone": "M03",
        "provenance": "SYNTHETIC_INTEGRATION_ONLY; no physical or field trials",
        "canonical_operations": len(INVENTORY),
        "implemented_operations": len(enabled),
        "deferred_operations": len(INVENTORY) - len(enabled),
        "implemented_by_domain": dict(sorted(Counter(op["group"] for op in OPERATIONS).items())),
        "operations": operations,
        "tables": [
            {"name": t["name"], "status": "MIGRATED" if t["name"] in TABLES else "DEFERRED"}
            for t in tables
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.evidence:
        evidence = json.loads(args.evidence.read_text())
        if evidence["exit_status"] != 0 or evidence["failed"] or evidence.get("errors", 0):
            raise SystemExit("Failed evidence cannot establish implementation coverage")
        tests = evidence["operation_tests"]
    else:
        saved = json.loads(TARGET.read_text())
        tests = {op["id"]: op["positive_response_tests"] for op in saved["operations"]}
    result = matrix(tests)
    for op in result["operations"]:
        if op["status"] == "CODE_TESTED":
            assert op["positive_response_tests"], op["id"]
        for test in op["positive_response_tests"]:
            assert (ROOT / test.split("::")[0]).is_file(), test
    if args.check:
        assert json.loads(TARGET.read_text()) == result, "Implementation matrix drift"
    elif args.evidence:
        TARGET.write_text(json.dumps(result, indent=2) + "\n")
    else:
        raise SystemExit("Use --evidence to regenerate or --check to validate")
    print(
        f"PASS: {len(INVENTORY)} operations = {len(OPERATIONS)} tested + {len(INVENTORY) - len(OPERATIONS)} deferred; {len(TABLES)}/{len(result['tables'])} tables migrated"
    )


if __name__ == "__main__":
    main()
