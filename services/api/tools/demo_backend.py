"""Execute the synthetic workflow through real verified loopback HTTPS and restart.

Only an explicitly confirmed hydro_disposable_* database may be initialized/reset.
The script retains database rows and sanitized evidence, and stops only its own API
and proxy child processes. It never drops a database or changes M05/M08 artifacts.
"""

import argparse
import json
import os
import secrets
import ssl
import subprocess
import sys
import time
from pathlib import Path

import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "services/api"), str(ROOT / "services/api/tests")]

from test_workflow import test_complete_persistent_operational_workflow

from hydro.cli import bootstrap
from hydro.config import Settings
from hydro.db import one
from hydro.operator import private_directory
from hydro.repository import TABLES


class HTTPSClient:
    def __init__(self, origin, certificate, number):
        context = ssl.create_default_context(cafile=str(certificate))
        self.http = httpx.Client(
            base_url=origin,
            transport=httpx.HTTPTransport(
                verify=context, local_address="127.0.0." + str(number + 1)
            ),
            timeout=15,
        )
        self.origin = origin

    def request(self, method, path, **kwargs):
        headers = kwargs.pop("headers", {})
        if method.lower() not in {"get", "head"}:
            csrf = self.request("GET", "/api/v1/auth/csrf")
            if csrf.status_code != 200:
                raise AssertionError("HTTPS CSRF bootstrap failed")
            headers = {"Origin": self.origin, "X-CSRF-Token": csrf.json()["csrf_token"], **headers}
        return self.http.request(method, path, headers=headers, **kwargs)

    def close(self):
        self.http.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator-config", type=Path, required=True)
    parser.add_argument("--runtime-config", type=Path, required=True)
    parser.add_argument("--confirm-disposable-database", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--openssl", default="openssl")
    args = parser.parse_args()
    name = args.confirm_disposable_database
    if not name.startswith("hydro_disposable_") or not name.replace("_", "").isalnum():
        raise SystemExit("Explicit disposable database name required")
    private = args.output_directory.resolve()
    if private.is_relative_to(ROOT):
        raise SystemExit("Keep private runtime/demo material outside Git")
    operator = json.loads(args.operator_config.read_text())
    runtime = json.loads(args.runtime_config.read_text())
    marker = private / "operator.json"
    if marker.exists():
        previous = json.loads(marker.read_text())
        if previous.get("database") != name or previous.get("purpose") != "SYNTHETIC_DEMO_ONLY":
            raise SystemExit("Output directory belongs to another operator setup; no files changed")
    private_directory(private)
    # Marker allows safe reruns of this dedicated directory; contains no secrets.
    (private / "operator.json").write_text(
        json.dumps({"database": name, "purpose": "SYNTHETIC_DEMO_ONLY"})
    )
    admin = conninfo_to_dict(operator["admin_dsn"])
    with psycopg.connect(**{**admin, "autocommit": True, "connect_timeout": 3}) as c:
        found = c.execute(
            "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s", (name,)
        ).fetchone()
        if found and found[0] != "hydro_migrator":
            raise SystemExit("Disposable database owner does not match; no reset performed")
        if not found:
            c.execute(
                sql.SQL("CREATE DATABASE {} OWNER hydro_migrator").format(sql.Identifier(name))
            )
        c.execute(sql.SQL("ALTER DATABASE {} SET timezone='UTC'").format(sql.Identifier(name)))
    with psycopg.connect(
        **{**admin, "dbname": name, "autocommit": True, "connect_timeout": 3}
    ) as c:
        c.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    owner_url = (
        make_url(operator["migration_url"]).set(database=name).render_as_string(hide_password=False)
    )
    runtime["database_url"] = (
        make_url(runtime["database_url"]).set(database=name).render_as_string(hide_password=False)
    )
    runtime["mail_directory"] = str(private / "mail")
    config = private / "runtime.json"
    config.write_text(json.dumps(runtime))
    config.chmod(0o600)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "services/api"), "HYDRO_MIGRATION_URL": owner_url}
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "services/api/alembic.ini", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    owner = create_engine(owner_url, hide_parameters=True, connect_args={"connect_timeout": 3})
    password = secrets.token_urlsafe(24)
    with owner.begin() as c:
        if one(c, "SELECT current_database() AS name")["name"] != name:
            raise SystemExit("Target changed; no reset performed")
        c.exec_driver_sql("TRUNCATE " + ",".join(sorted(TABLES)) + " RESTART IDENTITY CASCADE")
        org, member, _ = bootstrap(
            c,
            confirmed_database=name,
            slug="synthetic-utility-a",
            name="SYNTHETIC integration utility A",
            email="admin-a@example.invalid",
            display_name="Synthetic administrator A",
            password=password,
            reporting_enabled=True,
        )
        other, other_admin, _ = bootstrap(
            c,
            confirmed_database=name,
            slug="synthetic-utility-b",
            name="SYNTHETIC integration utility B",
            email="admin-b@example.invalid",
            display_name="Synthetic administrator B",
            password=password,
            reporting_enabled=True,
        )
    certificate = private / "localhost.crt"
    key = private / "localhost.key"
    if not certificate.exists():
        subprocess.run(
            [
                args.openssl,
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-days",
                "2",
                "-keyout",
                str(key),
                "-out",
                str(certificate),
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=DNS:localhost,IP:127.0.0.1",
            ],
            check=True,
            capture_output=True,
        )
        key.chmod(0o600)
    children = []
    clients = []
    log = (private / "local-server.log").open("ab")
    child_env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(
            (
                "HYDRO_OPERATOR",
                "HYDRO_MIGRATION",
                "HYDRO_TEST_OWNER",
                "HYDRO_TEST_ADMIN",
                "HYDRO_BOOTSTRAP",
            )
        )
    }
    child_env["PYTHONPATH"] = str(ROOT / "services/api")

    def start(kind):
        args2 = [sys.executable, "-m", "hydro.local", kind]
        args2 += (
            ["--runtime-config", str(config)]
            if kind == "api"
            else ["--certificate", str(certificate), "--key", str(key)]
        )
        process = subprocess.Popen(
            args2,
            cwd=ROOT,
            env=child_env,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        children.append(process)
        return process

    def ready(process):
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError("Local API exited; inspect the private log")
            try:
                if (
                    httpx.get("http://127.0.0.1:8000/internal/health/ready", timeout=1).status_code
                    == 200
                ):
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.25)
        raise RuntimeError("Local API did not become ready")

    api = None
    try:
        # Fail when another process owns the demonstration ports; do not kill it.
        import socket

        for port in [8000, 8443]:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", port))
        api = start("api")
        ready(api)
        start("proxy")
        number = 0

        def client():
            nonlocal number
            number += 1
            obj = HTTPSClient(runtime["origin"], certificate, number)
            clients.append(obj)
            return obj

        for _ in range(40):
            try:
                context = ssl.create_default_context(cafile=str(certificate))
                if (
                    httpx.get(
                        runtime["origin"] + "/api/v1/public/project-status",
                        verify=context,
                        timeout=1,
                    ).status_code
                    == 200
                ):
                    break
            except httpx.HTTPError:
                time.sleep(0.25)

        def restart(previous):
            nonlocal api
            api.terminate()
            api.wait(timeout=10)
            api = start("api")
            ready(api)
            obj = client()
            obj.http.cookies.update(previous.http.cookies)
            return obj

        fixture = {
            "owner": owner,
            "settings": Settings.model_validate(runtime),
            "org": org,
            "admin": member,
            "other": other,
            "other_admin": other_admin,
            "password": password,
            "client": client,
            "restart_factory": restart,
        }
        test_complete_persistent_operational_workflow(fixture, private)
        summary = json.loads((private / "m03-workflow-evidence.json").read_text())
        with owner.connect() as connection:
            migration_head = connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar_one()
        summary.update(
            transport="REAL_LOOPBACK_HTTPS",
            certificate_verification="PASS",
            actual_api_process_restart="PASS",
            database=name,
            migration_head=migration_head,
        )
        (private / "https-workflow-summary.json").write_text(json.dumps(summary, indent=2))
        print(
            "PASS: real HTTPS workflow, independent NOT_VERIFIABLE outcome and actual API restart"
        )
    finally:
        for client in clients:
            client.close()
        for process in reversed(children):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
        owner.dispose()
        log.close()


if __name__ == "__main__":
    main()
