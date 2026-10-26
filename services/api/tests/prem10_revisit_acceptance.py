"""Synthetic manual revisit guards; no measured repair outcome is asserted."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from helpers import expect, login, mutate
from test_workflow import assigned_work, setup, transition

from hydro.db import execute, one, query
from hydro.security import now


def verification_body():
    return {
        "outcome": "NOT_VERIFIABLE",
        "before_evidence_record_ids": [],
        "after_evidence_record_ids": [],
        "comparability": {
            "supply_state_comparable": False,
            "pressure_demand_storage_comparable": False,
            "calibration_quality_freshness_comparable": False,
            "unit_windows_comparable": False,
            "limitations": "SYNTHETIC manual receipt only; no measured evidence supplied",
        },
        "reason": "SYNTHETIC independent review cannot establish measured verification",
    }


def repair(f, work, performed_at=None):
    path = f["base"] + "/work-orders/" + work["id"]
    return expect(
        mutate(
            f["technician"],
            path + "/repairs",
            {
                "performed_at": performed_at or now().isoformat(),
                "description": "SYNTHETIC reported revisit work; no actual physical repair",
                "materials": [],
                "attachment_ids": [],
            },
            work["version"],
        ),
        201,
    )


def review(f, receipt):
    return expect(
        mutate(
            f["supervisor"],
            f["base"] + "/repairs/" + receipt["id"] + "/verifications",
            verification_body(),
            1,
        ),
        201,
    )


def first_cycle(env, completed=True):
    f = setup(env)
    incident, work = assigned_work(env, f)
    ip = f["base"] + "/incidents/" + incident["id"]
    wp = f["base"] + "/work-orders/" + work["id"]
    incident = transition(f["supervisor"], ip, incident, "IN_PROGRESS")
    work = transition(f["technician"], wp, work, "ACCEPTED")
    work = transition(f["technician"], wp, work, "IN_PROGRESS")
    receipt = repair(f, work)
    work = expect(f["technician"].request("GET", wp), 200)
    work = transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
    if completed:
        work = transition(f["supervisor"], wp, work, "COMPLETED")
    incident = transition(f["supervisor"], ip, incident, "VERIFICATION_PENDING")
    verification = review(f, receipt)
    incident = transition(f["supervisor"], ip, incident, "NOT_VERIFIABLE")
    return f, incident, work, receipt, verification


def reconsider(f, incident):
    path = f["base"] + "/incidents/" + incident["id"]
    incident = transition(f["supervisor"], path, incident, "UNDER_REVIEW")
    return transition(f["supervisor"], path, incident, "ACCEPTED")


def deny_transition(f, incident, target, code):
    response = mutate(
        f["supervisor"],
        f["base"] + "/incidents/" + incident["id"] + "/transitions",
        {
            "target": target,
            "reason": "SYNTHETIC attempt to reuse prior-cycle history",
        },
        incident["version"],
    )
    assert expect(response, 409)["error"]["code"] == code


def new_work(f, incident):
    work = expect(
        mutate(
            f["supervisor"],
            f["base"] + "/work-orders",
            {
                "incident_id": incident["id"],
                "priority": "MEDIUM",
                "instructions": "SYNTHETIC explicitly authorized revisit with fresh manual receipt",
            },
        ),
        201,
    )
    return expect(
        mutate(
            f["supervisor"],
            f["base"] + "/work-orders/" + work["id"] + "/assignment",
            {
                "assignee_membership_id": f["tech_membership"]["id"],
                "due_at": None,
                "reason": "SYNTHETIC new revisit assignment",
            },
            work["version"],
        ),
        201,
    )


def test_reconsideration_requires_current_work_receipt_and_review(env):
    f, incident, old_work, old_repair, old_review = first_cycle(env)
    with env["owner"].begin() as c:
        preserved = {
            table: query(c, f"SELECT * FROM {table} ORDER BY id")
            for table in ("repair_records", "verification_records", "work_order_actions")
        }
    incident = reconsider(f, incident)
    deny_transition(f, incident, "IN_PROGRESS", "WORK_REQUIRED")
    work = new_work(f, incident)
    ip = f["base"] + "/incidents/" + incident["id"]
    wp = f["base"] + "/work-orders/" + work["id"]
    incident = transition(f["supervisor"], ip, incident, "IN_PROGRESS")
    deny_transition(f, incident, "VERIFICATION_PENDING", "REPAIR_REQUIRED")
    work = transition(f["technician"], wp, work, "ACCEPTED")
    work = transition(f["technician"], wp, work, "IN_PROGRESS")
    fresh = repair(f, work)
    work = expect(f["technician"].request("GET", wp), 200)
    work = transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
    incident = transition(f["supervisor"], ip, incident, "VERIFICATION_PENDING")
    # Even a newly authored review of an old repair cannot finish this cycle.
    review(f, old_repair)
    deny_transition(f, incident, "NOT_VERIFIABLE", "VERIFICATION_REQUIRED")
    review(f, fresh)
    incident = transition(f["supervisor"], ip, incident, "NOT_VERIFIABLE")
    assert incident["status"] == "NOT_VERIFIABLE"
    with env["owner"].begin() as c:
        for table, rows in preserved.items():
            current = query(c, f"SELECT * FROM {table} ORDER BY id")
            assert all(row in current for row in rows)
        assert (
            one(c, "SELECT status FROM work_orders WHERE id=:i", i=old_work["id"])["status"]
            == "COMPLETED"
        )
        assert (
            one(c, "SELECT outcome FROM verification_records WHERE id=:i", i=old_review["id"])[
                "outcome"
            ]
            == "NOT_VERIFIABLE"
        )


def test_unfinished_work_can_be_explicitly_resumed_but_needs_fresh_receipt(env):
    f, incident, work, old_repair, _ = first_cycle(env, completed=False)
    incident = reconsider(f, incident)
    deny_transition(f, incident, "IN_PROGRESS", "WORK_REQUIRED")
    wp = f["base"] + "/work-orders/" + work["id"]
    ip = f["base"] + "/incidents/" + incident["id"]
    work = transition(f["supervisor"], wp, work, "IN_PROGRESS")
    incident = transition(f["supervisor"], ip, incident, "IN_PROGRESS")
    # Existing work submission currently accepts old receipts. Incident guard must not.
    work = transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
    deny_transition(f, incident, "VERIFICATION_PENDING", "REPAIR_REQUIRED")
    work = transition(f["supervisor"], wp, work, "IN_PROGRESS")
    repair(f, work, performed_at=old_repair["performed_at"])
    work = expect(f["technician"].request("GET", wp), 200)
    work = transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
    deny_transition(f, incident, "VERIFICATION_PENDING", "REPAIR_REQUIRED")
    work = transition(f["supervisor"], wp, work, "IN_PROGRESS")
    fresh = repair(f, work)
    work = expect(f["technician"].request("GET", wp), 200)
    transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
    incident = transition(f["supervisor"], ip, incident, "VERIFICATION_PENDING")
    review(f, fresh)
    transition(f["supervisor"], ip, incident, "NOT_VERIFIABLE")


@pytest.mark.parametrize("prior", ["RESOLVED", "VERIFICATION_PENDING"])
def test_reopened_history_boundary_without_claiming_a_measured_outcome(env, prior):
    f, incident, _, _, _ = first_cycle(env)
    # A narrowly injected historical state exercises the otherwise gated edge.
    # No PASSED/FAILED measurement or verification row is fabricated.
    with env["owner"].begin() as c:
        execute(
            c,
            "UPDATE incidents SET status='REOPENED',version=version+1 WHERE id=:i",
            i=incident["id"],
        )
        execute(
            c,
            "INSERT INTO incident_events(organization_id,incident_id,actor_id,event_type,from_status,to_status,reason,operation_id,occurred_at) VALUES(:o,:i,NULL,'TRANSITION',:prior,'REOPENED','SYNTHETIC historical lifecycle fixture, not a measured outcome',:key,now())",
            o=env["org"]["id"],
            i=incident["id"],
            prior=prior,
            key=uuid4(),
        )
    ip = f["base"] + "/incidents/" + incident["id"]
    incident = expect(f["supervisor"].request("GET", ip), 200)
    deny_transition(f, incident, "IN_PROGRESS", "WORK_REQUIRED")
    new_work(f, incident)
    transition(f["supervisor"], ip, incident, "IN_PROGRESS")


def test_reconsideration_replay_and_stale_version(env):
    f, incident, _, _, _ = first_cycle(env, completed=False)
    path = f["base"] + "/incidents/" + incident["id"] + "/transitions"
    key = uuid4()
    body = {"target": "UNDER_REVIEW", "reason": "SYNTHETIC justified reconsideration"}
    current = expect(mutate(f["supervisor"], path, body, incident["version"], key), 200)
    assert expect(mutate(f["supervisor"], path, body, incident["version"], key), 200) == current
    expect(mutate(f["supervisor"], path, body, incident["version"]), 412)
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM incident_events WHERE incident_id=:i AND from_status='NOT_VERIFIABLE' AND to_status='UNDER_REVIEW'",
                i=incident["id"],
            )["n"]
            == 1
        )
    ip = f["base"] + "/incidents/" + incident["id"]
    current = transition(f["supervisor"], ip, current, "ACCEPTED")
    deny_transition(f, current, "IN_PROGRESS", "WORK_REQUIRED")


def test_revisit_resumption_and_cancellation_are_version_serialized(env):
    f, incident, work, _, _ = first_cycle(env, completed=False)
    incident = reconsider(f, incident)
    other = login(env, "supervisor@example.invalid")
    path = f["base"] + "/work-orders/" + work["id"] + "/transitions"
    before = expect(f["supervisor"].request("GET", path.rsplit("/", 1)[0]), 200)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda pair: mutate(
                    pair[0],
                    path,
                    {"target": pair[1], "reason": "SYNTHETIC concurrent revisit decision"},
                    before["version"],
                ),
                [(f["supervisor"], "IN_PROGRESS"), (other, "CANCELLED")],
            )
        )
    assert sorted(r.status_code for r in responses) == [200, 412]
    current = expect(f["supervisor"].request("GET", path.rsplit("/", 1)[0]), 200)
    assert current["version"] == before["version"] + 1
    if current["status"] == "CANCELLED":
        deny_transition(f, incident, "IN_PROGRESS", "WORK_REQUIRED")
    else:
        ip = f["base"] + "/incidents/" + incident["id"]
        transition(f["supervisor"], ip, incident, "IN_PROGRESS")
    expect(
        mutate(
            f["citizen"],
            path,
            {"target": "IN_PROGRESS", "reason": "SYNTHETIC unauthorized revisit"},
            current["version"],
        ),
        403,
    )


def test_repeated_reconsideration_requires_a_new_receipt_each_cycle(env):
    f, incident, work, original, _ = first_cycle(env, completed=False)
    receipts = [original["id"]]
    ip = f["base"] + "/incidents/" + incident["id"]
    wp = f["base"] + "/work-orders/" + work["id"]
    for _ in range(2):
        # Each later visit uses new authenticated sessions. The test helper
        # bootstraps CSRF on every write; keep its synthetic per-client burst
        # below the real bootstrap rate limit rather than changing that limit.
        f["supervisor"] = login(env, "supervisor@example.invalid")
        f["technician"] = login(env, "technician@example.invalid")
        incident = reconsider(f, incident)
        deny_transition(f, incident, "IN_PROGRESS", "WORK_REQUIRED")
        work = transition(f["supervisor"], wp, work, "IN_PROGRESS")
        incident = transition(f["supervisor"], ip, incident, "IN_PROGRESS")
        work = transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
        deny_transition(f, incident, "VERIFICATION_PENDING", "REPAIR_REQUIRED")
        work = transition(f["supervisor"], wp, work, "IN_PROGRESS")
        fresh = repair(f, work)
        receipts.append(fresh["id"])
        work = expect(f["technician"].request("GET", wp), 200)
        work = transition(f["technician"], wp, work, "SUBMITTED_FOR_REVIEW")
        incident = transition(f["supervisor"], ip, incident, "VERIFICATION_PENDING")
        review(f, fresh)
        incident = transition(f["supervisor"], ip, incident, "NOT_VERIFIABLE")
    assert len(set(receipts)) == 3
    with env["owner"].begin() as c:
        assert (
            one(c, "SELECT count(*) AS n FROM repair_records WHERE work_order_id=:w", w=work["id"])[
                "n"
            ]
            == 3
        )
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM incident_events WHERE incident_id=:i AND from_status='NOT_VERIFIABLE' AND to_status='UNDER_REVIEW'",
                i=incident["id"],
            )["n"]
            == 2
        )
