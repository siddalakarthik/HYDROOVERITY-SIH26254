"""Reject stale or unrelated revisit source amendments."""
import copy
import unittest
from pre_m10_revisit_sources import extend_digest, manifest, validate_manifest


class RevisitRevisionTests(unittest.TestCase):
    def test_exact_before_digest(self):
        name = "services/api/hydro/services/incidents.py"
        row = manifest()["source_revisions"][name]
        self.assertEqual(extend_digest(name, row["baseline_sha256"]), row["sha256"])
        with self.assertRaises(AssertionError):
            extend_digest(name, "0" * 64)

    def test_scope_and_metadata(self):
        for name in ("simulations/guard5/model.py", "services/api/hydro/security.py", "../outside.py"):
            value = copy.deepcopy(manifest())
            value["source_revisions"][name] = next(iter(value["source_revisions"].values()))
            with self.assertRaises(AssertionError):
                validate_manifest(value)
        for key, replacement in (("sha256", "invalid"), ("reason", " ")):
            value = copy.deepcopy(manifest())
            next(iter(value["source_revisions"].values()))[key] = replacement
            with self.assertRaises(AssertionError):
                validate_manifest(value)

    def test_unlisted_source_stays_pinned(self):
        self.assertEqual(extend_digest("simulations/unchanged.py", "a" * 64), "a" * 64)


if __name__ == "__main__":
    unittest.main()
