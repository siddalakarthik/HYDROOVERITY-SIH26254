"""Bounded verified HTTPS measurements and isolated process/database recovery.

Run AFTER browser scenarios. Never targets an ordinary development database.
Owns only child processes it launches. Temporarily refuses connections only to
the exactly confirmed, marked synthetic browser database, restoring in finally.
"""

import argparse
import hashlib
import json
import os
import platform
import socket
import ssl
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services/api"))
from hydro.operator import private_directory


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture-directory", required=True, type=Path)
    p.add_argument("--operator-config", required=True, type=Path)
    p.add_argument("--confirm-disposable-database", required=True)
    p.add_argument("--output-directory", required=True, type=Path)
    p.add_argument("--api-port", type=int, default=8019)
    p.add_argument("--https-port", type=int, default=8469)
    args = p.parse_args()
    private, output = args.fixture_directory.resolve(), args.output_directory.resolve()
    if private.is_relative_to(ROOT) or output.is_relative_to(ROOT):
        raise SystemExit("Private fixture and evidence must remain outside Git")
    marker = json.loads((private / "operator.json").read_text())
    runtime = json.loads((private / "runtime.json").read_text())
    fixture = json.loads((private / "browser.json").read_text())
    database = args.confirm_disposable_database
    if not (
        database.startswith("hydro_disposable_")
        and marker.get("database") == database
        and marker.get("purpose") == "M04_BROWSER_ONLY"
        and make_url(runtime["database_url"]).database == database
        and fixture.get("provenance") == "SYNTHETIC_BROWSER_INTEGRATION_ONLY"
    ):
        raise SystemExit("Exact marked disposable browser database required; nothing disrupted")
    for port in (args.api_port, args.https_port):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    private_directory(output)
    origin = f"https://localhost:{args.https_port}"
    runtime["origin"] = origin
    config = output / "runtime.json"
    config.write_text(json.dumps(runtime))
    certificate = private / "localhost.crt"
    tls = ssl.create_default_context(cafile=str(certificate))
    admin = conninfo_to_dict(json.loads(args.operator_config.read_text())["admin_dsn"])
    env = {
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
    env["PYTHONPATH"] = str(ROOT / "services/api")
    children, clients = [], []
    log = (output / "private-process.log").open("ab")

    def launch(arguments):
        child = subprocess.Popen(
            [sys.executable, *arguments],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        children.append(child)
        return child

    def api():
        child = launch(
            [
                "-m",
                "hydro.local",
                "api",
                "--runtime-config",
                str(config),
                "--port",
                str(args.api_port),
            ]
        )
        for _ in range(60):
            if child.poll() is not None:
                raise RuntimeError("Owned test API exited; inspect private process log")
            try:
                if (
                    httpx.get(
                        f"http://127.0.0.1:{args.api_port}/internal/health/ready", timeout=1
                    ).status_code
                    == 200
                ):
                    return child
            except httpx.HTTPError:
                pass
            time.sleep(0.25)
        raise RuntimeError("Owned API did not become ready")

    def request(client, method, path, **kwargs):
        headers = kwargs.pop("headers", {})
        if method != "GET":
            csrf = client.get("/api/v1/auth/csrf")
            assert csrf.status_code == 200
            headers.update({"Origin": origin, "X-CSRF-Token": csrf.json()["csrf_token"]})
        return client.request(method, path, headers=headers, **kwargs)

    summary = {
        "provenance": "SYNTHETIC_LOOPBACK_ONLY",
        "os": platform.platform(),
        "python": platform.python_version(),
        "database": database,
        "tls": "EXPLICIT_CERTIFICATE_VERIFICATION",
        "physical_trials": 0,
        "limits": "Short local test; no SLA, production scale, long soak, native screen reader or physical validation",
    }
    connections_disabled = False
    try:
        owned_api = api()
        launch(
            [
                "apps/web/tools/local_proxy.py",
                "--certificate",
                str(certificate),
                "--key",
                str(private / "localhost.key"),
                "--port",
                str(args.https_port),
                "--api-port",
                str(args.api_port),
                "--web-port",
                "3000",
            ]
        )
        client = httpx.Client(base_url=origin, verify=tls, timeout=20, trust_env=False)
        clients.append(client)
        for _ in range(40):
            try:
                if client.get("/api/v1/public/project-status").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.25)
        assert (
            request(
                client,
                "POST",
                "/api/v1/auth/login",
                json={"email": "service-citizen@example.invalid", "password": fixture["password"]},
            ).status_code
            == 200
        )
        base = f"/api/v1/orgs/{fixture['org']}"
        path = base + "/service-requests"
        for _ in range(5):
            assert client.get(path).status_code == 200
        measurements = []

        def sample(_):
            started = time.perf_counter()
            r = client.get(path)
            return {
                "ms": (time.perf_counter() - started) * 1000,
                "status": r.status_code,
                "bytes": len(r.content),
            }

        # 3 x 20 requests, concurrency 4, below the unchanged session throttle.
        start = time.perf_counter()
        for _ in range(3):
            with ThreadPoolExecutor(max_workers=4) as pool:
                measurements.extend(pool.map(sample, range(20)))
        duration = time.perf_counter() - start
        latencies = sorted(v["ms"] for v in measurements)
        summary["http_measurement"] = {
            "warmup": 5,
            "repetitions": 3,
            "samples": 60,
            "concurrency": 4,
            "duration_s": duration,
            "requests_per_second": 60 / duration,
            "p50_ms": latencies[29],
            "p95_ms": latencies[56],
            "p99_ms": None,
            "p99_reason": "60 samples insufficient for a stable tail estimate",
            "errors": sum(v["status"] != 200 for v in measurements),
            "response_bytes_min_max": [
                min(v["bytes"] for v in measurements),
                max(v["bytes"] for v in measurements),
            ],
        }
        assert summary["http_measurement"]["errors"] == 0
        owned_api.terminate()
        owned_api.wait(timeout=10)
        failed = client.get(path)
        assert failed.status_code == 503 and failed.json()["error"]["code"] == "PROXY_UNAVAILABLE"
        owned_api = api()
        assert client.get(path).status_code == 200  # same persisted session
        summary["actual_api_restart"] = "PASS_503_THEN_SAME_SESSION_200"
        with psycopg.connect(**admin, autocommit=True) as c:
            actual = c.execute(
                "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s", (database,)
            ).fetchone()
            assert actual == ("hydro_migrator",)
            c.execute(
                sql.SQL("ALTER DATABASE {} ALLOW_CONNECTIONS false").format(
                    sql.Identifier(database)
                )
            )
            connections_disabled = True
            c.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=%s AND pid<>pg_backend_pid()",
                (database,),
            )
        failure = client.get(path)
        assert failure.status_code == 503
        text = failure.text.lower()
        assert all(
            secret not in text
            for secret in ("postgresql", "password", "sqlalchemy", "traceback", database)
        )
        with psycopg.connect(**admin, autocommit=True) as c:
            c.execute(
                sql.SQL("ALTER DATABASE {} ALLOW_CONNECTIONS true").format(sql.Identifier(database))
            )
            connections_disabled = False
        assert client.get(path).status_code == 200
        summary["actual_database_connection_outage"] = "PASS_503_SANITIZED_THEN_200"
        with psycopg.connect(**{**admin, "dbname": database}, autocommit=True) as c:
            summary["postgres"] = c.execute("SELECT version()").fetchone()[0]
            summary["postgis"] = c.execute("SELECT postgis_lib_version()").fetchone()[0]
            summary["migration_head"] = c.execute(
                "SELECT version_num FROM alembic_version"
            ).fetchone()[0]
            summary["migrated_tables"] = c.execute(
                "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename NOT IN ('alembic_version','spatial_ref_sys')"
            ).fetchone()[0]
            summary["database_connections"] = c.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE datname=current_database()"
            ).fetchone()[0]
            summary["waiting_locks"] = c.execute(
                "SELECT count(*) FROM pg_locks l JOIN pg_stat_activity a ON a.pid=l.pid WHERE a.datname=current_database() AND NOT l.granted"
            ).fetchone()[0]
        summary["dependency_locks_sha256"] = {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in (
                "services/api/requirements-lock.txt",
                "apps/web/pnpm-lock.yaml",
                "simulations/requirements-m05.txt",
            )
        }
        summary["git_head_at_execution"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        (output / "m09-https-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(
            "PASS: 60 verified HTTPS reads; actual API restart and isolated database outage/recovery"
        )
    finally:
        if connections_disabled:
            with psycopg.connect(**admin, autocommit=True) as c:
                c.execute(
                    sql.SQL("ALTER DATABASE {} ALLOW_CONNECTIONS true").format(
                        sql.Identifier(database)
                    )
                )
        for client in clients:
            client.close()
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)
        log.close()


if __name__ == "__main__":
    main()
