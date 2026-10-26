"""Execute gated project contact acceptance against an isolated PostgreSQL database."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[3]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--operator-config", type=Path, required=True)
    p.add_argument("--runtime-config", type=Path, required=True)
    p.add_argument("--confirm-disposable-database", required=True)
    p.add_argument("--evidence-directory", type=Path, required=True)
    args = p.parse_args()
    operator = json.loads(args.operator_config.read_text())
    runtime = json.loads(args.runtime_config.read_text())
    database = args.confirm_disposable_database
    if operator["database"] != database or not database.startswith("hydro_disposable_"):
        raise SystemExit("Exact disposable database confirmation required")
    output = args.evidence_directory.resolve()
    if output.is_relative_to(ROOT):
        raise SystemExit("Keep raw pre-M10 contact evidence outside Git")
    output.mkdir(parents=True, exist_ok=True)
    temporary = output / "temp"
    temporary.mkdir(exist_ok=True)
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "services/api"),
        "HYDRO_TEST_OWNER_URL": operator["migration_url"],
        "HYDRO_TEST_RUNTIME_URL": runtime["database_url"],
        "HYDRO_TEST_DATABASE_CONFIRM": database,
        "HYDRO_MIGRATION_URL": operator["migration_url"],
        "HYDRO_TEST_EVIDENCE_DIR": str(output),
        "TEMP": str(temporary),
        "TMP": str(temporary),
    }
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "services/api/tests/prem10_contact_acceptance.py",
            "-q",
            "--tb=short",
            "--junitxml=" + str(output / "pytest-junit.xml"),
        ],
        cwd=ROOT,
        env=env,
    )
    if result.returncode:
        raise SystemExit(result.returncode)
    summary = json.loads((output / "pytest-summary.json").read_text())
    xml = ElementTree.parse(output / "pytest-junit.xml")
    summary["skipped"] = sum(int(s.get("skipped", "0")) for s in xml.iter("testsuite"))
    summary["errors"] = sum(int(s.get("errors", "0")) for s in xml.iter("testsuite"))
    summary["source_sha256"] = {
        str(f.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in [Path(__file__), ROOT / "services/api/tests/prem10_contact_acceptance.py"]
    }
    summary["git_head_at_execution"] = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if (ROOT / ".git").exists()
        else os.environ.get("HYDRO_SOURCE_COMMIT", "UNAVAILABLE")
    )
    summary["physical_trials"] = 0
    summary["field_trials"] = 0
    (output / "prem10-contact-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        f"PASS: {summary['collected']} independent pre-M10 contact scenarios; no physical evidence claimed"
    )


if __name__ == "__main__":
    main()
