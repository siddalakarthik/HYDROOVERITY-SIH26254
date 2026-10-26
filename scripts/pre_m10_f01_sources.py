"""Reviewable F01-only source and additive schema transition after foundation PR #23."""
import copy
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    ".github/workflows/repository-integrity.yml",
    "apps/web/browser/communications.spec.ts",
    "apps/web/contracts/implemented.openapi.json",
    "apps/web/src/features/communications.tsx",
    "apps/web/src/lib/generated.ts",
    "scripts/check_m06.py", "scripts/check_m07a_implementation.py",
    "scripts/check_m09.py", "scripts/check_pre_m10.py", "scripts/pre_m10_sources.py",
    "services/api/hydro/communications_contracts.py", "services/api/hydro/db.py",
    "services/api/hydro/notification_worker.py",
    "services/api/tests/m09_acceptance.py", "services/api/tests/test_communications.py",
    "services/api/tests/test_concurrency_resilience.py",
    "services/api/tests/test_foundation.py", "services/api/tests/test_workflow.py",
})


def validate_manifest(value):
    assert value["baseline_commit"] == "848c1c8a1dbf72f980c1f58454a41d0bd332eab8"
    assert set(value["source_revisions"]) == ALLOWED, "Unexpected F01 revision scope"
    for name, change in value["source_revisions"].items():
        assert change["reason"].strip(), name
        for key in ("baseline_sha256", "sha256"):
            assert re.fullmatch(r"[a-f0-9]{64}", change[key]), name
        assert change["baseline_sha256"] != change["sha256"], name
    return value


@lru_cache(maxsize=1)
def manifest():
    value = json.loads((ROOT / "data/schemas/pre-m10-f01-revisions.json").read_text())
    return validate_manifest(value)


def extend_digest(name, expected):
    change = manifest()["source_revisions"].get(name)
    if change is None:
        return expected
    assert change["baseline_sha256"] == expected, f"Broken F01 baseline chain: {name}"
    return change["sha256"]


def previous_openapi(spec):
    """Remove only the explicitly added opt-in category, then compare the entire old API."""
    from pre_m10_contact_sources import before_contact
    previous = copy.deepcopy(before_contact(spec))
    schemas = previous["components"]["schemas"]
    for name in ("M07NotificationPreferences", "M07NotificationPreferencesWrite"):
        categories = schemas[name]["properties"]["event_categories"]
        assert categories["items"]["enum"] == [
            "SERVICE_PROGRESS", "APPOINTMENT", "WORK_ASSIGNMENT", "SERVICE_FEEDBACK", "COMPLAINT_PROGRESS",
        ]
        assert categories["maxItems"] == 5
        categories["items"]["enum"].remove("COMPLAINT_PROGRESS")
        categories["maxItems"] = 4
    category = schemas["M07Notification"]["properties"]["event_category"]
    assert category["enum"] == [
        "SERVICE_PROGRESS", "APPOINTMENT", "WORK_ASSIGNMENT", "SERVICE_FEEDBACK", "COMPLAINT_PROGRESS",
    ]
    category["enum"].remove("COMPLAINT_PROGRESS")
    return previous
