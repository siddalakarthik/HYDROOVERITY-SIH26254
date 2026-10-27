"""Reject unrelated or broken historical-source amendments."""
import copy
import unittest
from pre_m10_docs_sources import extend_digest, manifest, validate_manifest


class DocumentationBoundaryTests(unittest.TestCase):
    def test_unrelated_source_rejected(self):
        value = copy.deepcopy(manifest())
        value["source_revisions"]["services/api/hydro/auth.py"] = next(iter(value["source_revisions"].values()))
        with self.assertRaises(AssertionError):
            validate_manifest(value)

    def test_missing_new_checker_rejected(self):
        value = copy.deepcopy(manifest())
        value["new_source_sha256"].pop("scripts/check_pre_m10_docs.py")
        with self.assertRaises(AssertionError):
            validate_manifest(value)

    def test_unrelated_expected_hash_is_preserved(self):
        self.assertEqual(extend_digest("simulations/guard5/model.py", "a" * 64), "a" * 64)

    def test_wrong_historical_hash_rejected(self):
        with self.assertRaises(AssertionError):
            extend_digest("apps/web/README.md", "0" * 64)
        row = manifest()["source_revisions"]["apps/web/README.md"]
        self.assertEqual(extend_digest("apps/web/README.md", row["baseline_sha256"]), row["sha256"])


if __name__ == "__main__":
    unittest.main()
