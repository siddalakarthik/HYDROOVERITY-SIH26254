"""Real PostgreSQL bounded replay acceptance; record updates are not physical freshness."""

import asyncio
import json
from uuid import uuid4

import pytest
from conftest import Client
from helpers import expect, login, mutate, register
from test_workflow import complaint_body

from hydro.db import execute, one
from hydro.main import create_app


def endpoints(env):
    base = f"/api/v1/orgs/{env['org']['id']}"
    return base + "/events/history", base + "/events", base


def initial(client, path):
    response = client.request("GET", path)
    page = expect(response, 200)
    assert response.headers["x-hydro-reset-required"] == "true"
    assert page["items"] == [] and len(page["next_cursor"]) == 64
    return page["next_cursor"]


def test_realtime_real_receipt_after_snapshot_watermark_is_replayed_safely(env):
    client = register(env, "realtime-resident@example.invalid")
    login(env, "realtime-resident@example.invalid", client)
    path, _, base = endpoints(env)
    cursor = initial(client, path)
    receipt = expect(mutate(client, base + "/complaints", complaint_body()), 201)
    response = client.request("GET", path, params={"cursor": cursor})
    page = expect(response, 200)
    assert response.headers["x-hydro-reset-required"] == "false"
    assert [item["resource_id"] for item in page["items"]] == [receipt["id"]]
    assert page["items"][0]["event_type"] == "record_changed.citizen_complaints"
    assert complaint_body()["description"] not in response.text
    assert "An authorized record changed" in response.text
    assert (
        expect(client.request("GET", path, params={"cursor": page["next_cursor"]}), 200)["items"]
        == []
    )
    replay = expect(client.request("GET", path, params={"cursor": cursor}), 200)
    assert replay["items"] == page["items"]
    with env["owner"].begin() as c:
        row = one(c, "SELECT * FROM realtime_cursors ORDER BY created_at,id LIMIT 1")
        assert "token_value" not in row and len(bytes(row["token_hash"])) == 32


def test_realtime_owner_and_tenant_denial_and_foreign_cursor_reset(env):
    clients = [
        register(env, email)
        for email in ("realtime-a@example.invalid", "realtime-b@example.invalid")
    ]
    for client, email in zip(
        clients, ("realtime-a@example.invalid", "realtime-b@example.invalid"), strict=True
    ):
        login(env, email, client)
    path, _, base = endpoints(env)
    first = initial(clients[0], path)
    second = initial(clients[1], path)
    receipt = expect(mutate(clients[1], base + "/complaints", complaint_body()), 201)
    own = expect(clients[1].request("GET", path, params={"cursor": second}), 200)
    assert own["items"][0]["resource_id"] == receipt["id"]
    assert expect(clients[0].request("GET", path, params={"cursor": first}), 200)["items"] == []
    foreign = clients[0].request("GET", path, params={"cursor": own["next_cursor"]})
    assert (
        expect(foreign, 200)["items"] == [] and foreign.headers["x-hydro-reset-required"] == "true"
    )
    expect(clients[0].request("GET", f"/api/v1/orgs/{env['other']['id']}/events/history"), 404)


def resident(env):
    client = register(env, "realtime-resident@example.invalid")
    login(env, "realtime-resident@example.invalid", client)
    return client


def test_realtime_cursor_expiry_and_permission_change_require_explicit_reset(env):
    client = resident(env)
    path, _, base = endpoints(env)
    cursor = initial(client, path)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE realtime_cursors SET created_at=now()-interval '8 days',expires_at=now()-interval '1 day'",
        )
    expired = client.request("GET", path, params={"cursor": cursor})
    assert (
        expect(expired, 200)["items"] == [] and expired.headers["x-hydro-reset-required"] == "true"
    )
    fresh = expired.json()["next_cursor"]
    assert fresh != cursor
    # Add an irrelevant permission to prove an otherwise still-authorized role
    # fingerprint change resets rather than silently accepting an old grant view.
    with env["owner"].begin() as c:
        execute(
            c,
            "INSERT INTO permissions(code,description) VALUES('synthetic.unrelated.read','SYNTHETIC role fingerprint fixture')",
        )
        execute(
            c,
            "INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r,permissions p WHERE r.code='CITIZEN' AND p.code='synthetic.unrelated.read'",
        )
    changed = client.request("GET", path, params={"cursor": fresh})
    assert (
        expect(changed, 200)["items"] == [] and changed.headers["x-hydro-reset-required"] == "true"
    )
    with env["owner"].begin() as c:
        execute(
            c,
            "DELETE FROM role_permissions WHERE permission_id=(SELECT id FROM permissions WHERE code='synthetic.unrelated.read')",
        )
        execute(c, "DELETE FROM permissions WHERE code='synthetic.unrelated.read'")


def test_realtime_cursor_is_durable_across_application_restart_and_key_rotation(env):
    client = resident(env)
    path, _, base = endpoints(env)
    cursor = initial(client, path)
    receipt = expect(mutate(client, base + "/complaints", complaint_body()), 201)
    restarted = create_app(env["settings"])
    other = Client(restarted)
    other.http.cookies.update(client.http.cookies)
    try:
        page = expect(other.request("GET", path, params={"cursor": cursor}), 200)
        assert page["items"][0]["resource_id"] == receipt["id"]
        from pydantic import SecretStr

        restarted.state.settings = env["settings"].model_copy(
            update={"hmac_key": SecretStr("SYNTHETIC-ROTATED-LOCAL-KEY-" + "x" * 40)}
        )
        reset = other.request("GET", path, params={"cursor": page["next_cursor"]})
        assert (
            expect(reset, 200)["items"] == [] and reset.headers["x-hydro-reset-required"] == "true"
        )
        assert reset.json()["next_cursor"] != page["next_cursor"]
    finally:
        other.close()
        restarted.state.engine.dispose()


def test_realtime_stored_private_summary_and_unknown_topics_never_disclose(env):
    client = resident(env)
    path, _, base = endpoints(env)
    cursor = initial(client, path)
    receipt = expect(mutate(client, base + "/complaints", complaint_body()), 201)
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE domain_events SET safe_summary=CAST(:value AS jsonb)",
            value=json.dumps({"private": "SYNTHETIC-SECRET-TRUTH-SENTINEL"}),
        )
        execute(
            c,
            "INSERT INTO domain_events(organization_id,event_type,resource_type,resource_id,workspace_mode,minimum_permission,occurred_at,safe_summary) VALUES(:o,'SYNTHETIC_PRIVATE','restricted_simulation_truth',:i,'OPERATIONAL','realtime.read',now(),CAST(:value AS jsonb))",
            o=env["org"]["id"],
            i=uuid4(),
            value=json.dumps({"truth_seed": "SYNTHETIC-SECRET-TRUTH-SENTINEL"}),
        )
    response = client.request("GET", path, params={"cursor": cursor})
    page = expect(response, 200)
    assert len(page["items"]) == 1 and page["items"][0]["resource_id"] == receipt["id"]
    assert "SYNTHETIC-SECRET-TRUTH-SENTINEL" not in response.text
    assert "restricted_simulation_truth" not in response.text


def test_realtime_bounded_history_pages_advance_without_losing_owned_records(env):
    client = resident(env)
    path, _, base = endpoints(env)
    cursor = initial(client, path)
    expected = [
        expect(mutate(client, base + "/complaints", complaint_body()), 201)["id"] for _ in range(3)
    ]
    observed = []
    for _ in range(3):
        page = expect(client.request("GET", path, params={"cursor": cursor, "limit": 1}), 200)
        observed += [r["resource_id"] for r in page["items"]]
        cursor = page["next_cursor"]
    assert observed == expected
    expect(client.request("GET", path, params={"limit": 101}), 422)
    expect(client.request("GET", path, params={"workspace_mode": "SIMULATION"}), 403)
    expect(client.request("GET", path, params={"workspace_mode": "FIELD"}), 422)
    expect(client.request("GET", path, params={"organization_id": env["other"]["id"]}), 422)


def test_realtime_sse_reset_framing_and_connection_capacity_release(env, monkeypatch):
    client = resident(env)
    _, stream, _ = endpoints(env)
    import hydro.realtime as module

    monkeypatch.setattr(module, "CONNECTION_SECONDS", 0)
    response = client.request("GET", stream)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: reset_required\n" in response.text and "event: checkpoint\n" in response.text
    assert "event: reconnect_required\n" in response.text
    assert "not-physical-sensor-freshness" in response.headers["x-hydro-record-updates"]
    semaphore = env["app"].state.realtime_capacity
    assert all(semaphore.acquire(blocking=False) for _ in range(20))
    assert not semaphore.acquire(blocking=False)
    for _ in range(20):
        semaphore.release()


def test_realtime_revoked_session_and_capacity_are_not_silent_success(env):
    client = resident(env)
    path, stream, _ = endpoints(env)
    initial(client, path)
    semaphore = env["app"].state.realtime_capacity
    for _ in range(20):
        assert semaphore.acquire(blocking=False)
    try:
        response = client.request("GET", stream)
        assert expect(response, 503)["error"]["code"] == "STREAM_CAPACITY"
    finally:
        for _ in range(20):
            semaphore.release()
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE sessions SET revoked_at=now() WHERE id IN (SELECT session_id FROM realtime_cursors)",
        )
    expect(client.request("GET", path), 401)
    expect(client.request("GET", stream), 401)


def test_realtime_revocation_between_history_and_emission_discloses_no_record(env, monkeypatch):
    client = resident(env)
    path, stream, base = endpoints(env)
    cursor = initial(client, path)
    receipt = expect(mutate(client, base + "/complaints", complaint_body()), 201)
    import hydro.realtime as module

    original = module.current_event_allowed

    def revoke(*args):
        with env["owner"].begin() as c:
            execute(
                c,
                "UPDATE sessions SET revoked_at=now() WHERE id IN (SELECT session_id FROM realtime_cursors)",
            )
        return original(*args)

    monkeypatch.setattr(module, "current_event_allowed", revoke)
    response = client.request("GET", stream, headers={"Last-Event-ID": cursor})
    assert response.status_code == 200 and "event: authorization_lost\n" in response.text
    assert receipt["id"] not in response.text and "event: record_changed\n" not in response.text


def test_realtime_slow_consumer_timeout_closes_generator_and_releases_slot(monkeypatch):
    import hydro.realtime as module

    monkeypatch.setattr(module, "SEND_SECONDS", 0.01)
    released, closed = [], []

    async def body():
        try:
            yield "event: checkpoint\ndata: {}\n\n"
        finally:
            closed.append(True)

    async def blocked_send(message):
        if message["type"] == "http.response.body":
            await asyncio.sleep(60)

    response = module.BoundedStreamingResponse(body(), on_close=lambda: released.append(True))
    asyncio.run(response({"type": "http", "asgi": {"spec_version": "2.4"}}, None, blocked_send))
    assert closed == [True] and released == [True]


def test_realtime_disconnect_before_headers_also_releases_capacity():
    from starlette.requests import ClientDisconnect

    from hydro.realtime import BoundedStreamingResponse

    released = []

    async def body():
        yield "data: {}\n\n"

    async def disconnected(message):
        raise OSError("SYNTHETIC consumer disconnected before headers")

    response = BoundedStreamingResponse(body(), on_close=lambda: released.append(True))
    with pytest.raises(ClientDisconnect):
        asyncio.run(response({"type": "http", "asgi": {"spec_version": "2.4"}}, None, disconnected))
    assert released == [True]


def test_realtime_runtime_rls_cannot_read_or_retarget_another_session_cursor(env):
    from sqlalchemy.exc import DBAPIError

    from hydro.db import context

    client = resident(env)
    path, _, _ = endpoints(env)
    initial(client, path)
    with env["owner"].begin() as c:
        cursor = one(c, "SELECT * FROM realtime_cursors LIMIT 1")
        user = one(
            c, "SELECT user_id FROM organization_memberships WHERE id=:i", i=cursor["membership_id"]
        )
    with env["app"].state.engine.begin() as c:
        context(c, user["user_id"], env["org"]["id"])
        execute(c, "SELECT set_config('hydro.session_id',:s,true)", s=str(uuid4()))
        assert one(c, "SELECT count(*) AS n FROM realtime_cursors")["n"] == 0
        assert not one(
            c,
            "UPDATE realtime_cursors SET revoked_at=now() WHERE id=:i RETURNING id",
            i=cursor["id"],
        )
    with pytest.raises(DBAPIError), env["app"].state.engine.begin() as c:
        context(c, user["user_id"], env["org"]["id"])
        execute(c, "SELECT set_config('hydro.session_id',:s,true)", s=str(cursor["session_id"]))
        execute(
            c,
            "UPDATE realtime_cursors SET organization_id=:o WHERE id=:i",
            o=env["other"]["id"],
            i=cursor["id"],
        )


def test_realtime_deactivated_identity_cannot_read_cursor_through_runtime_rls(env):
    from hydro.db import context

    client = resident(env)
    path, _, _ = endpoints(env)
    initial(client, path)
    with env["owner"].begin() as c:
        cursor = one(c, "SELECT * FROM realtime_cursors LIMIT 1")
        user = one(c, "SELECT user_id FROM sessions WHERE id=:i", i=cursor["session_id"])
        execute(c, "UPDATE users SET deactivated_at=now() WHERE id=:i", i=user["user_id"])
    with env["app"].state.engine.begin() as c:
        context(c, user["user_id"], env["org"]["id"])
        execute(c, "SELECT set_config('hydro.session_id',:s,true)", s=str(cursor["session_id"]))
        assert one(c, "SELECT count(*) AS n FROM realtime_cursors")["n"] == 0
    assert client.request("GET", path).status_code == 401


def test_realtime_has_separate_bounded_admission_and_cannot_weaken_existing_limits(env):
    from hydro.errors import Problem

    client = resident(env)
    path, _, _ = endpoints(env)
    with env["owner"].begin() as c:
        session = one(
            c,
            "SELECT id FROM sessions WHERE auth_level='AUTHENTICATED' ORDER BY created_at DESC LIMIT 1",
        )
    limits = env["app"].state.limits
    for _ in range(121):
        try:
            limits.hit("general", str(session["id"]), 120, 60)
        except Problem as error:
            assert error.status == 429
            break
    else:
        pytest.fail("Existing general limit did not enforce its original bound")
    expect(client.request("GET", "/api/v1/me"), 429)
    for _ in range(30):
        expect(client.request("GET", path), 200)
    response = client.request("GET", path)
    expect(response, 429)
    assert response.headers["retry-after"] == "60"
    expect(client.request("GET", "/api/v1/me"), 429)


def test_realtime_populated_migration_downgrade_refuses_to_erase_cursors(env):
    from alembic import command
    from alembic.config import Config

    from hydro.config import ROOT

    client = resident(env)
    path, _, _ = endpoints(env)
    initial(client, path)
    cfg = Config(str(ROOT / "services/api/alembic.ini"))
    cfg.attributes["connection"] = env["owner"].connect()
    try:
        with pytest.raises(RuntimeError, match="non-destructive downgrade refused"):
            command.downgrade(cfg, "pre_m10_002")
    finally:
        cfg.attributes["connection"].close()
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "pre_m10_003"
        assert one(c, "SELECT count(*) AS n FROM realtime_cursors")["n"] == 1


def test_realtime_reassignment_rechecks_current_parent_instead_of_event_recipient(env):
    from helpers import provision
    from test_workflow import assigned_work, setup

    f = setup(env)
    _, work = assigned_work(env, f)
    other, member = provision(env, "TECHNICIAN", "realtime-replacement@example.invalid", f["admin"])
    path = f["base"] + "/events/history"
    old_cursor = initial(f["technician"], path)
    new_cursor = initial(other, path)
    expect(
        mutate(
            f["supervisor"],
            f["base"] + "/work-orders/" + work["id"] + "/assignment",
            {
                "assignee_membership_id": member["id"],
                "due_at": None,
                "reason": "SYNTHETIC realtime reassignment boundary",
            },
            work["version"],
        ),
        201,
    )
    old = expect(f["technician"].request("GET", path, params={"cursor": old_cursor}), 200)
    new = expect(other.request("GET", path, params={"cursor": new_cursor}), 200)
    assert work["id"] not in [e["resource_id"] for e in old["items"]]
    assert work["id"] in [e["resource_id"] for e in new["items"]]


def test_realtime_service_appointment_events_are_current_owner_or_assignee_only(env):
    from test_scheduling import booking_fixture, confirm, request_visit

    f = booking_fixture(env)
    path = f["base"] + "/events/history"
    citizen_cursor = initial(f["citizen"], path)
    tech_cursor = initial(f["technician"], path)
    visit = confirm(f, request_visit(f))["appointment"]
    for actor, cursor in [(f["citizen"], citizen_cursor), (f["technician"], tech_cursor)]:
        page = expect(actor.request("GET", path, params={"cursor": cursor}), 200)
        assert visit["id"] in [e["resource_id"] for e in page["items"]]
        assert all(
            "internal_reason" not in e and "safe resident" not in e["safe_summary"]
            for e in page["items"]
        )


def test_realtime_snapshot_waits_for_existing_mutation_commit_then_replays_new_change(env):
    import threading
    from concurrent.futures import ThreadPoolExecutor

    client = resident(env)
    path, _, base = endpoints(env)
    started = threading.Event()
    with ThreadPoolExecutor(max_workers=1) as pool:
        with env["owner"].begin() as c:
            execute(
                c,
                "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
                key="hydro-dispatch:" + str(env["org"]["id"]),
            )

            def snapshot():
                started.set()
                return client.request("GET", path)

            future = pool.submit(snapshot)
            assert started.wait(2)
            # The lock is still held. Snapshot cannot commit a cursor before this transaction.
            with pytest.raises(TimeoutError):
                future.result(timeout=0.05)
        cursor = expect(future.result(timeout=5), 200)["next_cursor"]
    row = expect(mutate(client, base + "/complaints", complaint_body()), 201)
    page = expect(client.request("GET", path, params={"cursor": cursor}), 200)
    assert row["id"] in [e["resource_id"] for e in page["items"]]


def test_realtime_real_loopback_sse_disconnect_and_reconnect_uses_received_cursor(env, monkeypatch):
    import socket
    import threading

    import httpx
    import uvicorn

    import hydro.realtime as module

    client = resident(env)
    path, stream, base = endpoints(env)
    cursor = initial(client, path)
    first = expect(mutate(client, base + "/complaints", complaint_body()), 201)
    monkeypatch.setattr(module, "POLL_SECONDS", 0.02)
    monkeypatch.setattr(module, "CONNECTION_SECONDS", 0.1)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            env["app"],
            host="127.0.0.1",
            port=port,
            lifespan="off",
            access_log=False,
            log_level="critical",
        )
    )
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    cookie = "; ".join(f"{k}={v}" for k, v in client.http.cookies.items())
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5, trust_env=False) as http:
            with http.stream(
                "GET", stream, headers={"Cookie": cookie, "Last-Event-ID": cursor}
            ) as response:
                assert response.status_code == 200
                lines = []
                for line in response.iter_lines():
                    lines.append(line)
                    if line.startswith("data:") and first["id"] in line:
                        break
                assert "event: record_changed" in lines
                received = next(line[4:] for line in lines if line.startswith("id: "))
            second = expect(mutate(client, base + "/complaints", complaint_body()), 201)
            response = http.get(stream, headers={"Cookie": cookie, "Last-Event-ID": received})
            assert response.status_code == 200 and second["id"] in response.text
            assert first["id"] not in response.text and "event: reconnect_required" in response.text
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
        assert not thread.is_alive()
