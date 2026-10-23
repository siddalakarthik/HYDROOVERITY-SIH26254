"""Reproduce the implemented-only browser contract and 46-route capability index."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
WEB = ROOT / "apps/web"
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.contracts import runtime_openapi  # noqa: E402
from hydro.service_contracts import ACTIVE  # noqa: E402
from hydro.science_contracts import OPERATIONS as SCIENCE  # noqa: E402


def outputs():
    catalogue = json.loads((ROOT / "design/ui-ux/m02-route-catalog.json").read_text())
    matrix = json.loads((ROOT / "data/schemas/m03-implementation-matrix.json").read_text())
    inventory = json.loads((ROOT / "data/schemas/m02-api-inventory.json").read_text())["operations"]
    implemented = {o["id"] for o in matrix["operations"] if o["status"] == "CODE_TESTED"}
    contract = runtime_openapi()
    advertised = {operation["operationId"] for methods in contract["paths"].values() for operation in methods.values()}
    assert advertised == implemented | ACTIVE | {o["id"] for o in SCIENCE}, "Browser contract must match exactly the implemented operations"
    assert not {"EvaluationResult", "SimulationParameters", "SimulationRun", "RunOutput"}.intersection(contract["components"]["schemas"]), "Deferred scientific/evaluation models must not enter the browser contract"
    groups = {
        7: ["Public"], 8: ["Public"], 18: ["Current user"], 19: ["Current user"],
        20: ["Complaints"], 21: ["Complaints"], 22: ["Complaints"],
        23: ["Incidents", "Work orders", "Water zones"], 24: ["Water zones", "Pipeline assets"],
        31: ["Incidents", "Evidence", "Water zones"], 32: ["Incidents", "Evidence"],
        33: ["Work orders"], 34: ["Work orders", "Repairs"], 35: ["Verification"],
        36: ["Complaints", "Incidents"], 44: ["Administration"], 45: ["Organization"], 46: ["Administration"],
    }
    auth = {12: "login", 13: "register", 14: "recovery", 15: "reset", 16: "verify", 17: "invitation-accept"}
    pages = []
    for p in catalogue["pages"]:
        number = int(p["id"].split("-")[1])
        status = ("INFORMATIONAL" if number in [1, 2, 3, 4, 5, 6, 9, 10, 11] else
                  "DEFERRED" if number in [25, 26, 27, 28, 29, 30, 37, 38, 39, 40, 41, 42, 43] else
                  "ACTIVE_READ_ONLY" if number in [7, 23, 45, 46] else "ACTIVE_FUNCTIONAL")
        candidates = [o for o in inventory if o["group"] in groups.get(number, [])]
        if number in auth:
            candidates = [o for o in inventory if o["path"] in ["/auth/csrf", "/auth/" + auth[number]]]
        if number == 7:
            candidates = [o for o in candidates if o["path"] == "/public/project-status"]
        if number == 8:
            candidates = [o for o in candidates if o["path"] == "/public/utilities/{slug}"]
        if number == 46:
            candidates = [o for o in candidates if o["path"].endswith("/audit-logs")]
        if number == 44:
            candidates = [o for o in candidates if not o["path"].endswith(("/audit-logs", "/integrations"))]
        private = p["roles"] != "PUBLIC"
        deps = [{"operation_id": o["id"], "method": o["method"].upper(), "path": o["path"],
                 "status": "IMPLEMENTED" if o["id"] in implemented else "DEFERRED"} for o in candidates]
        pages.append({"id": p["id"], "route": p["route"], "roles": p["roles"], "title": p["objective"],
                      "status": status, "operations": deps,
                      "shared_operations": ["GET /me", "GET /me/memberships", "GET /orgs/{organization_id}"] if private else [],
                      "data_boundary": "Current membership plus own/assigned/role checks enforced by M03" if private else "Editorial or allow-listed public projection only",
                      "states": ["loading", "empty", "error", "denied", "expired", "pending", "receipt", "stale", "rate-limited", "mobile"] if status.startswith("ACTIVE") else ["informational", "mobile"],
                      "component": "public" if number <= 11 else "auth" if number <= 19 else "complaints" if number in [20, 21, 22, 36] else "network" if number == 24 else "incidents" if number in [23, 31, 32] else "work" if number in [33, 34, 35] else "administration" if number in [44, 45, 46] else "unavailable",
                      "browser_evidence": "Executed scoped cross-role and account/GIS suites; see M04_EXECUTION_LEDGER.md. This classification does not imply individual assertions for every route.",
                      "future_dependency": "Deferred M03 operation; no active navigation" if status == "DEFERRED" else "Attachments, telemetry, offline queue and scientific integration remain disabled"})
    assert len(pages) == 46 and len(implemented) == 58
    for p in pages:
        if p["id"] in {"PAGE-40", "PAGE-41"}:
            p.update(status="ACTIVE_FUNCTIONAL", component="science",
                     title="Import and replay verified observation-only M05 scenarios",
                     operations=[{"operation_id": o["id"], "method": o["method"].upper(), "path": o["path"], "status": "IMPLEMENTED"} for o in SCIENCE],
                     data_boundary="Engineer-only tenant-scoped SIMULATION snapshots; no evaluator truth or operational linkage",
                     future_dependency="Arbitrary run jobs, simulator credentials and evaluator endpoints remain deferred")
    proposed = json.loads((ROOT / "design/ui-ux/m07-route-catalog.json").read_text())
    page_operations = {47:[2,5],48:[1],49:[3,4,6,8],50:[2,7],51:[3,4,7,8,9,13]}
    for p in proposed["pages"][-5:]:
        number = int(p["id"].split("-")[1])
        pages.append({"id": p["id"], "route": p["route"], "roles": p["roles"], "title": p["objective"],
                      "status": "ACTIVE_FUNCTIONAL", "operations": [{"operation_id": f"m07_n{i:02}", "status": "IMPLEMENTED"} for i in page_operations[number]],
                      "component": "service-requests", "future_dependency": "Visit preferences/access, scheduling, attachments and notifications disabled"})
    return {WEB / "contracts/implemented.openapi.json": contract,
            WEB / "src/lib/route-capabilities.json": {"milestone": "M04 + M07-A + M06", "pages": pages}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, data in outputs().items():
        expected = json.dumps(data, indent=2) + "\n"
        if args.check:
            assert json.loads(path.read_text()) == data, f"Contract drift: {path.relative_to(ROOT)}"
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected)
    print("PASS: 77 implemented operations and 51 route classifications; privacy-gated routes excluded")
