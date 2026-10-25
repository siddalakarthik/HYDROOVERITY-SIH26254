"""Run one utility-scoped private-development in-app worker; no external adapters."""

import argparse
import json
import sys
import time
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.config import Settings
from hydro.db import engine
from hydro.notification_worker import run_once


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-config", required=True, type=Path)
    parser.add_argument("--organization", required=True, type=UUID)
    parser.add_argument("--supervisor-user", required=True, type=UUID)
    parser.add_argument("--once", action="store_true")
    parser.add_argument(
        "--retry-policy",
        type=Path,
        help="Private operator-reviewed JSON: reference and two delay_seconds; omit to disable retries",
    )
    args = parser.parse_args()
    config = args.runtime_config.resolve()
    if config.is_relative_to(ROOT):
        raise SystemExit("Private runtime configuration must be outside Git")
    settings = Settings.model_validate_json(config.read_text())
    policy = None
    if args.retry_policy:
        path = args.retry_policy.resolve()
        if path.is_relative_to(ROOT):
            raise SystemExit("Operator policy must remain outside Git")
        policy = json.loads(path.read_text())
        if (
            set(policy) != {"reference", "delay_seconds"}
            or not isinstance(policy["reference"], str)
            or not policy["reference"].strip()
        ):
            raise SystemExit("Explicit reviewed policy reference required")
    database = engine(settings)
    try:
        while True:
            result = run_once(
                database,
                args.supervisor_user,
                args.organization,
                policy["delay_seconds"] if policy else None,
                policy["reference"] if policy else None,
            )
            print(result, flush=True)  # Safe state only; no recipient, event or raw error.
            if args.once:
                break
            if result == "IDLE":
                time.sleep(2)
    finally:
        database.dispose()


if __name__ == "__main__":
    main()
