"""Reject unrelated source amendments and changes to the frozen contact contract."""
import copy
import json
import unittest

from pre_m10_contact_sources import ROOT, before_contact, digest, extend_digest, manifest, validate_manifest


class ContactCompatibilityTests(unittest.TestCase):
    def test_exact_before_digest_and_scope(self):
        value = manifest()
        name = "services/api/hydro/routes.py"
        row = value["source_revisions"][name]
        self.assertEqual(extend_digest(name, row["baseline_sha256"]), row["sha256"])
        with self.assertRaises(AssertionError):
            extend_digest(name, "0" * 64)
        for name in ("simulations/guard5/model.py", "../outside.py"):
            bad = copy.deepcopy(value)
            bad["source_revisions"][name] = row
            with self.assertRaises(AssertionError):
                validate_manifest(bad)

    def test_whole_previous_api_is_reconstructed(self):
        spec = json.loads((ROOT / "apps/web/contracts/implemented.openapi.json").read_text(encoding="utf-8"))
        self.assertEqual(digest(before_contact(spec)), manifest()["previous_openapi_sha256"])
        spec["paths"]["/public/contact"]["post"]["security"] = []
        with self.assertRaises(AssertionError):
            before_contact(spec)

    def test_metadata_and_new_source_scope(self):
        value = copy.deepcopy(manifest())
        value["new_source_sha256"]["services/api/hydro/unsafe.py"] = "a" * 64
        with self.assertRaises(AssertionError):
            validate_manifest(value)
        value = copy.deepcopy(manifest())
        next(iter(value["source_revisions"].values()))["reason"] = " "
        with self.assertRaises(AssertionError):
            validate_manifest(value)


if __name__ == "__main__":
    unittest.main()
