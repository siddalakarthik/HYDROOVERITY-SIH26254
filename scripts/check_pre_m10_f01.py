"""Check the exact F01 source amendment without relaxing historical baselines."""
import hashlib

from pre_m10_f01_sources import ROOT, manifest
from pre_m10_revisit_sources import extend_digest
from pre_m10_contact_sources import extend_digest as extend_contact
from pre_m10_realtime_sources import extend_digest as extend_realtime


def main():
    value = manifest()
    for name, change in value["source_revisions"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert actual == extend_realtime(name, extend_contact(name, extend_digest(name, change["sha256"]))), name
    print(f"PASS: {len(value['source_revisions'])} explicitly scoped F01 source revisions")


if __name__ == "__main__":
    main()
