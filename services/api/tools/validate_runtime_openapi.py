"""Independently validate the enabled API using an isolated M02 validator env."""

import json
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.contracts import runtime_openapi


def main():
    with tempfile.TemporaryDirectory(prefix="hydro-openapi-") as directory:
        root = Path(directory)
        document = root / "implemented-openapi.json"
        document.write_text(json.dumps(runtime_openapi()))
        venv.create(root / "validator", with_pip=True)
        python = (
            root / "validator" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        )
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--only-binary=:all:",
                "-r",
                str(ROOT / "scripts/openapi-validation-requirements.txt"),
            ],
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-m",
                "openapi_spec_validator",
                "--schema",
                "3.1",
                "--validation-errors",
                "all",
                str(document),
            ],
            check=True,
        )
    print("PASS: independent OpenAPI 3.1 validation of implemented operations")


if __name__ == "__main__":
    main()
