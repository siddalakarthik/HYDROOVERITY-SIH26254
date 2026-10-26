"""Exact gated-contact transition after green revisit main; frozen history stays intact."""
import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The final reviewed builder writes the exact literal scope here before publication.
ALLOWED = frozenset({
    '.github/workflows/repository-integrity.yml',
    'apps/web/browser/communications.spec.ts',
    'apps/web/contracts/implemented.openapi.json',
    'apps/web/src/features/public.tsx',
    'apps/web/src/lib/generated.ts',
    'apps/web/src/lib/route-capabilities.json',
    'apps/web/tools/contracts.py',
    'scripts/check_m06.py',
    'scripts/check_m07a_implementation.py',
    'scripts/check_m07b.py',
    'scripts/check_m07c.py',
    'scripts/check_m09.py',
    'scripts/check_pre_m10_f01.py',
    'scripts/check_pre_m10_revisit.py',
    'scripts/check_repository_media.py',
    'scripts/pre_m10_f01_sources.py',
    'scripts/pre_m10_sources.py',
    'services/api/hydro/config.py',
    'services/api/hydro/contracts.py',
    'services/api/hydro/db.py',
    'services/api/hydro/routes.py',
    'services/api/tests/conftest.py',
    'services/api/tests/m09_acceptance.py',
    'services/api/tests/prem10_complaint_acceptance.py',
    'services/api/tests/test_communications.py',
    'services/api/tests/test_concurrency_resilience.py',
    'services/api/tests/test_foundation.py',
    'services/api/tests/test_schema_boundaries.py',
    'services/api/tests/test_workflow.py',
    'services/api/tools/verify_backend.py',
})
NEW = frozenset({
    "services/api/hydro/contact_policy.py", "services/api/hydro/project_contact.py",
    "services/api/migrations/versions/pre_m10_002.py",
    "services/api/tests/prem10_contact_acceptance.py",
    "services/api/tools/project_contact_operator.py", "services/api/tools/verify_prem10_contact.py",
})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_manifest(value):
    assert value["baseline_commit"] == "630b28cc396d29f03f5e9fb3f7ea076eecc86821"
    assert set(value["source_revisions"]) == ALLOWED, "Unexpected contact amendment scope"
    assert set(value["new_source_sha256"]) == NEW, "Unexpected new contact source"
    for name, row in value["source_revisions"].items():
        assert row["reason"].strip(), name
        for key in ("baseline_sha256", "sha256"):
            assert re.fullmatch(r"[a-f0-9]{64}", row[key]), name
        assert row["baseline_sha256"] != row["sha256"], name
    for name, expected in value["new_source_sha256"].items():
        assert re.fullmatch(r"[a-f0-9]{64}", expected), name
    for key in ("contact_operation_sha256", "contact_schema_sha256"):
        assert re.fullmatch(r"[a-f0-9]{64}", value[key]), key
    return value


@lru_cache(maxsize=1)
def manifest():
    return validate_manifest(json.loads((ROOT / "data/schemas/pre-m10-contact-revisions.json").read_text(encoding="utf-8")))


def extend_digest(name, expected):
    row = manifest()["source_revisions"].get(name)
    if row is None:
        return expected
    assert row["baseline_sha256"] == expected, f"Broken contact baseline chain: {name}"
    return row["sha256"]


def before_contact(spec):
    from pre_m10_realtime_sources import before_realtime
    previous = copy.deepcopy(before_realtime(spec))
    if "/public/contact" not in previous["paths"]:
        assert "ContactWrite" not in previous["components"]["schemas"]
        return previous
    assert digest(previous["paths"]["/public/contact"]) == manifest()["contact_operation_sha256"]
    assert digest(previous["components"]["schemas"]["ContactWrite"]) == manifest()["contact_schema_sha256"]
    del previous["paths"]["/public/contact"]
    del previous["components"]["schemas"]["ContactWrite"]
    return previous
