"""One-shot trusted container initializer; runtime cannot read owner credentials."""

import json
import os
import subprocess
import sys
from pathlib import Path

from psycopg.conninfo import make_conninfo

from .operator import prepare


def main():
    # Dedicated bind root is traversable, while operator credentials stay
    # root-only in 0700/operator and runtime files belong to uid 10001.
    os.chmod("/private", 0o711)
    os.environ["HYDRO_OPERATOR_DSN"] = make_conninfo(
        host="db",
        port=5432,
        dbname="postgres",
        user="hydro_operator",
        password=Path("/run/secrets/database_root").read_text().strip(),
    )
    database = os.environ.get("HYDRO_INIT_DATABASE", "hydro_local_m03")
    prepare(database, database, Path("/private/operator"))
    operator = json.loads(Path("/private/operator/operator.json").read_text())
    env = {**os.environ, "HYDRO_MIGRATION_URL": operator["migration_url"]}
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "services/api/alembic.ini", "upgrade", "head"],
        env=env,
        check=True,
    )
    runtime = json.loads(Path("/private/operator/runtime.json").read_text())
    target = Path("/private/runtime")
    target.mkdir(mode=0o700, exist_ok=True)
    runtime["mail_directory"] = "/private/runtime/mail"
    config = target / "runtime.json"
    config.write_text(json.dumps(runtime))
    config.chmod(0o600)
    os.chown(config, 10001, 10001)
    os.chown(target, 10001, 10001)
    print("Private database migrations ready; no human account was created")


if __name__ == "__main__":
    main()
