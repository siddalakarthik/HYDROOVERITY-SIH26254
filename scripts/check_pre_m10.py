"""Validate current completion bookkeeping without rewriting historical evidence."""
import hashlib
import json
from collections import Counter
from pathlib import Path

from pre_m10_sources import changes

ROOT = Path(__file__).resolve().parents[1]


def main():
    historical = json.loads((ROOT / "docs/testing/m09-traceability.json").read_text())
    register = json.loads((ROOT / "docs/testing/pre-m10-completion.json").read_text())
    items = register["items"]
    current = {row["id"]: row for row in items}
    assert len(current) == len(items), "Duplicate requirement IDs"
    baseline = historical["m02_cases"] + historical["m09_risks"]
    assert len(historical["m02_cases"]) == 40 and len(historical["m09_risks"]) == 8
    assert Counter(row["result"] for row in historical["m02_cases"]) == {
        "PASS": 21, "BLOCKED": 13, "NOT IMPLEMENTED": 6,
    }
    for old in baseline:
        row = current[old["id"]]
        assert row["historical_status"] == old["result"], old["id"]
        assert row["requirement"] == old["requirement"], old["id"]
    states = {"PASS", "FAIL", "BLOCKED", "NOT IMPLEMENTED", "NOT TESTED", "NOT APPLICABLE"}
    for row in items:
        assert row["current_status"] in states and row["historical_status"] in states
        for key in ("root_cause", "required_implementation", "required_test",
                    "dependency_or_approval", "risk", "source_files", "evidence", "remaining_limitations"):
            assert row[key], (row["id"], key)
        assert "completion_commit" in row and "completion_pr" in row
        for name in row["source_files"]:
            assert (ROOT / name).is_file(), name
        if row["current_status"] == "NOT APPLICABLE":
            assert row.get("scope_reason"), row["id"]
    for name, change in changes().items():
        actual = hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert actual == change["sha256"], name
    print(f"PASS: original 40 + 8 risks, {len(items)} register items, explicit source revisions")


if __name__ == "__main__":
    main()
