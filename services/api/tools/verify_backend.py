"""Run real PostgreSQL acceptance and write sanitized, machine-readable evidence."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator-config", type=Path, required=True)
    parser.add_argument("--runtime-config", type=Path, required=True)
    parser.add_argument("--confirm-disposable-database", required=True)
    parser.add_argument("--evidence-directory", type=Path, required=True)
    args = parser.parse_args()
    operator = json.loads(args.operator_config.read_text())
    runtime = json.loads(args.runtime_config.read_text())
    if operator["database"] != args.confirm_disposable_database or not operator[
        "database"
    ].startswith("hydro_disposable_"):
        raise SystemExit("Refusing acceptance reset without exact disposable database confirmation")
    evidence = args.evidence_directory.resolve()
    if evidence.is_relative_to(ROOT):
        raise SystemExit("Store generated acceptance evidence outside the repository")
    evidence.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "services/api"),
        "HYDRO_TEST_OWNER_URL": operator["migration_url"],
        "HYDRO_TEST_RUNTIME_URL": runtime["database_url"],
        "HYDRO_TEST_DATABASE_CONFIRM": operator["database"],
        "HYDRO_MIGRATION_URL": operator["migration_url"],
        "HYDRO_TEST_EVIDENCE_DIR": str(evidence),
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "services/api/alembic.ini", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "services/api/tests",
            "-q",
            "--tb=short",
            "--junitxml=" + str(evidence / "pytest-junit.xml"),
        ],
        cwd=ROOT,
        env=env,
    )
    if result.returncode:
        raise SystemExit(result.returncode)
    from hydro.contracts import INVENTORY, OPERATIONS

    summary = json.loads((evidence / "pytest-summary.json").read_text())
    missing = [op["id"] for op in OPERATIONS if op["id"] not in summary["operation_tests"]]
    if missing:
        print("Operations without executed positive response conformance:", ",".join(missing))
        raise SystemExit(1)
    files = sorted(
        [
            *(ROOT / "services/api").rglob("*.py"),
            *(ROOT / "services/api/migrations").glob("*.sql"),
            ROOT / "docs/architecture/openapi-design.json",
        ]
    )
    digest = hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(ROOT)).replace("\\", "/").encode())
        digest.update(path.read_bytes())
    head = os.environ.get("HYDRO_SOURCE_COMMIT")
    if not head:
        try:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            head = "UNAVAILABLE"
    from xml.etree import ElementTree

    xml = ElementTree.parse(evidence / "pytest-junit.xml")
    summary["skipped"] = sum(int(s.get("skipped", "0")) for s in xml.iter("testsuite"))
    summary["errors"] = sum(int(s.get("errors", "0")) for s in xml.iter("testsuite"))
    summary.update(
        implemented_operations=len(OPERATIONS),
        deferred_operations=len(INVENTORY) - len(OPERATIONS),
        positive_response_conformance="PASS",
        git_head_at_execution=head,
        backend_source_sha256=digest.hexdigest(),
        physical_trials=0,
        field_trials=0,
    )
    (evidence / "acceptance-summary.json").write_text(json.dumps(summary, indent=2))
    print(
        "PASS:",
        summary["collected"],
        "tests;",
        len(OPERATIONS),
        "implemented operation projections verified against canonical schemas",
    )


if __name__ == "__main__":
    main()
