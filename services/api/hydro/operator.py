"""Private database preparation; never imported by the runtime API."""

import argparse
import json
import os
import secrets
import subprocess
from pathlib import Path
from urllib.parse import quote

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict

from .config import ROOT


def private_directory(directory: Path) -> None:
    directory = directory.resolve()
    if directory.is_relative_to(ROOT):
        raise ValueError("Operator configuration must be outside the repository")
    if directory.exists():
        if not (directory / "operator.json").is_file():
            raise ValueError("Use a new dedicated private directory")
        return
    directory.mkdir(parents=True, mode=0o700)
    if os.name == "nt":
        principal = subprocess.run(
            ["whoami"], capture_output=True, text=True, check=True
        ).stdout.strip()
        subprocess.run(
            [
                "icacls",
                str(directory),
                "/inheritance:r",
                "/grant:r",
                principal + ":(OI)(CI)F",
                "*S-1-5-18:(OI)(CI)F",
            ],
            check=True,
            capture_output=True,
        )
    else:
        directory.chmod(0o700)


def prepare(database: str, confirmed: str, directory: Path) -> None:
    if database != confirmed or not database.replace("_", "").isalnum():
        raise ValueError("Explicit database confirmation is required")
    dsn = os.environ["HYDRO_OPERATOR_DSN"]
    admin = conninfo_to_dict(dsn)
    directory = directory.resolve()
    private_directory(directory)
    operator_file = directory / "operator.json"
    existing = json.loads(operator_file.read_text()) if operator_file.exists() else None
    if existing and existing["database"] != database:
        raise ValueError("Private directory is already bound to another database")
    owner_password = existing["owner_password"] if existing else secrets.token_urlsafe(36)
    app_password = existing["app_password"] if existing else secrets.token_urlsafe(36)
    with psycopg.connect(dsn, autocommit=True, connect_timeout=3) as c:
        for role, password in [("hydro_migrator", owner_password), ("hydro_app", app_password)]:
            row = c.execute(
                "SELECT rolsuper,rolbypassrls,rolcreaterole FROM pg_roles WHERE rolname=%s", (role,)
            ).fetchone()
            if row:
                if not existing or any(row):
                    raise ValueError(
                        "Existing role is not a safely prepared M03 role; no password was changed"
                    )
            else:
                c.execute(
                    sql.SQL(
                        "CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS NOCREATEROLE NOCREATEDB NOINHERIT"
                    ).format(sql.Identifier(role), sql.Literal(password))
                )
        found = c.execute(
            "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s", (database,)
        ).fetchone()
        if found and (not existing or found[0] != "hydro_migrator"):
            raise ValueError(
                "Existing database is not bound to this private setup; no data changed"
            )
        if not found:
            c.execute(
                sql.SQL("CREATE DATABASE {} OWNER hydro_migrator").format(sql.Identifier(database))
            )
        c.execute(sql.SQL("ALTER DATABASE {} SET timezone='UTC'").format(sql.Identifier(database)))
    params = {**admin, "dbname": database}
    with psycopg.connect(**params, autocommit=True, connect_timeout=3) as c:
        c.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    host = admin.get("host", "127.0.0.1")
    port = admin.get("port", "5432")

    def url(role, password):
        return f"postgresql+psycopg://{role}:{quote(password, safe='')}@{host}:{port}/{database}"

    runtime = {
        "database_url": url("hydro_app", app_password),
        "hmac_key": existing["hmac_key"] if existing else secrets.token_urlsafe(48),
        "origin": "https://localhost:8443",
        "mail_directory": str(directory / "mail"),
        "development": True,
    }
    operator = {
        "database": database,
        "migration_url": url("hydro_migrator", owner_password),
        "admin_dsn": dsn,
        "owner_password": owner_password,
        "app_password": app_password,
        "hmac_key": runtime["hmac_key"],
    }
    for name, value in [("operator.json", operator), ("runtime.json", runtime)]:
        p = directory / name
        with p.open("w", encoding="utf-8") as f:
            p.chmod(0o600)
            json.dump(value, f, indent=2)
    print("Prepared private configuration:", directory, "(credentials not printed)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--confirm-database", required=True)
    parser.add_argument("--private-directory", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.database, args.confirm_database, args.private_directory)


if __name__ == "__main__":
    main()
