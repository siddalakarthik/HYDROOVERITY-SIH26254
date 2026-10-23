"""Real PostgreSQL M07-A acceptance. All fixtures are synthetic, never field evidence."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from helpers import expect, login, mutate, provision, register
from sqlalchemy.exc import DBAPIError
from test_workflow import incident, setup, transition

from hydro.config import ROOT
from hydro.db import MIGRATION_HEAD, context, execute, one, query


def submission(**overrides):
    return {
        "category": "VISIBLE_LEAK",
        "description": "SYNTHETIC visible water concern for service review",
        "coarse_area": "SYNTHETIC public landmark",
        "origin_complaint_id": None,
        "expected_complaint_version": None,
        "follow_up_of_id": None,
        "service_privacy_acknowledged": True,
        **overrides,
    }


def resident(env, email="resident@example.invalid"):
    client = register(env, email)
    return login(env, email, client)


def create(client, base):
    return expect(mutate(client, base + "/service-requests", submission()), 201)


def triage(sup, path, row, target):
    return expect(
        mutate(
            sup,
            path + "/triage",
            {
                "target": target,
                "public_message": "SYNTHETIC safe resident update",
                "internal_reason": "SYNTHETIC private operational reason never for resident",
            },
            row["version"],
        ),
        200,
    )


def test_service_intake_reference_owned_tracking_and_no_automatic_incident(env):
    citizen = resident(env)
    base = f"/api/v1/orgs/{env['org']['id']}"
    key = uuid4()
    row = expect(mutate(citizen, base + "/service-requests", submission(), key=key), 201)
    assert row["status"] == "SUBMITTED" and row["current_appointment"] is None
    assert row["preferences"] is None and row["verification_summary"] == "NOT_APPLICABLE"
    assert len(row["tracking_reference"]) == 30 and row["tracking_reference"].startswith("HYS-")
    assert not {"owner_membership_id", "work_links", "internal_event_summary"} & row.keys()
    assert (
        expect(mutate(citizen, base + "/service-requests", submission(), key=key), 201)["id"]
        == row["id"]
    )
    expect(
        mutate(
            citizen,
            base + "/service-requests",
            submission(description="SYNTHETIC different content"),
            key=key,
        ),
        409,
    )
    page = expect(citizen.request("GET", base + "/service-requests?limit=1"), 200)
    assert page["items"][0]["id"] == row["id"]
    response = citizen.request("GET", base + "/service-requests/" + row["id"])
    assert response.headers["etag"] == '"1"' and response.headers["cache-control"] == "no-store"
    found = expect(
        citizen.request(
            "POST",
            base + "/service-request-lookups",
            json={"tracking_reference": row["tracking_reference"]},
        ),
        200,
    )
    assert found["id"] == row["id"]
    expect(
        mutate(
            citizen,
            base + "/service-request-lookups",
            {"tracking_reference": row["tracking_reference"]},
        ),
        400,
    )
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM incidents")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM work_orders")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM service_requests")["n"] == 1


def test_service_ownership_role_tenant_csrf_and_privacy_gates(env):
    citizen = resident(env)
    other = resident(env, "stranger@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    row = create(citizen, base)
    path = base + "/service-requests/" + row["id"]
    expect(other.request("GET", path), 404)
    expect(
        other.request(
            "POST",
            base + "/service-request-lookups",
            json={"tracking_reference": row["tracking_reference"]},
        ),
        404,
    )
    expect(
        citizen.request("GET", path.replace(str(env["org"]["id"]), str(env["other"]["id"]))), 404
    )
    expect(citizen.request("GET", path + "/timeline?audience=INTERNAL"), 403)
    expect(login(env, "admin-a@example.invalid").request("GET", path), 403)
    expect(env["client"]().request("GET", path), 401)
    expect(
        citizen.raw(
            "POST",
            path + "/follow-ups",
            json={"operation_id": str(uuid4()), "message": "SYNTHETIC follow-up"},
        ),
        403,
    )
    expect(citizen.request("GET", path + "/visit-access"), 503)
    expect(mutate(citizen, path + "/visit-access", {}, 1, method="PUT"), 503)
    expect(mutate(citizen, path + "/visit-preferences", {}, 1, method="PUT"), 503)
    expect(
        mutate(citizen, base + "/service-requests", submission(service_privacy_acknowledged=False)),
        422,
    )
    expect(
        mutate(
            citizen, base + "/service-requests", submission(description="SYNTHETIC\x00bad data")
        ),
        422,
    )


def test_supervisor_triage_followup_private_and_public_timeline(env):
    citizen = resident(env)
    sup, _ = provision(env, "SUPERVISOR", "supervisor@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    row = create(citizen, base)
    path = base + "/service-requests/" + row["id"]
    row = triage(sup, path, row, "UNDER_REVIEW")
    row = triage(sup, path, row, "AWAITING_RESIDENT")
    expect(
        mutate(
            citizen,
            path + "/follow-ups",
            {"operation_id": str(uuid4()), "message": "SYNTHETIC requested information"},
        ),
        428,
    )
    key, operation = uuid4(), str(uuid4())
    follow = {"operation_id": operation, "message": "SYNTHETIC requested information"}
    receipt = expect(mutate(citizen, path + "/follow-ups", follow, row["version"], key), 201)
    assert (
        expect(mutate(citizen, path + "/follow-ups", follow, row["version"], key), 201) == receipt
    )
    row = expect(sup.request("GET", path), 200)
    assert row["status"] == "UNDER_REVIEW"
    expect(
        mutate(
            sup,
            path + "/triage",
            {
                "target": "ACCEPTED",
                "public_message": "SYNTHETIC update",
                "internal_reason": "SYNTHETIC reason",
            },
            1,
        ),
        412,
    )
    row = triage(sup, path, row, "ACCEPTED")
    update = expect(
        mutate(
            sup,
            path + "/public-updates",
            {
                "event_kind": "INFORMATION",
                "message": "SYNTHETIC reviewed progress",
                "supersedes_update_id": None,
            },
            row["version"],
        ),
        201,
    )
    row = expect(sup.request("GET", path), 200)
    expect(
        mutate(
            sup,
            path + "/public-updates",
            {
                "event_kind": "CORRECTION",
                "message": "SYNTHETIC corrected progress",
                "supersedes_update_id": update["id"],
            },
            row["version"],
        ),
        201,
    )
    safe = expect(citizen.request("GET", path + "/timeline"), 200)
    internal = expect(sup.request("GET", path + "/timeline?audience=INTERNAL"), 200)
    assert "private operational reason" not in str(safe)
    assert "private operational reason" in str(internal)
    assert all("internal_reason" not in x and "actor_membership_id" not in x for x in safe["items"])
    assert expect(sup.request("GET", base + "/service-requests"), 200)["items"][0][
        "owner_membership_id"
    ]
    row = expect(citizen.request("GET", path), 200)
    row = expect(
        mutate(
            citizen,
            path + "/transitions",
            {
                "action": "REQUEST_CANCELLATION",
                "reason_code": "RESIDENT",
                "public_message": "SYNTHETIC request cancellation",
            },
            row["version"],
        ),
        200,
    )
    assert row["cancellation_pending"] and row["status"] == "ACCEPTED"
    expect(
        mutate(
            citizen,
            path + "/transitions",
            {
                "action": "START_SERVICE",
                "reason_code": "START",
                "public_message": "SYNTHETIC request",
                "internal_reason": "SYNTHETIC reason",
            },
            row["version"],
        ),
        403,
    )


def test_service_decline_withdrawal_and_linked_recurrence(env):
    citizen = resident(env)
    sup, _ = provision(env, "SUPERVISOR", "supervisor@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    row = create(citizen, base)
    path = base + "/service-requests/" + row["id"]
    row = triage(sup, path, row, "UNDER_REVIEW")
    row = triage(sup, path, row, "DECLINED")
    expect(
        mutate(
            citizen,
            path + "/follow-ups",
            {"operation_id": str(uuid4()), "message": "Late follow-up"},
            row["version"],
        ),
        409,
    )
    follow = expect(
        mutate(citizen, base + "/service-requests", submission(follow_up_of_id=row["id"])), 201
    )
    follow = expect(
        mutate(
            citizen,
            base + "/service-requests/" + follow["id"] + "/transitions",
            {
                "action": "WITHDRAW",
                "reason_code": "RESIDENT",
                "public_message": "SYNTHETIC withdrawn concern",
            },
            follow["version"],
        ),
        200,
    )
    assert follow["status"] == "WITHDRAWN"


def test_findings_and_work_link_complete_without_fake_repair(env):
    f = setup(env)
    base, sup, tech, citizen = f["base"], f["supervisor"], f["technician"], f["citizen"]
    case = create(citizen, base)
    cp = base + "/service-requests/" + case["id"]
    case = triage(sup, cp, case, "UNDER_REVIEW")
    case = triage(sup, cp, case, "ACCEPTED")
    item = incident(env, f)
    ip = base + "/incidents/" + item["id"]
    body = {
        "incident_id": item["id"],
        "priority": "MEDIUM",
        "instructions": "SYNTHETIC investigation only",
        "task_purpose": "INVESTIGATION",
    }
    expect(mutate(sup, base + "/work-orders", body), 409)
    item = transition(sup, ip, item, "UNDER_REVIEW")
    item = transition(sup, ip, item, "INVESTIGATION_REQUIRED")
    work = expect(mutate(sup, base + "/work-orders", body), 201)
    wp = base + "/work-orders/" + work["id"]
    link = {
        "work_order_id": work["id"],
        "expected_work_version": work["version"],
        "purpose": "INVESTIGATION",
        "internal_reason": "SYNTHETIC operational linkage",
    }
    expect(mutate(sup, cp + "/work-order-links", link, case["version"]), 201)
    work = expect(
        mutate(
            sup,
            wp + "/assignment",
            {
                "assignee_membership_id": f["tech_membership"]["id"],
                "due_at": None,
                "reason": "SYNTHETIC assignment without appointment",
            },
            work["version"],
        ),
        201,
    )
    work = transition(tech, wp, work, "ACCEPTED")
    work = transition(tech, wp, work, "IN_PROGRESS")
    expect(
        mutate(
            tech,
            wp + "/transitions",
            {"target": "SUBMITTED_FOR_REVIEW", "reason": "SYNTHETIC missing findings"},
            work["version"],
        ),
        409,
    )
    body = {
        "operation_id": str(uuid4()),
        "assignment_version": work["assignment_version"],
        "observed_at": datetime.now(UTC).isoformat(),
        "findings": "SYNTHETIC inspection identified insufficient evidence",
        "no_repair_reason": "SYNTHETIC investigation only, no repair performed",
        "attachment_ids": [],
        "supersedes_id": None,
    }
    key = uuid4()
    result = expect(mutate(tech, wp + "/findings", body, work["version"], key), 201)
    assert expect(mutate(tech, wp + "/findings", body, work["version"], key), 201) == result
    assert result["resource"]["provenance"] == "MANUAL"
    expect(mutate(sup, wp + "/findings", body, work["version"]), 403)
    expect(citizen.request("GET", wp + "/findings"), 403)
    assert len(expect(tech.request("GET", wp + "/findings"), 200)["items"]) == 1
    assert len(expect(sup.request("GET", wp + "/findings"), 200)["items"]) == 1
    assert len(expect(f["engineer"].request("GET", wp + "/findings"), 200)["items"]) == 1
    work = expect(tech.request("GET", wp), 200)
    work = transition(tech, wp, work, "SUBMITTED_FOR_REVIEW")
    work = transition(sup, wp, work, "COMPLETED")
    case = expect(sup.request("GET", cp), 200)
    for action in ["REQUEST_REVIEW", "CLOSE"]:
        body = {
            "action": action,
            "reason_code": "INVESTIGATED",
            "public_message": "SYNTHETIC investigation outcome with no repair claim",
            "internal_reason": "SYNTHETIC review rationale",
        }
        if action == "CLOSE":
            body.update(
                service_outcome="NO_ACTION_WITH_REASON",
                child_dispositions=[],
                expected_work_versions=[{"work_order_id": work["id"], "version": work["version"]}],
            )
        case = expect(mutate(sup, cp + "/transitions", body, case["version"]), 200)
    assert case["status"] == "SERVICE_CLOSED" and case["verification_summary"] == "NOT_APPLICABLE"
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM repair_records")["n"] == 0
        assert one(c, "SELECT count(*) AS n FROM verification_records")["n"] == 0


def test_service_rls_blocks_other_owner_internal_history_and_pool_leakage(env):
    citizen = resident(env)
    other = resident(env, "stranger@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    row = create(citizen, base)
    with env["owner"].begin() as c:
        owner = one(c, "SELECT owner_membership_id FROM service_requests WHERE id=:i", i=row["id"])[
            "owner_membership_id"
        ]
        user = one(c, "SELECT user_id FROM organization_memberships WHERE id=:i", i=owner)[
            "user_id"
        ]
    with env["app"].state.engine.begin() as c:
        context(c, user, env["org"]["id"])
        assert one(c, "SELECT id FROM service_requests")
        assert one(c, "SELECT id FROM service_public_updates")
        assert not query(c, "SELECT id FROM service_request_events")
        assert not query(c, "SELECT id FROM service_work_order_links")
        context(c, user, env["other"]["id"])
        assert not query(c, "SELECT id FROM service_requests")
    with env["app"].state.engine.begin() as c:
        assert not query(c, "SELECT id FROM service_requests")
    with pytest.raises(DBAPIError):
        with env["owner"].begin() as c:
            execute(c, "UPDATE service_public_updates SET message='Must fail'")
    assert expect(other.request("GET", base + "/service-requests"), 200)["items"] == []


def test_service_empty_migration_roundtrip_and_populated_rollback_refusal(env, monkeypatch):
    monkeypatch.setenv("HYDRO_MIGRATION_URL", os.environ["HYDRO_TEST_OWNER_URL"])
    cfg = Config(str(ROOT / "services/api/alembic.ini"))
    command.downgrade(cfg, "m03_004")
    command.upgrade(cfg, "head")
    citizen = resident(env)
    create(citizen, f"/api/v1/orgs/{env['org']['id']}")
    with pytest.raises(RuntimeError, match="forward-only"):
        command.downgrade(cfg, "m03_004")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD
        assert one(c, "SELECT count(*) AS n FROM service_requests")["n"] == 1


def test_service_concurrent_idempotency_and_competing_versions(env):
    citizen = resident(env)
    other_session = login(env, "resident@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    key = uuid4()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda c: expect(mutate(c, base + "/service-requests", submission(), key=key), 201),
                [citizen, other_session],
            )
        )
    assert results[0]["id"] == results[1]["id"]
    path = base + "/service-requests/" + results[0]["id"]
    body = {
        "action": "WITHDRAW",
        "reason_code": "RESIDENT",
        "public_message": "SYNTHETIC competing withdrawal",
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(
            pool.map(
                lambda c: mutate(c, path + "/transitions", body, 1).status_code,
                [citizen, other_session],
            )
        )
    assert sorted(statuses) == [200, 412]


def test_service_origin_complaint_ownership_versions_and_single_conversion(env):
    f = setup(env)
    citizen, sup, base = f["citizen"], f["supervisor"], f["base"]
    stranger = resident(env, "stranger@example.invalid")
    complaint = expect(
        mutate(
            citizen,
            base + "/complaints",
            {
                "category": "LOW_PRESSURE",
                "description": "SYNTHETIC owned report for separate service review",
                "coarse_area": "SYNTHETIC locality",
                "photo_consent": False,
                "attachment_ids": [],
            },
        ),
        201,
    )
    body = submission(
        origin_complaint_id=complaint["id"], expected_complaint_version=complaint["version"]
    )
    expect(mutate(stranger, base + "/service-requests", body), 404)
    expect(
        mutate(citizen, base + "/service-requests", {**body, "expected_complaint_version": 99}), 412
    )
    key = uuid4()
    case = expect(mutate(citizen, base + "/service-requests", body, key=key), 201)
    expect(mutate(citizen, base + "/service-requests", body), 409)
    # The complaint may change after creation. Receipt replay still reauthorizes
    # ownership but must not demand its former version again.
    expect(
        mutate(
            sup,
            base + "/complaints/" + complaint["id"] + "/review",
            {
                "public_status": "UNDER_REVIEW",
                "public_message": "SYNTHETIC independent complaint review",
                "internal_reason": "SYNTHETIC private reason",
                "incident_id": None,
            },
            complaint["version"],
        ),
        200,
    )
    assert (
        expect(mutate(citizen, base + "/service-requests", body, key=key), 201)["id"] == case["id"]
    )
    assert (
        expect(citizen.request("GET", base + "/complaints/" + complaint["id"]), 200)["status"]
        == "UNDER_REVIEW"
    )


def test_service_cursors_are_bound_to_owner_parent_filters_and_audience(env):
    citizen = resident(env)
    sup, _ = provision(env, "SUPERVISOR", "supervisor@example.invalid")
    base = f"/api/v1/orgs/{env['org']['id']}"
    first, second = create(citizen, base), create(citizen, base)
    path = base + "/service-requests/" + first["id"]
    triage(sup, path, first, "UNDER_REVIEW")
    page = expect(citizen.request("GET", path + "/timeline?limit=1"), 200)
    cursor = page["next_cursor"]
    assert cursor
    expect(citizen.request("GET", path + "/timeline?limit=1&cursor=" + cursor), 200)
    expect(sup.request("GET", path + "/timeline?audience=INTERNAL&limit=1&cursor=" + cursor), 422)
    expect(
        citizen.request(
            "GET", base + "/service-requests/" + second["id"] + "/timeline?limit=1&cursor=" + cursor
        ),
        422,
    )
    cursor = expect(citizen.request("GET", base + "/service-requests?limit=1"), 200)["next_cursor"]
    expect(
        citizen.request(
            "GET", base + "/service-requests?limit=1&category=LOW_PRESSURE&cursor=" + cursor
        ),
        422,
    )
    expect(citizen.request("GET", base + "/service-requests?from=invalid&to=invalid"), 422)


def test_findings_reassignment_revokes_read_write_and_receipt_replay(env):
    f = setup(env)
    item = incident(env, f)
    ip = f["base"] + "/incidents/" + item["id"]
    item = transition(f["supervisor"], ip, item, "UNDER_REVIEW")
    transition(f["supervisor"], ip, item, "INVESTIGATION_REQUIRED")
    work = expect(
        mutate(
            f["supervisor"],
            f["base"] + "/work-orders",
            {
                "incident_id": item["id"],
                "priority": "MEDIUM",
                "instructions": "SYNTHETIC investigation scope",
                "task_purpose": "INVESTIGATION",
            },
        ),
        201,
    )
    wp = f["base"] + "/work-orders/" + work["id"]
    work = expect(
        mutate(
            f["supervisor"],
            wp + "/assignment",
            {
                "assignee_membership_id": f["tech_membership"]["id"],
                "due_at": None,
                "reason": "SYNTHETIC assignment",
            },
            work["version"],
        ),
        201,
    )
    work = transition(f["technician"], wp, work, "ACCEPTED")
    work = transition(f["technician"], wp, work, "IN_PROGRESS")
    key = uuid4()
    body = {
        "operation_id": str(uuid4()),
        "assignment_version": work["assignment_version"],
        "observed_at": datetime.now(UTC).isoformat(),
        "findings": "SYNTHETIC manual inspection findings",
        "no_repair_reason": "SYNTHETIC no repair performed",
        "attachment_ids": [],
        "supersedes_id": None,
    }
    result = expect(mutate(f["technician"], wp + "/findings", body, work["version"], key), 201)
    with env["owner"].begin() as c:
        assert one(
            c,
            "SELECT findings FROM work_investigation_findings WHERE id=:i",
            i=result["resource"]["id"],
        )
    other, member = provision(env, "TECHNICIAN", "replacement@example.invalid", f["admin"])
    work = expect(f["supervisor"].request("GET", wp), 200)
    expect(
        mutate(
            f["supervisor"],
            wp + "/assignment",
            {
                "assignee_membership_id": member["id"],
                "due_at": None,
                "reason": "SYNTHETIC authorized reassignment",
            },
            work["version"],
        ),
        201,
    )
    expect(f["technician"].request("GET", wp + "/findings"), 404)
    expect(mutate(f["technician"], wp + "/findings", body, work["version"], key), 404)
    assert len(expect(other.request("GET", wp + "/findings"), 200)["items"]) == 1
