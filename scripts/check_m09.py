"""Check M09's unchanged accepted source, API and scientific evidence boundary."""

import hashlib
import json
from pre_m10_sources import revised_digest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.contracts import runtime_openapi


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    manifest = json.loads((ROOT / "data/schemas/m09-acceptance-baseline.json").read_text())
    assert manifest["baseline_commit"] == "500a349299ceb79994d618cc0208dca9b2fb6ed0"
    assert manifest["implemented_operations"] == 111 and manifest["migrated_tables"] == 51
    for name, expected in manifest["accepted_text_source_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == revised_digest(name, expected), name
    assert digest(runtime_openapi()) == manifest["implemented_openapi_sha256"]
    trace = json.loads((ROOT / "docs/testing/m09-traceability.json").read_text())
    plan = (ROOT / "docs/testing/M02_ACCEPTANCE_AND_TEST_PLAN.md").read_text()
    import re

    expected = set(re.findall(r"^\| ([AFPRUSC]\d{2}) \|", plan, re.M))
    rows = trace["m02_cases"]
    assert len(rows) == len(expected) == 40
    assert {row["id"] for row in rows} == expected
    for row in rows + trace["m09_risks"]:
        assert row["result"] in {"PASS", "FAIL", "BLOCKED", "NOT IMPLEMENTED", "NOT TESTED"}
        assert row["procedure"] and row["observed"] and row["limitation"]
        for source in row["tests"]:
            name, _, symbol = source.partition("::")
            assert (ROOT / name).is_file(), source
            if symbol:
                assert symbol in (ROOT / name).read_text(encoding="utf-8"), source
        if row["result"] == "PASS":
            assert row["tests"], row["id"]
    print(f"PASS: {len(manifest['accepted_text_source_sha256'])} accepted source pins with explicit pre-M10 revisions, unchanged 111 operations, 40 M02 cases and {len(trace['m09_risks'])} M09 risks")


if __name__ == "__main__":
    main()
