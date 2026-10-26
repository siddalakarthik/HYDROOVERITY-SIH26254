"""Restricted disposable-database operator procedure; no live activation or external delivery."""

import argparse
import json
import os
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))

from hydro.contact_policy import ContactTestPolicy
from hydro.db import one
from hydro.project_contact import mark_reviewed, purge_synthetic_policy, review_inbox, set_hold


def private_path(value):
    result = value.resolve()
    if result.is_relative_to(ROOT):
        raise ValueError("Operator configuration and private output must be outside Git")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator-config", type=Path, required=True)
    parser.add_argument("--policy-config", type=Path, required=True)
    parser.add_argument("--confirm-disposable-database", required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--output", type=Path, required=True)
    listing.add_argument("--limit", type=int, default=50)
    for name in ("review", "hold", "release-hold"):
        action = sub.add_parser(name)
        action.add_argument("--id", type=UUID, required=True)
        action.add_argument("--version", type=int, required=True)
        if name == "hold":
            action.add_argument("--reference", required=True)
    sub.add_parser("purge-synthetic-expired")
    args = parser.parse_args()
    config = json.loads(private_path(args.operator_config).read_text(encoding="utf-8"))
    policy = ContactTestPolicy.model_validate_json(
        private_path(args.policy_config).read_text(encoding="utf-8")
    )
    database = args.confirm_disposable_database
    if not database.startswith("hydro_disposable_") or config["database"] != database:
        raise ValueError("Exact disposable database confirmation required")
    output = private_path(args.output) if args.action == "list" else None
    if output and (output.exists() or not output.parent.is_dir()):
        raise ValueError("Use a new output file in an existing private directory")
    engine = create_engine(config["migration_url"], hide_parameters=True)
    try:
        with engine.begin() as c:
            if one(c, "SELECT current_database() AS name")["name"] != database:
                raise ValueError("Connected database does not match confirmation")
            if args.action == "list":
                rows = review_inbox(c, policy, args.limit)
                count = len(rows)
            elif args.action == "review":
                mark_reviewed(c, policy, args.id, args.version)
                count = 1
            elif args.action in {"hold", "release-hold"}:
                set_hold(
                    c,
                    policy,
                    args.id,
                    args.version,
                    args.reference if args.action == "hold" else None,
                )
                count = 1
            else:
                count = purge_synthetic_policy(c, policy)
        if output:
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as f:
                json.dump(
                    {"provenance": policy.provenance, "items": rows}, f, indent=2, default=str
                )
                f.write("\n")
        print(f"Completed synthetic-policy operator action: {args.action}; records={count}.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit(
            "Project contact operator action failed; no credentials or private payload are logged."
        ) from None
