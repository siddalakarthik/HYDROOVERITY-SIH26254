"""Real PostgreSQL scientific boundary acceptance; never load evaluator truth."""

import copy
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import pytest
from helpers import expect, login, mutate, provision, register

from hydro.config import ROOT
from hydro.db import context, one
from hydro.science_data import Case, digest, load_catalogue


@pytest.fixture
def science(env):
    path = os.environ.get("HYDRO_SCIENCE_CATALOGUE", str(ROOT / "data/samples/m06"))
    pins = json.loads((ROOT / "data/schemas/m06-observation-pins.json").read_text())
    data = load_catalogue(path, pins["catalogue_sha256"])
    env["settings"].science_catalogue_path = Path(path)
    env["settings"].science_catalogue_sha256 = pins["catalogue_sha256"]
    engineer, membership = provision(env, "ENGINEER", "science@example.invalid")
    return engineer, membership, data, f"/api/v1/orgs/{env['org']['id']}/scientific-replays"


def test_scientific_ingestion_retrieval_replay_export_and_stream(env, science):
    client, _, data, base = science
    listing = expect(client.request("GET", base + "/catalogue"), 200)
    assert len(listing["items"]) == 69
    assert listing["source_category"] == "SIMULATION"
    key = uuid4()
    row = expect(mutate(client, base, {"scenario_code": "H11"}, key=key), 200)
    assert expect(mutate(client, base, {"scenario_code": "H11"}, key=key), 200) == row
    expect(mutate(client, base, {"scenario_code": "H01"}, key=key), 409)
    detail = expect(client.request("GET", base + "/" + row["id"]), 200)
    expected = next(case for case in data["cases"] if case["code"] == "H11")
    assert detail["snapshot"]["case"] == expected
    assert digest(detail["snapshot"]) == row["content_hash"]
    assert expect(client.request("GET", base + "/" + row["id"] + "/export"), 200) == detail
    cursor, samples = 0, []
    while cursor is not None:
        page = expect(
            client.request("GET", base + "/" + row["id"] + f"/frames?offset={cursor}&limit=13"), 200
        )
        samples.extend(page["items"])
        cursor = page["next_offset"]
    assert len(samples) == len(expected["data"]["time_s"])
    assert [v["sequence"] for v in samples] == list(range(len(samples)))
    assert [v["values"]["pressure_bar"] for v in samples] == expected["data"]["pressure_bar"]
    stream = client.request("GET", base + "/" + row["id"] + "/events?offset=13&limit=13")
    assert stream.status_code == 200 and stream.headers["content-type"].startswith(
        "text/event-stream"
    )
    assert stream.text.count("event: observation") == 13
    assert '"next_offset": 26' in stream.text and "SIMULATION" in stream.text
    assert len(expect(client.request("GET", base), 200)["items"]) == 1
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM incidents")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM work_orders")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM verification_records")["n"] == 0
        assert (
            one(
                c, "SELECT workspace_mode FROM domain_events WHERE event_type='SIMULATION_IMPORTED'"
            )["workspace_mode"]
            == "SIMULATION"
        )


def test_scientific_role_tenant_csrf_and_input_boundaries(env, science):
    client, member, _, base = science
    row = expect(mutate(client, base, {"scenario_code": "A01"}), 200)
    resident = register(env, "resident-science@example.invalid")
    login(env, "resident-science@example.invalid", resident)
    administrator = login(env, "admin-a@example.invalid")
    for denied in (resident, administrator):
        for suffix in ("/catalogue", "", "/" + row["id"], "/" + row["id"] + "/events"):
            expect(denied.request("GET", base + suffix), 403)
    other = base.replace(str(env["org"]["id"]), str(env["other"]["id"]))
    expect(client.request("GET", other + "/" + row["id"]), 404)
    expect(client.raw("POST", base, json={"scenario_code": "H01"}), 403)
    for body in (
        {"scenario_code": "H01", "seed": 1},
        {"scenario_code": "../../evaluation"},
        {"scenario_code": "H01", "source_category": "FIELD"},
        {"scenario_code": "H01", "truth": {}},
    ):
        expect(mutate(client, base, body), 422)
    for suffix in ("?offset=-1", "?limit=0", "?limit=201", "?truth=true", "?offset=9999"):
        expect(client.request("GET", base + "/" + row["id"] + "/frames" + suffix), 422)
    with env["owner"].begin() as c:
        user_id = one(
            c, "SELECT user_id FROM organization_memberships WHERE id=:i", i=member["id"]
        )["user_id"]
    with env["app"].state.engine.begin() as c:
        context(c, user_id, env["other"]["id"])
        assert one(c, "SELECT count(*) AS n FROM scientific_replays")["n"] == 0


def test_truth_injection_and_unfavorable_results(env, science, tmp_path):
    _, _, data, _ = science
    assert data["historical_benchmark"]["acoustics"]["confidently_wrong_intervals"] == 20
    nominal = data["historical_benchmark"]["guard"]["nominal"]
    assert nominal["guard5"]["f1"] < nominal["pad"]["f1"] < nominal["multizone"]["f1"]
    assert {c["data"]["outcome"] for c in data["cases"] if c["code"].startswith("V-")} == {
        "PASSED",
        "FAILED",
        "NOT_VERIFIABLE",
    }
    for key in ("truth", "seed", "position_m", "hidden_label", "artifact_path"):
        altered = copy.deepcopy(data)
        altered["cases"][0]["data"][key] = "private"
        target = tmp_path / "poison.json"
        target.write_text(json.dumps(altered))
        with pytest.raises(ValueError):
            load_catalogue(target, digest(altered))
    for case in data["cases"]:
        Case.model_validate(case)
        if case["data"]["module"] == "GUARD-5":
            assert case["data"]["channels"] == ["A", "B", "C", "EXT", "BYPASS"]
            assert case["data"]["health"] == ["UNKNOWN"] * 5


def test_replay_concurrency_revocation_immutability_and_rollback(env, science, monkeypatch):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy.exc import DBAPIError

    from hydro.db import execute

    first, member, _, base = science
    second = login(env, "science@example.invalid")
    key = uuid4()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: expect(
                    mutate(client, base, {"scenario_code": "V-missing_post_evidence"}, key=key), 200
                ),
                (first, second),
            )
        )
    assert results[0]["id"] == results[1]["id"]
    detail = expect(first.request("GET", base + "/" + results[0]["id"]), 200)
    assert detail["snapshot"]["case"]["data"]["outcome"] == "NOT_VERIFIABLE"
    assert detail["snapshot"]["case"]["data"]["guard"]["health"] == ["UNKNOWN"] * 5
    with pytest.raises(DBAPIError):
        with env["owner"].begin() as c:
            execute(c, "UPDATE scientific_replays SET scenario_code='H01'")
    monkeypatch.setenv("HYDRO_MIGRATION_URL", os.environ["HYDRO_TEST_OWNER_URL"])
    with pytest.raises(RuntimeError, match="forward-only"):
        command.downgrade(Config(str(ROOT / "services/api/alembic.ini")), "m07_a_001")
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE role_assignments SET revoked_at=now() WHERE membership_id=:m AND role_id=(SELECT id FROM roles WHERE code='ENGINEER')",
            m=member["id"],
        )
    for suffix in ("", "/frames", "/events", "/export"):
        expect(first.request("GET", base + "/" + results[0]["id"] + suffix), 403)
    expect(mutate(first, base, {"scenario_code": "V-missing_post_evidence"}, key=key), 403)


def test_missing_catalogue_is_explicitly_unavailable(env, science):
    client, _, _, base = science
    env["settings"].science_catalogue_path = None
    expect(client.request("GET", base + "/catalogue"), 503)
    expect(mutate(client, base, {"scenario_code": "H01"}), 503)
