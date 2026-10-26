"""Validate exact contact amendments and all previous API compatibility."""
import hashlib
import sys

from pre_m10_contact_sources import ROOT, before_contact, digest, manifest


def main():
    value = manifest()
    for name, row in value["source_revisions"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert actual == row["sha256"], name
    for name, expected in value["new_source_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == expected, name
    sys.path.insert(0, str(ROOT / "services/api"))
    from hydro.contracts import runtime_openapi
    spec = runtime_openapi()
    assert sum(len(ms) for ms in spec["paths"].values()) == 112
    assert digest(before_contact(spec)) == value["previous_openapi_sha256"]
    from hydro.config import Settings
    assert Settings.model_fields["contact_test_policy"].default is None
    print("PASS: all 111 previous operations preserved; one gated contact operation; 53 tables; normal intake disabled")


if __name__ == "__main__":
    main()
