"""Ensure the amendment rejects unrelated source and incompatible API changes."""
import copy
import hashlib
import json
import unittest

from pre_m10_f01_sources import ROOT, extend_digest, manifest, previous_openapi, validate_manifest


class F01CompatibilityTests(unittest.TestCase):
    def test_exact_prior_digest(self):
        name = "services/api/hydro/notification_worker.py"
        row = manifest()["source_revisions"][name]
        self.assertEqual(extend_digest(name, row["baseline_sha256"]), row["sha256"])
        with self.assertRaises(AssertionError):
            extend_digest(name, "0" * 64)

    def test_out_of_scope_and_malformed_amendments(self):
        for name in ("simulations/run_all.py", "services/api/hydro/security.py", "../outside.py"):
            value = copy.deepcopy(manifest())
            value["source_revisions"][name] = next(iter(value["source_revisions"].values()))
            with self.assertRaises(AssertionError):
                validate_manifest(value)
        for key, replacement in (("sha256", "invalid"), ("reason", " ")):
            value = copy.deepcopy(manifest())
            next(iter(value["source_revisions"].values()))[key] = replacement
            with self.assertRaises(AssertionError):
                validate_manifest(value)

    def test_only_additive_category_changes(self):
        spec = json.loads((ROOT / "apps/web/contracts/implemented.openapi.json").read_text())
        baseline = json.loads((ROOT / "data/schemas/m09-acceptance-baseline.json").read_text())
        digest = hashlib.sha256(json.dumps(previous_openapi(spec), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, baseline["implemented_openapi_sha256"])
        self.assertIn("COMPLAINT_PROGRESS", spec["components"]["schemas"]["M07Notification"]["properties"]["event_category"]["enum"])
        spec["components"]["schemas"]["M07Notification"]["properties"]["event_category"]["enum"].remove("APPOINTMENT")
        with self.assertRaises(AssertionError):
            previous_openapi(spec)


if __name__ == "__main__":
    unittest.main()
