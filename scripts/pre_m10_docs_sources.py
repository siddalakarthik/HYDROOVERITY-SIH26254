"""Narrow current-guide amendment; historical source inventories remain immutable."""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    "services/api/README.md", "apps/web/README.md",
    "scripts/pre_m10_devices_sources.py", "scripts/check_pre_m10_devices.py",
    ".github/workflows/repository-integrity.yml",
})
NEW = frozenset({
    "scripts/pre_m10_docs_sources.py", "scripts/check_pre_m10_docs.py",
    "scripts/test_pre_m10_docs.py",
})


def validate_manifest(value):
    assert value["baseline_commit"] == "496451f7dd4b215e3adba6ebefc4dd31b5d5c330"
    assert set(value["source_revisions"]) == ALLOWED, "Unreviewed guide revision scope"
    assert set(value["new_source_sha256"]) == NEW, "Unexpected documentation checker source"
    for name, row in value["source_revisions"].items():
        assert row["reason"].strip(), name
        assert row["baseline_sha256"] != row["sha256"], name
        for key in ("baseline_sha256", "sha256"):
            assert re.fullmatch(r"[0-9a-f]{64}", row[key]), name
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in value["new_source_sha256"].values())
    return value


@lru_cache(maxsize=1)
def manifest():
    return validate_manifest(json.loads((ROOT / "data/schemas/pre-m10-docs-revisions.json").read_text(encoding="utf-8")))


def extend_digest(name, expected):
    row = manifest()["source_revisions"].get(name)
    if row is None:
        return expected
    assert row["baseline_sha256"] == expected, f"Broken documentation source chain: {name}"
    return row["sha256"]
