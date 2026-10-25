"""Verify the exact reviewed documentation images and their source provenance."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "docs/media/manifest.json").read_text())
    assert manifest["baseline_commit"] == "848c1c8a1dbf72f980c1f58454a41d0bd332eab8"
    names = {row["path"] for row in manifest["assets"]}
    assert len(names) == len(manifest["assets"]) == 7
    assert names == {"docs/media/" + name + ".png" for name in (
        "website-public", "guard5-cad", "guard5-channels", "acoustic-clock",
        "test-rig", "budget", "guard5-comparison",
    )}
    assert {p.name for p in (ROOT / "docs/media").iterdir()} == {
        "README.md", "manifest.json", *(Path(name).name for name in names),
    }, "Unexpected public media payload"
    for row in manifest["assets"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] < 1024 * 1024
        assert raw.startswith(b"\x89PNG\r\n\x1a\n")
        assert hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"]
        width, height = struct.unpack(">II", raw[16:24])
        assert width >= 1400 and height >= 700, row["path"]
        assert row["caption"] and row["kind"] and (ROOT / row["reproduction"]).is_file()
        for name, expected in row["source_sha256"].items():
            assert hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == expected, name
    print("PASS: seven exact reviewed previews, source hashes, dimensions and bounded payloads")


if __name__ == "__main__":
    main()
