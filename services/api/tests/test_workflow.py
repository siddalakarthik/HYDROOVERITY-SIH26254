"""Synthetic complaint -> manual repair -> independent NOT_VERIFIABLE workflow."""

from uuid import uuid4

import pytest
from conftest import Client
from helpers import expect, login, mutate, provision, register

from hydro.db import execute, one
from hydro.main import create_app


def setup(env):
    admin = login(env, "admin-a@example.invalid")
    engineer, _ = provision(env, "ENGINEER", "engineer@example.invalid", admin)
    supervisor, _ = provision(env, "SUPERVISOR", "supervisor@example.invalid", admin)
    technician, tech_membership = provision(env, "TECHNICIAN", "technician@example.invalid", admin)
    citizen = register(env, "citizen@example.invalid")
    login(env, "citizen@example.invalid", citizen)
    base = f"/api/v1/orgs/{env['org']['id']}"
    zone = expect(
        mutate(
            engineer,
            base + "/zones",
            {
                "name": "SYNTHETIC service area",
                "demand_boundary_version": "synthetic-v1",
                "demand_accounting": {
                    "outflow_includes_customer_demand": True,
                    "storage_observed": False,
                    "notes": "Synthetic integration fixture; no instrument readings",
                },
            },
        ),
        201,
    )
    return {
        "base": base,
        "admin": admin,
        "engineer": engineer,
        "supervisor": supervisor,
        "technician": technician,
        "tech_membership": tech_membership,
        "citizen": citizen,
        "zone": zone,
    }


def complaint_body():
    return {
        "category": "VISIBLE_LEAK",
        "description": "SYNTHETIC report for backend integration testing",
        "coarse_area": "SYNTHETIC locality only",
        "photo_consent": False,
        "attachment_ids": [],
    }


def incident(env, flow):
    return expect(
        mutate(
            flow["supervisor"],
            flow["base"] + "/incidents",
            {
                "zone_id": flow["zone"]["id"],
                "title": "SYNTHETIC concern requiring investigation",
                "severity": "MEDIUM",
                "assessment_ids": [],
                "workspace_mode": "OPERATIONAL",
                "simulation_run_id": None,
            },
        ),
        201,
    )


def transition(client, path, resource, target):
    return expect(
        mutate(
            client,
            path + "/transitions",
            {"target": target, "reason": "SYNTHETIC authorized transition for integration test"},
            version=resource["version"],
        ),
        200,
    )


def assigned_work(env, flow):
    item = incident(env, flow)
    path = flow["base"] + "/incidents/" + item["id"]
    item = transition(flow["supervisor"], path, item, "UNDER_REVIEW")
    item = transition(flow["supervisor"], path, item, "ACCEPTED")
    work = expect(
        mutate(
            flow["supervisor"],
            flow["base"] + "/work-orders",
            {
                "incident_id": item["id"],
                "priority": "MEDIUM",
                "instructions": "SYNTHETIC manual investigation; no hardware operation is authorized",
            },
        ),
        201,
    )
    work = expect(
        mutate(
            flow["supervisor"],
            flow["base"] + "/work-orders/" + work["id"] + "/assignment",
            {
                "assignee_membership_id": flow["tech_membership"]["id"],
                "due_at": None,
                "reason": "SYNTHETIC technician assignment",
            },
            version=work["version"],
        ),
        201,
    )
    return item, work


def test_complete_persistent_operational_workflow(env, tmp_path):
    flow = setup(env)
    base = flow["base"]
    citizen = flow["citizen"]
    sup = flow["supervisor"]
    tech = flow["technician"]
    key = uuid4()
    b = complaint_body()
    complaint = expect(mutate(citizen, base + "/complaints", b, key=key), 201)
    assert expect(mutate(citizen, base + "/complaints", b, key=key), 201)["id"] == complaint["id"]
    expect(
        mutate(
            citizen,
            base + "/complaints",
            {**b, "description": "Different SYNTHETIC report payload"},
            key=key,
        ),
        409,
    )
    cp = base + "/complaints/" + complaint["id"]
    expect(
        mutate(
            citizen,
            cp + "/follow-ups",
            {
                "description": "SYNTHETIC additional information",
                "photo_consent": False,
                "attachment_ids": [],
            },
            version=complaint["version"],
        ),
        200,
    )
    complaint = expect(citizen.request("GET", cp), 200)
    incident_row = incident(env, flow)
    ip = base + "/incidents/" + incident_row["id"]
    expect(
        mutate(
            sup,
            cp + "/review",
            {
                "public_status": "UNDER_REVIEW",
                "public_message": "SYNTHETIC report reviewed for a manual visit",
                "incident_id": incident_row["id"],
                "internal_reason": "SYNTHETIC private review reason never exposed to citizen",
            },
            version=complaint["version"],
        ),
        200,
    )
    incident_row = transition(sup, ip, incident_row, "UNDER_REVIEW")
    incident_row = transition(sup, ip, incident_row, "ACCEPTED")
    work = expect(
        mutate(
            sup,
            base + "/work-orders",
            {
                "incident_id": incident_row["id"],
                "priority": "MEDIUM",
                "instructions": "SYNTHETIC authorized manual investigation only",
            },
        ),
        201,
    )
    wp = base + "/work-orders/" + work["id"]
    work = expect(
        mutate(
            sup,
            wp + "/assignment",
            {
                "assignee_membership_id": flow["tech_membership"]["id"],
                "due_at": None,
                "reason": "SYNTHETIC visit assignment",
            },
            version=work["version"],
        ),
        201,
    )
    incident_row = transition(sup, ip, incident_row, "IN_PROGRESS")
    brief = expect(tech.request("GET", wp + "/brief"), 200)
    assert brief["work_order"]["id"] == work["id"]
    assert "citizen@example.invalid" not in str(brief)
    work = transition(tech, wp, work, "ACCEPTED")
    work = transition(tech, wp, work, "IN_PROGRESS")
    from hydro.security import now

    action = {
        "operation_id": str(uuid4()),
        "observed_at": now().isoformat(),
        "base_version": work["version"],
        "assignment_version": work["assignment_version"],
        "note": "SYNTHETIC investigation note; no physical test was performed",
        "materials": [],
        "attachment_ids": [],
    }
    action_key = uuid4()
    a = expect(mutate(tech, wp + "/actions", action, key=action_key), 200)
    assert expect(mutate(tech, wp + "/actions", action, key=action_key), 200)["id"] == a["id"]
    work = expect(tech.request("GET", wp), 200)
    repair = expect(
        mutate(
            tech,
            wp + "/repairs",
            {
                "performed_at": now().isoformat(),
                "description": "SYNTHETIC reported repair for workflow tests only; no device was built or repaired",
                "materials": [{"name": "SYNTHETIC fixture item", "quantity": 1, "unit": "item"}],
                "attachment_ids": [],
            },
            version=work["version"],
        ),
        201,
    )
    assert repair["environment"] == "MANUAL"
    assert expect(tech.request("GET", wp + "/repairs"), 200)["items"][0]["id"] == repair["id"]
    work = expect(tech.request("GET", wp), 200)
    work = transition(tech, wp, work, "SUBMITTED_FOR_REVIEW")
    work = transition(sup, wp, work, "COMPLETED")
    assert expect(sup.request("GET", ip), 200)["status"] == "IN_PROGRESS"
    incident_row = transition(sup, ip, incident_row, "VERIFICATION_PENDING")
    comparability = {
        "supply_state_comparable": False,
        "pressure_demand_storage_comparable": False,
        "calibration_quality_freshness_comparable": False,
        "unit_windows_comparable": False,
        "limitations": "SYNTHETIC manual receipts only; no comparable calibrated observations exist",
    }
    vb = {
        "outcome": "NOT_VERIFIABLE",
        "before_evidence_record_ids": [],
        "after_evidence_record_ids": [],
        "comparability": comparability,
        "reason": "SYNTHETIC independent review cannot establish measurement comparability",
    }
    vp = base + "/repairs/" + repair["id"] + "/verifications"
    verification = expect(mutate(sup, vp, vb, version=1), 201)
    assert verification["outcome"] == "NOT_VERIFIABLE"
    assert expect(tech.request("GET", vp), 200)["items"][0]["id"] == verification["id"]
    expect(mutate(sup, vp, {**vb, "outcome": "VERIFICATION_PASSED"}, version=1), 422)
    expect(mutate(sup, vp, {**vb, "outcome": "VERIFICATION_FAILED"}, version=1), 422)
    incident_row = transition(sup, ip, incident_row, "NOT_VERIFIABLE")
    second = expect(
        mutate(
            sup,
            vp,
            {**vb, "reason": "SYNTHETIC second independent review retaining the original outcome"},
            version=1,
        ),
        201,
    )
    assert second["id"] != verification["id"]
    with env["owner"].begin() as c:
        assert (
            str(
                one(
                    c, "SELECT supersedes_id FROM verification_records WHERE id=:i", i=second["id"]
                )["supersedes_id"]
            )
            == verification["id"]
        )
    current = expect(citizen.request("GET", cp), 200)
    assert "incident_id" not in current and "private review reason" not in str(current)
    other = register(env, "other-citizen@example.invalid")
    login(env, "other-citizen@example.invalid", other)
    expect(other.request("GET", cp), 404)
    expect(other.request("GET", ip), 403)
    b_admin = login(env, "admin-b@example.invalid")
    expect(b_admin.request("GET", ip), 404)
    expect(
        mutate(
            b_admin,
            ip + "/transitions",
            {"target": "RESOLVED", "reason": "SYNTHETIC unauthorized transition"},
            version=incident_row["version"],
        ),
        404,
    )
    # Recreate the actual application against the same persistent database.
    restarted = None
    if env.get("restart_factory"):
        restart_client = env["restart_factory"](sup)
    else:
        restarted = create_app(env["settings"])
        restart_client = Client(restarted)
    try:
        restart_client.http.cookies.update(sup.http.cookies)
        assert expect(restart_client.request("GET", ip), 200)["status"] == "NOT_VERIFIABLE"
        timeline = expect(restart_client.request("GET", ip + "/timeline?limit=2"), 200)
        assert len(timeline["items"]) == 2 and timeline["next_cursor"]
        assert expect(
            restart_client.request(
                "GET", ip + "/timeline?limit=2&cursor=" + timeline["next_cursor"]
            ),
            200,
        )["items"]
    finally:
        restart_client.close()
        if restarted:
            restarted.state.engine.dispose()
    evidence = {
        "fixture_provenance": "SYNTHETIC_INTEGRATION_ONLY",
        "hardware_experiments": 0,
        "physical_repair_performed": False,
        "scenario": "complaint_to_independent_manual_verification",
        "result": "NOT_VERIFIABLE",
        "complaint_receipts": 1,
        "audit_and_history_persisted": True,
        "restart_retrieval": "PASS",
    }
    (tmp_path / "m03-workflow-evidence.json").write_text(
        __import__("json").dumps(evidence, indent=2)
    )


def test_reassignment_denies_former_technician_and_receipt_replay(env):
    f = setup(env)
    item, work = assigned_work(env, f)
    wp = f["base"] + "/work-orders/" + work["id"]
    tech = f["technician"]
    work = transition(tech, wp, work, "ACCEPTED")
    work = transition(tech, wp, work, "IN_PROGRESS")
    from hydro.security import now

    body = {
        "operation_id": str(uuid4()),
        "observed_at": now().isoformat(),
        "base_version": work["version"],
        "assignment_version": work["assignment_version"],
        "note": "SYNTHETIC action before reassignment",
        "materials": [],
        "attachment_ids": [],
    }
    key = uuid4()
    expect(mutate(tech, wp + "/actions", body, key=key), 200)
    other, member = provision(env, "TECHNICIAN", "replacement@example.invalid", f["admin"])
    work = expect(f["supervisor"].request("GET", wp), 200)
    new = expect(
        mutate(
            f["supervisor"],
            wp + "/assignment",
            {
                "assignee_membership_id": member["id"],
                "due_at": None,
                "reason": "SYNTHETIC reassignment while old worker is offline",
            },
            version=work["version"],
        ),
        201,
    )
    assert new["assignment_version"] == work["assignment_version"] + 1
    expect(tech.request("GET", wp), 404)
    expect(mutate(tech, wp + "/actions", body, key=key), 404)
    assert not expect(tech.request("GET", f["base"] + "/work-orders"), 200)["items"]
    expect(other.request("GET", wp + "/brief"), 200)


def test_workflow_invalid_transitions_nested_tenant_ids_and_photos_disabled(env):
    f = setup(env)
    row = incident(env, f)
    ip = f["base"] + "/incidents/" + row["id"]
    expect(
        mutate(
            f["supervisor"],
            ip + "/transitions",
            {"target": "RESOLVED", "reason": "SYNTHETIC invalid transition"},
            version=row["version"],
        ),
        409,
    )
    expect(
        mutate(
            f["supervisor"],
            ip + "/transitions",
            {"target": "UNDER_REVIEW", "reason": "SYNTHETIC stale transition"},
            version=999,
        ),
        412,
    )
    expect(
        mutate(
            f["supervisor"],
            ip + "/transitions",
            {"target": "UNDER_REVIEW", "reason": "SYNTHETIC missing version"},
        ),
        428,
    )
    expect(
        mutate(
            f["citizen"],
            f["base"] + "/complaints",
            {**complaint_body(), "photo_consent": True, "attachment_ids": [str(uuid4())]},
        ),
        422,
    )

    expect(
        mutate(
            f["supervisor"],
            f["base"] + "/work-orders",
            {
                "incident_id": str(uuid4()),
                "priority": "LOW",
                "instructions": "SYNTHETIC invalid nested parent",
            },
        ),
        404,
    )
    item, work = assigned_work(env, f)
    wp = f["base"] + "/work-orders/" + work["id"]
    expect(
        mutate(
            f["technician"],
            wp + "/transitions",
            {"target": "COMPLETED", "reason": "SYNTHETIC worker cannot complete own task"},
            version=work["version"],
        ),
        409,
    )
    with env["owner"].begin() as c:
        suspended = one(
            c,
            "SELECT id FROM organization_memberships WHERE organization_id=:o AND id=:m",
            o=env["org"]["id"],
            m=f["tech_membership"]["id"],
        )
        execute(
            c,
            "UPDATE organization_memberships SET status='SUSPENDED' WHERE id=:i",
            i=suspended["id"],
        )
    expect(
        mutate(
            f["supervisor"],
            wp + "/assignment",
            {
                "assignee_membership_id": f["tech_membership"]["id"],
                "due_at": None,
                "reason": "SYNTHETIC inactive worker must be rejected",
            },
            version=work["version"],
        ),
        422,
    )


def test_complete_followup_and_unlinked_private_review_are_retained(env, monkeypatch):
    f = setup(env)
    base = f["base"]
    citizen = f["citizen"]
    sup = f["supervisor"]
    row = expect(mutate(citizen, base + "/complaints", complaint_body()), 201)
    path = base + "/complaints/" + row["id"]
    text = "SYNTHETIC full resident follow-up " + ("x" * 1900)
    expect(
        mutate(
            citizen,
            path + "/follow-ups",
            {"description": text, "photo_consent": False, "attachment_ids": []},
            version=row["version"],
        ),
        200,
    )
    current = expect(citizen.request("GET", path), 200)
    assert current["public_updates"][0]["message"] == text
    private = "SYNTHETIC private triage justification retained without an incident"
    receipt = expect(
        mutate(
            sup,
            path + "/review",
            {
                "public_status": "UNDER_REVIEW",
                "public_message": "SYNTHETIC public review update",
                "incident_id": None,
                "internal_reason": private,
            },
            version=current["version"],
        ),
        200,
    )
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT internal_reason FROM complaint_status_events WHERE id=:i",
                i=receipt["id"],
            )["internal_reason"]
            == private
        )
    assert private not in str(expect(citizen.request("GET", path), 200))
    import os

    from alembic import command
    from alembic.config import Config

    from hydro.config import ROOT

    monkeypatch.setenv("HYDRO_MIGRATION_URL", os.environ["HYDRO_TEST_OWNER_URL"])
    with pytest.raises(RuntimeError, match="Forward-only"):
        command.downgrade(Config(str(ROOT / "services/api/alembic.ini")), "m03_003")
    with env["owner"].begin() as c:
        assert one(c, "SELECT version_num FROM alembic_version")["version_num"] == "m03_004"
