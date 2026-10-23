"""Prepare a separate, explicitly confirmed synthetic M04 browser database.

No existing database is reset without a matching marker in a dedicated directory.
Credential roles are reused, never changed. Private fixtures never enter the web bundle.
"""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "services/api"), str(ROOT / "services/api/tests")]
from hydro.cli import bootstrap
from hydro.config import Settings
from hydro.db import one
from hydro.main import create_app
from hydro.operator import private_directory
from hydro.repository import TABLES
from conftest import Client
from helpers import expect, login, mutate, provision, register, token
from test_workflow import setup, assigned_work


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--operator-config", required=True, type=Path)
    p.add_argument("--runtime-config", required=True, type=Path)
    p.add_argument("--private-directory", required=True, type=Path)
    p.add_argument("--confirm-disposable-database", required=True)
    p.add_argument("--openssl", default="openssl")
    args = p.parse_args()
    name = args.confirm_disposable_database
    if name not in {"hydro_disposable_m04", "hydro_disposable_m07a_browser"}:
        raise SystemExit("Only explicitly confirmed M04 or M07-A disposable browser fixtures may be reset")
    private = args.private_directory.resolve()
    if private.is_relative_to(ROOT):
        raise SystemExit("Private material must remain outside the checkout")
    marker = private / "operator.json"
    if private.exists() and (not marker.exists() or json.loads(marker.read_text()).get("purpose") != "M04_BROWSER_ONLY"):
        raise SystemExit("Private directory is not a recognized M04 fixture; no reset performed")
    operator = json.loads(args.operator_config.read_text())
    runtime = json.loads(args.runtime_config.read_text())
    admin = conninfo_to_dict(operator["admin_dsn"])
    with psycopg.connect(**admin, autocommit=True, connect_timeout=3) as c:
        found = c.execute("SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s", (name,)).fetchone()
        if found and (found[0] != "hydro_migrator" or not marker.exists()):
            raise SystemExit("Database is not bound to this M04 fixture; no reset performed")
        if not found:
            c.execute(sql.SQL("CREATE DATABASE {} OWNER hydro_migrator").format(sql.Identifier(name)))
    private_directory(private)
    marker.write_text(json.dumps({"database": name, "purpose": "M04_BROWSER_ONLY"}))
    with psycopg.connect(**{**admin, "dbname": name}, autocommit=True, connect_timeout=3) as c:
        c.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    owner_url = make_url(operator["migration_url"]).set(database=name).render_as_string(hide_password=False)
    runtime["database_url"] = make_url(runtime["database_url"]).set(database=name).render_as_string(hide_password=False)
    runtime["mail_directory"] = str(private / "mail")
    runtime["hmac_key"] = secrets.token_urlsafe(48)
    (private / "runtime.json").write_text(json.dumps(runtime))
    env = {**os.environ, "PYTHONPATH": str(ROOT / "services/api"), "HYDRO_MIGRATION_URL": owner_url}
    subprocess.run([sys.executable, "-m", "alembic", "-c", "services/api/alembic.ini", "upgrade", "head"], cwd=ROOT, env=env, check=True)
    owner = create_engine(owner_url, hide_parameters=True)
    password = secrets.token_urlsafe(24)
    with owner.begin() as c:
        assert one(c, "SELECT current_database() AS n")["n"] == name
        c.exec_driver_sql("TRUNCATE " + ",".join(sorted(TABLES)) + " RESTART IDENTITY CASCADE")
        org, member, _ = bootstrap(c, confirmed_database=name, slug="synthetic-utility-a", name="SYNTHETIC integration utility A", email="admin-a@example.invalid", display_name="Synthetic administrator A", password=password, reporting_enabled=True)
        other, _, _ = bootstrap(c, confirmed_database=name, slug="synthetic-utility-b", name="SYNTHETIC integration utility B", email="admin-b@example.invalid", display_name="Synthetic administrator B", password=password, reporting_enabled=True)
    settings = Settings.model_validate(runtime)
    app = create_app(settings)
    clients = []

    def client():
        obj = Client(app)
        clients.append(obj)
        return obj

    fixture = {"app": app, "owner": owner, "settings": settings, "org": org, "admin": member, "other": other, "password": password, "client": client}
    flow = setup(fixture)
    # Separate synthetic identities keep the service suite independent of M04's
    # deliberate role revocation and reassignment scenarios.
    _, service_tech = provision(fixture, "TECHNICIAN", "service-tech@example.invalid", flow["admin"])
    provision(fixture, "SUPERVISOR", "service-supervisor@example.invalid", flow["admin"])
    register(fixture, "service-citizen@example.invalid")
    register(fixture, "service-stranger@example.invalid")
    _, other_tech = provision(fixture, "TECHNICIAN", "other-tech@example.invalid", flow["admin"])
    stranger = register(fixture, "other-citizen@example.invalid")
    login(fixture, "other-citizen@example.invalid", stranger)
    stranger_report = expect(mutate(stranger, f"/api/v1/orgs/{org['id']}/complaints", {"category": "VISIBLE_LEAK", "description": "SYNTHETIC another resident report, never visible to the current resident.", "coarse_area": "SYNTHETIC separate locality", "photo_consent": False, "attachment_ids": []}), 201)
    incident, work = assigned_work(fixture, flow)
    base = flow["base"]
    junctions = []
    for ref, coordinates in [("SYNTHETIC-JA", [78.0, 17.0]), ("SYNTHETIC-JB", [78.001, 17.0])]:
        junctions.append(expect(mutate(flow["engineer"], base + "/junctions", {"zone_id": flow["zone"]["id"], "external_ref": ref, "geometry": {"type": "Point", "coordinates": coordinates}, "topology_quality": "UNVERIFIED"}), 201))
    pipe = expect(mutate(flow["engineer"], base + "/pipes", {"zone_id": flow["zone"]["id"], "from_junction_id": junctions[0]["id"], "to_junction_id": junctions[1]["id"], "geometry": {"type": "LineString", "coordinates": [j["geometry"]["coordinates"] for j in junctions]}, "material": "SYNTHETIC PVC reference", "diameter_mm": 32, "path_length_m": None, "topology_quality": "UNVERIFIED"}), 201)
    other_admin = login(fixture, "admin-b@example.invalid")
    expect(mutate(other_admin, f"/api/v1/orgs/{other['id']}/invitations", {"email": "admin-a@example.invalid", "role": "ADMIN"}), 200)
    expect(flow["admin"].request("POST", "/api/v1/auth/invitation-accept", json={"token": token(fixture, "INVITATION", "admin-a@example.invalid")}), 200)
    for item in clients:
        item.close()
    app.state.engine.dispose()
    owner.dispose()
    certificate, key = private / "localhost.crt", private / "localhost.key"
    subprocess.run([args.openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2", "-keyout", str(key), "-out", str(certificate), "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"], capture_output=True, check=True)
    public_key = subprocess.check_output([args.openssl, "x509", "-in", str(certificate), "-pubkey", "-noout"])
    der = subprocess.check_output([args.openssl, "pkey", "-pubin", "-outform", "der"], input=public_key)
    browser = {"provenance": "SYNTHETIC_BROWSER_INTEGRATION_ONLY", "password": password, "other_complaint": stranger_report["id"], "org": str(org["id"]), "other_org": str(other["id"]), "zone": flow["zone"]["id"], "tech_membership": flow["tech_membership"]["id"], "other_tech_membership": other_tech["id"], "incident": incident["id"], "work_order": work["id"], "junctions": [j["id"] for j in junctions], "pipe": pipe["id"], "certificate_spki": base64.b64encode(hashlib.sha256(der).digest()).decode()}
    browser["service_tech_membership"] = service_tech["id"]
    (private / "browser.json").write_text(json.dumps(browser))
    if os.name != "nt":
        for path in private.glob("*.json"):
            path.chmod(0o600)
        key.chmod(0o600)
    print("Prepared real M04 synthetic browser fixtures; secrets retained only in private directory.")


if __name__ == "__main__":
    main()
