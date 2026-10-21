"""Record/check the complete canonical target against the tested M03 subset."""

import argparse
import ast
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))

from hydro.contracts import INVENTORY, OPERATIONS
from hydro.repository import TABLES

TARGET = ROOT / "data/schemas/m03-implementation-matrix.json"
MINIMUM_ACCEPTANCE_TESTS = 45


class TraceabilityError(ValueError):
    """Invalid evidence or a reviewable contract/coverage difference."""


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


@lru_cache
def validate_reference(reference):
    if not isinstance(reference, str) or not re.fullmatch(
        r"services/api/tests/test_[a-z0-9_]+\.py::test_[a-z0-9_]+(?:\[[^\r\n]+\])?",
        reference,
    ):
        raise TraceabilityError(f"Invalid executable test reference: {reference!r}")
    filename, name = reference.split("::")
    path = ROOT / filename
    if not path.is_file():
        raise TraceabilityError(f"Missing test source: {filename}")
    functions = {
        node.name
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if name.split("[", 1)[0] not in functions:
        raise TraceabilityError(f"Missing executable test function: {reference}")


def validate_mapping(tests, collected=None):
    if not isinstance(tests, dict) or not all(isinstance(k, str) for k in tests):
        raise TraceabilityError("operation_tests must be an object")
    enabled = {op["id"] for op in OPERATIONS}
    unknown = set(tests) - enabled
    missing = enabled - set(tests)
    if unknown:
        raise TraceabilityError(f"Unknown or deferred positive operation IDs: {sorted(unknown)}")
    if missing:
        raise TraceabilityError(f"Missing positive-response evidence: {sorted(missing)}")
    for oid, refs in tests.items():
        if not isinstance(refs, list) or not refs or not all(isinstance(r, str) for r in refs):
            raise TraceabilityError(f"Missing/invalid positive-response references: {oid}")
        if len(refs) != len(set(refs)):
            raise TraceabilityError(f"Duplicate positive-response references: {oid}")
        for reference in refs:
            validate_reference(reference)
            if collected is not None and reference not in collected:
                raise TraceabilityError(
                    f"Positive-response test was not collected: {oid}: {reference}"
                )
    return tests


def validate_evidence(evidence):
    if not isinstance(evidence, dict):
        raise TraceabilityError("Acceptance evidence must be an object")
    if evidence.get("fixture_provenance") != "SYNTHETIC_INTEGRATION_ONLY":
        raise TraceabilityError("Invalid acceptance fixture provenance")
    for name in ("failed", "errors", "skipped", "exit_status", "physical_trials", "field_trials"):
        if type(evidence.get(name)) is not int or evidence[name] != 0:
            raise TraceabilityError(f"Acceptance evidence requires {name}=0")
    count = evidence.get("collected")
    if type(count) is not int or count < MINIMUM_ACCEPTANCE_TESTS:
        raise TraceabilityError("Acceptance requires at least the original 45 tests")
    expected = {
        "implemented_operations": len(OPERATIONS),
        "deferred_operations": len(INVENTORY) - len(OPERATIONS),
        "positive_response_conformance": "PASS",
    }
    for key, value in expected.items():
        if evidence.get(key) != value:
            raise TraceabilityError(f"Invalid acceptance evidence field: {key}")
    checksum = evidence.get("backend_source_sha256")
    if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise TraceabilityError("Acceptance backend source checksum is missing/invalid")
    collected = evidence.get("collected_tests")
    if (
        not isinstance(collected, list)
        or not all(isinstance(r, str) for r in collected)
        or len(collected) != count
        or len(set(collected)) != count
    ):
        raise TraceabilityError("collected_tests must identify every actual collected test once")
    for reference in collected:
        validate_reference(reference)
    return validate_mapping(evidence.get("operation_tests"), set(collected))


def index(rows, key):
    if not isinstance(rows, list) or not all(isinstance(r, dict) and key in r for r in rows):
        raise TraceabilityError(f"Invalid matrix rows: {key}")
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise TraceabilityError(f"Duplicate matrix identifiers: {key}")
    return result


def describe_drift(saved, generated):
    """Safe metadata/test-name differences only; never request bodies or secrets."""
    if not isinstance(saved, dict):
        raise TraceabilityError("Saved matrix must be an object")
    count_keys = {
        "canonical_operations",
        "implemented_operations",
        "deferred_operations",
        "implemented_by_domain",
    }
    changes = {
        "counts": {
            k: {"saved": saved.get(k), "generated": generated.get(k)}
            for k in sorted(count_keys)
            if saved.get(k) != generated.get(k)
        },
        "operations": [],
        "tables": [],
        "other_fields": {},
    }
    before, after = index(saved.get("operations"), "id"), index(generated["operations"], "id")
    for oid in sorted(set(before) | set(after)):
        a, b = before.get(oid, {}), after.get(oid, {})
        metadata = {
            k: {"saved": a.get(k), "generated": b.get(k)}
            for k in sorted((set(a) | set(b)) - {"positive_response_tests"})
            if a.get(k) != b.get(k)
        }
        added = sorted(
            set(b.get("positive_response_tests", [])) - set(a.get("positive_response_tests", []))
        )
        removed = sorted(
            set(a.get("positive_response_tests", [])) - set(b.get("positive_response_tests", []))
        )
        if metadata or added or removed:
            changes["operations"].append(
                {"id": oid, "added_tests": added, "removed_tests": removed, "metadata": metadata}
            )
    before, after = index(saved.get("tables"), "name"), index(generated["tables"], "name")
    for name in sorted(set(before) | set(after)):
        if before.get(name) != after.get(name):
            changes["tables"].append(
                {"name": name, "saved": before.get(name), "generated": after.get(name)}
            )
    for key in sorted((set(saved) | set(generated)) - count_keys - {"operations", "tables"}):
        if saved.get(key) != generated.get(key):
            changes["other_fields"][key] = {
                "saved": saved.get(key),
                "generated": generated.get(key),
            }
    semantic = (
        changes["counts"]
        or changes["tables"]
        or changes["other_fields"]
        or any(op["metadata"] for op in changes["operations"])
    )
    classification = (
        "IDENTICAL"
        if saved == generated
        else "CONTRACT_OR_CLASSIFICATION"
        if semantic
        else "POSITIVE_RESPONSE_EVIDENCE"
        if changes["operations"]
        else "ORDERING_ONLY"
    )
    return {"classification": classification, **changes}


def check_matrix(saved, tests):
    generated = matrix(validate_mapping(tests))
    drift = describe_drift(saved, generated)
    if saved != generated:
        raise TraceabilityError("Implementation matrix drift:\n" + json.dumps(drift, indent=2))
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--diagnose", action="store_true", help="Read-only diff; does not certify evidence"
    )
    args = parser.parse_args()
    if args.evidence:
        evidence = json.loads(args.evidence.read_text())
        if args.diagnose:
            print(
                json.dumps(
                    describe_drift(
                        json.loads(TARGET.read_text()), matrix(evidence["operation_tests"])
                    ),
                    indent=2,
                )
            )
            return
        tests = validate_evidence(evidence)
    else:
        saved = json.loads(TARGET.read_text())
        enabled = {op["id"] for op in OPERATIONS}
        tests = {
            op["id"]: op["positive_response_tests"]
            for op in saved["operations"]
            if op["id"] in enabled
        }
    if args.diagnose:
        raise TraceabilityError("--diagnose requires --evidence; no files were changed")
    result = matrix(validate_mapping(tests))
    if args.check:
        check_matrix(json.loads(TARGET.read_text()), tests)
    elif args.evidence:
        TARGET.write_text(json.dumps(result, indent=2) + "\n")
    else:
        raise SystemExit("Use --evidence to regenerate or --check to validate")
    print(
        f"PASS: {len(INVENTORY)} operations = {len(OPERATIONS)} tested + {len(INVENTORY) - len(OPERATIONS)} deferred; {len(TABLES)}/{len(result['tables'])} tables migrated"
    )
    if not args.evidence:
        print("Contract/reference check only; current execution requires --evidence")


if __name__ == "__main__":
    try:
        main()
    except (TraceabilityError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from None
