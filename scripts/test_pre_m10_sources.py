"""Reject stale, malformed and out-of-scope baseline amendments."""
import copy
import json
import unittest
from unittest.mock import patch

from pre_m10_sources import ROOT, revised_digest, validate_changes


class SourceRevisionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "data/schemas/pre-m10-source-revisions.json").read_text())

    def test_exact_previous_digest_required(self):
        changes = validate_changes(self.manifest)
        name = "services/api/tools/demo_backend.py"
        with patch("pre_m10_sources.changes", return_value=changes):
            self.assertEqual(revised_digest(name, changes[name]["baseline_sha256"]), changes[name]["sha256"])
            with self.assertRaises(AssertionError):
                revised_digest(name, "0" * 64)

    def test_scientific_files_cannot_be_amended(self):
        self.manifest["source_revisions"]["simulations/guard5/model.py"] = copy.deepcopy(
            self.manifest["source_revisions"]["services/api/tools/demo_backend.py"]
        )
        with self.assertRaises(AssertionError):
            validate_changes(self.manifest)

    def test_unlisted_source_remains_pinned(self):
        self.assertEqual(revised_digest("simulations/unchanged.py", "a" * 64), "a" * 64)

    def test_missing_reason_or_digest_is_rejected(self):
        for key, value in (("reason", ""), ("sha256", "invalid")):
            candidate = copy.deepcopy(self.manifest)
            candidate["source_revisions"]["services/api/tools/demo_backend.py"][key] = value
            with self.assertRaises(AssertionError):
                validate_changes(candidate)


if __name__ == "__main__":
    unittest.main()
