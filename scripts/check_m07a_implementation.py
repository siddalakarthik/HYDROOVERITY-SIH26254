"""Verify the bounded M07-A runtime activation against approved contracts."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.contracts import DESIGN, OPERATIONS, runtime_openapi  # noqa: E402
from hydro.service_contracts import ACTIVE, DISABLED  # noqa: E402


def main():
    manifest = json.loads((ROOT / "data/schemas/m07a-implementation.json").read_text())
    assert manifest["verified_main"] == "c3f785c4fa2974ec45e473786bca4ea8806e2c7a"
    assert manifest["approved_contract_head"] == "5893c5c79831d77fc228d3eae9b814915c071d98"
    assert set(manifest["implemented_operation_ids"]) == ACTIVE
    assert set(manifest["privacy_disabled_operation_ids"]) == DISABLED
    assert manifest["counts"] == {"baseline_implemented":58,"m07a_implemented":12,"total_implemented":70,"designed_operations":161,"baseline_migrated_tables":30,"m07a_migrated_tables":5,"total_migrated_tables":35,"designed_tables":74}
    runtime = runtime_openapi()
    ids = {o["operationId"] for ms in runtime["paths"].values() for o in ms.values()}
    assert ids == {o["id"] for o in OPERATIONS} | ACTIVE
    assert not ids & DISABLED
    for op in OPERATIONS:
        actual = copy.deepcopy(runtime["paths"][op["path"]][op["method"]])
        if op["path"].endswith("/work-orders") and op["method"] == "post":
            actual["requestBody"]["content"]["application/json"]["schema"] = {"$ref":"#/components/schemas/WorkOrderWrite"}
        assert actual == DESIGN["paths"][op["path"]][op["method"]], op["id"]
    for name, schema in runtime["components"]["schemas"].items():
        if name in DESIGN["components"]["schemas"]:
            assert schema == DESIGN["components"]["schemas"][name], name
    assert not {"EvaluationResult", "SimulationParameters", "RunOutput"} & runtime["components"]["schemas"].keys()
    for name, digest in manifest["new_source_sha256"].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    print("PASS: 58 compatible baseline + 12 M07-A operations = 70; 35 migrated / 74 designed tables; privacy and future-operation gates retained")


if __name__ == "__main__":
    main()
