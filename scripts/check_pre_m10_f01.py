"""Check the exact F01 source amendment without relaxing historical baselines."""
import hashlib

from pre_m10_f01_sources import ROOT, manifest


def main():
    value = manifest()
    for name, change in value["source_revisions"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert actual == change["sha256"], name
    print(f"PASS: {len(value['source_revisions'])} explicitly scoped F01 source revisions")


if __name__ == "__main__":
    main()
