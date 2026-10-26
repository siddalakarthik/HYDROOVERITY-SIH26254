"""Explicit source revisions after M09; historical manifests remain immutable."""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    "services/api/tools/demo_backend.py",
    "scripts/check_m07_design.py",
    "scripts/check_m07b.py",
    "scripts/check_m07c.py",
    "scripts/check_m09.py",
})


def validate_changes(manifest):
    assert manifest["baseline_commit"] == "d772045ba6d44ddd1bbee1e4baf890c5786628d5"
    changes = manifest["source_revisions"]
    assert set(changes) == ALLOWED, "Unreviewed source revision scope"
    for name, change in changes.items():
        assert change["reason"].strip(), name
        for key in ("baseline_sha256", "sha256"):
            assert re.fullmatch(r"[0-9a-f]{64}", change[key]), name
        assert change["baseline_sha256"] != change["sha256"], name
    return changes


@lru_cache(maxsize=1)
def changes():
    return validate_changes(json.loads((ROOT / "data/schemas/pre-m10-source-revisions.json").read_text()))


def revised_digest(name, expected):
    change = changes().get(name)
    if change is not None:
        assert change["baseline_sha256"] == expected, f"Broken pre-M10 baseline chain: {name}"
        expected = change["sha256"]
    from pre_m10_f01_sources import extend_digest
    expected = extend_digest(name, expected)
    from pre_m10_revisit_sources import extend_digest as extend_revisit
    expected = extend_revisit(name, expected)
    from pre_m10_contact_sources import extend_digest as extend_contact
    return extend_contact(name, expected)
