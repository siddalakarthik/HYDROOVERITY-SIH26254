"""Check current guide claims and exact documentation amendment scope."""
import hashlib
import json
from collections import Counter
from pre_m10_docs_sources import ROOT, manifest


def main():
    value = manifest()
    expected = {n: row["sha256"] for n, row in value["source_revisions"].items()}
    expected.update(value["new_source_sha256"])
    for name, digest in expected.items():
        assert hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == digest, name
    contract = json.loads((ROOT / "apps/web/contracts/implemented.openapi.json").read_text(encoding="utf-8"))
    assert sum(method in {"get", "post", "put", "patch", "delete"} for path in contract["paths"].values() for method in path) == 119
    pages = json.loads((ROOT / "apps/web/src/lib/route-capabilities.json").read_text(encoding="utf-8"))["pages"]
    assert len(pages) == 51
    assert Counter(p["status"] for p in pages) == {"ACTIVE_FUNCTIONAL": 30, "ACTIVE_READ_ONLY": 5, "INFORMATIONAL": 9, "DEFERRED": 7}
    register = json.loads((ROOT / "docs/testing/pre-m10-completion.json").read_text(encoding="utf-8"))
    assert register["implemented_operations"] == 119 and register["migrated_tables"] == 57
    for name in ("apps/web/README.md", "services/api/README.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "119" in text and "58" in text and "historical" in text.lower(), name
    print("PASS: current 119-operation/57-table/51-page guides; narrow amendment preserves historical source pins")


if __name__ == "__main__":
    main()
