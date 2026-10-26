"""Exact revisit amendment after green F01 main; historical manifests stay frozen."""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    "services/api/hydro/services/incidents.py",
    ".github/workflows/repository-integrity.yml",
    "scripts/pre_m10_sources.py",
    "scripts/check_pre_m10_f01.py",
})


def validate_manifest(value):
    assert value["baseline_commit"] == "008bd507c09352dcbb8098ec9812448693e0d99b"
    assert set(value["source_revisions"]) == ALLOWED, "Unexpected revisit revision scope"
    for name, change in value["source_revisions"].items():
        assert change["reason"].strip(), name
        for key in ("baseline_sha256", "sha256"):
            assert re.fullmatch(r"[a-f0-9]{64}", change[key]), name
        assert change["baseline_sha256"] != change["sha256"], name
    return value


@lru_cache(maxsize=1)
def manifest():
    return validate_manifest(json.loads((ROOT / "data/schemas/pre-m10-revisit-revisions.json").read_text(encoding="utf-8")))


def extend_digest(name, expected):
    change = manifest()["source_revisions"].get(name)
    if change is None:
        return expected
    assert change["baseline_sha256"] == expected, f"Broken revisit baseline chain: {name}"
    return change["sha256"]
