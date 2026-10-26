"""Check the exact revisit source revision without rewriting old evidence."""
import hashlib
from pre_m10_revisit_sources import ROOT, manifest


def main():
    value = manifest()
    for name, change in value["source_revisions"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert actual == change["sha256"], name
    print(f"PASS: {len(value['source_revisions'])} explicitly scoped revisit source revisions")


if __name__ == "__main__":
    main()
