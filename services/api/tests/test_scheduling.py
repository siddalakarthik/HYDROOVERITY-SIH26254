"""M07-B acceptance uses only isolated synthetic PostgreSQL fixtures."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from helpers import expect, login, mutate, provision

from hydro.db import one


def test_global_enrollment_is_exclusive_under_concurrency(env):
    from concurrent.futures import ThreadPoolExecutor

    from helpers import token

    admin, sup, tech, base, enroll = foundation(env)
    otheradmin = login(env, "admin-b@example.invalid")
    otherbase = f"/api/v1/orgs/{env['other']['id']}"
    expect(
        mutate(
            otheradmin,
            otherbase + "/invitations",
            dict(email="dispatch-technician@example.invalid", role="TECHNICIAN"),
        ),
        200,
    )
    expect(
        tech.request(
            "POST",
            "/api/v1/auth/invitation-accept",
            json={"token": token(env, "INVITATION", "dispatch-technician@example.invalid")},
        ),
        200,
    )
    with env["owner"].begin() as c:
        othermember = one(
            c,
            "SELECT * FROM organization_memberships WHERE organization_id=:o AND user_id=(SELECT user_id FROM organization_memberships WHERE id=:m)",
            o=env["other"]["id"],
            m=enroll["membership_id"],
        )
    otherbody = {
        **enroll,
        "membership_id": str(othermember["id"]),
        "expected_membership_version": othermember["version"],
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(mutate, admin, base + "/technicians", enroll),
            pool.submit(mutate, otheradmin, otherbase + "/dispatch/technicians", otherbody),
        ]
        results = [r.result() for r in futures]
    assert sorted(r.status_code for r in results) == [201, 409]
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM dispatch_calendar_subjects")["n"] == 1


def test_postgres_exclusion_denies_concurrent_runtime_allocations(env):
    from concurrent.futures import ThreadPoolExecutor

    from sqlalchemy.exc import IntegrityError

    from hydro.db import context, execute

    admin, sup, tech, base, enroll = foundation(env)
    expect(mutate(admin, base + "/technicians", enroll), 201)
    with env["owner"].begin() as c:
        profile = one(c, "SELECT * FROM dispatch_technician_profiles")
        actor = one(
            c,
            "SELECT user_id FROM organization_memberships WHERE id IN (SELECT membership_id FROM role_assignments a JOIN roles r ON r.id=a.role_id WHERE r.code='SUPERVISOR' AND a.revoked_at IS NULL)",
        )["user_id"]
    start = datetime.now(UTC) + timedelta(days=1)

    def allocate(_):
        try:
            with env["app"].state.engine.begin() as c:
                context(c, actor, env["org"]["id"])
                execute(
                    c,
                    "INSERT INTO dispatch_allocations(organization_id,profile_id,subject_id,kind,occupied_range,reason) VALUES(:o,:p,:subject,'UNAVAILABLE',tstzrange(:s,:e,'[)'),'SYNTHETIC concurrent allocation')",
                    o=env["org"]["id"],
                    p=profile["id"],
                    subject=profile["subject_id"],
                    s=start,
                    e=start + timedelta(hours=1),
                )
            return "COMMITTED"
        except IntegrityError:
            return "EXCLUDED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(allocate, range(2))) == ["COMMITTED", "EXCLUDED"]


def test_revoked_technician_does_not_erase_commitments(env):
    f = booking_fixture(env)
    row = request_visit(f)
    visit = confirm(f, row)["appointment"]
    base = f["base"]
    with env["owner"].begin() as c:
        m = one(
            c, "SELECT * FROM organization_memberships WHERE id=:m", m=f["tech_membership"]["id"]
        )
    expect(
        mutate(
            f["admin"],
            base + "/memberships/" + str(m["id"]) + "/status",
            dict(status="SUSPENDED", reason="SYNTHETIC revocation"),
            m["version"],
        ),
        201,
    )
    expect(f["technician"].request("GET", base + "/appointments/" + visit["id"]), 401)
    safe = expect(f["supervisor"].request("GET", base + "/appointments/" + visit["id"]), 200)
    assert safe["status"] == "CONFIRMED" and safe["dispatch_health"] == "REVIEW_REQUIRED"
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM dispatch_allocations WHERE active AND kind='APPOINTMENT'",
            )["n"]
            == 1
        )


def policy_body():
    return dict(
        booking_enabled=True,
        horizon_days=14,
        minimum_lead_minutes=0,
        free_cancel_before_minutes=0,
        max_arrival_width_minutes=60,
        request_expiry_hours=24,
        offer_expiry_hours=8,
        max_daily_minutes=480,
        minimum_before_buffer_minutes=10,
        minimum_after_buffer_minutes=10,
        allowed_duration_minutes=[30],
        reason="SYNTHETIC acceptance policy; never a real utility default",
    )


def test_existing_relationship_can_receive_audited_eligibility_review(env):
    from test_service_foundation import create, triage
    from test_workflow import incident, setup, transition

    f = setup(env)
    sup = f["supervisor"]
    base = f["base"]
    case = create(f["citizen"], base)
    path = base + "/service-requests/" + case["id"]
    case = triage(sup, path, case, "UNDER_REVIEW")
    case = triage(sup, path, case, "ACCEPTED")
    i = incident(env, f)
    ip = base + "/incidents/" + i["id"]
    i = transition(sup, ip, i, "UNDER_REVIEW")
    i = transition(sup, ip, i, "ACCEPTED")
    work = expect(
        mutate(
            sup,
            base + "/work-orders",
            dict(incident_id=i["id"], priority="MEDIUM", instructions="Synthetic reviewed task"),
        ),
        201,
    )
    body = dict(
        work_order_id=work["id"],
        expected_work_version=work["version"],
        purpose="REPAIR",
        internal_reason="Synthetic initial linkage",
    )
    original = expect(mutate(sup, path + "/work-order-links", body, case["version"]), 201)
    current = expect(sup.request("GET", path), 200)
    reviewed = expect(
        mutate(
            sup,
            path + "/work-order-links",
            {
                **body,
                "dispatch_service_area_code": "SYNTHETIC_AREA",
                "dispatch_required_skill_codes": ["SYNTHETIC_INSPECTION"],
            },
            current["version"],
        ),
        201,
    )
    assert reviewed["id"] == original["id"] and reviewed["version"] == original["version"] + 1
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM service_work_order_links")["n"] == 1
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM service_request_events WHERE event_kind='DISPATCH_ELIGIBILITY_REVIEWED'",
            )["n"]
            == 1
        )


def test_failed_booking_replacement_rolls_back_and_concurrent_cancel_releases_once(env):
    from concurrent.futures import ThreadPoolExecutor

    f = booking_fixture(env)
    base = f["base"]
    sup = f["supervisor"]
    first = confirm(f, request_visit(f))["appointment"]
    proposed = request_visit(f, 1, first)
    path = base + "/appointment-requests/" + proposed["id"]
    staff = expect(sup.request("GET", path), 200)
    # A real database rejection after old-booking deactivation exercises rollback,
    # including assignment, allocations and audit, in this disposable fixture only.
    with env["owner"].begin() as c:
        c.exec_driver_sql(
            "ALTER TABLE appointments ADD CONSTRAINT synthetic_replacement_rejection CHECK(replaces_id IS NULL) NOT VALID"
        )
    try:
        expect(
            mutate(
                sup,
                path + "/decisions",
                dict(
                    decision="CONFIRM_REQUESTED",
                    expectations=staff["expectations"],
                    public_message="Synthetic replacement confirmation.",
                    internal_reason="Synthetic rollback acceptance",
                ),
                staff["version"],
            ),
            409,
        )
        with env["owner"].begin() as c:
            old = one(c, "SELECT * FROM appointments WHERE id=:i", i=first["id"])
            assert old["status"] == "CONFIRMED" and old["version"] == first["version"]
            assert (
                one(
                    c,
                    "SELECT count(*) AS n FROM dispatch_allocations WHERE appointment_id=:i AND active",
                    i=first["id"],
                )["n"]
                == 1
            )
    finally:
        with env["owner"].begin() as c:
            c.exec_driver_sql(
                "ALTER TABLE appointments DROP CONSTRAINT synthetic_replacement_rejection"
            )
    other = login(env, "supervisor@example.invalid")
    service = expect(sup.request("GET", f["case_path"]), 200)
    work = expect(sup.request("GET", base + "/work-orders/" + f["work"]["id"]), 200)
    body = dict(
        caller_action="SUPERVISOR",
        reason_code="UTILITY",
        public_reason="Synthetic visit cancellation.",
        expected_service_version=service["version"],
        expected_work_version=work["version"],
        expected_assignment_version=work["assignment_version"],
        internal_reason="Synthetic concurrent cancellation",
        disposition="CANCEL",
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: mutate(
                    client,
                    base + "/appointments/" + first["id"] + "/cancellations",
                    body,
                    first["version"],
                ),
                [sup, other],
            )
        )
    assert sorted(r.status_code for r in results) == [200, 412]
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM dispatch_allocations WHERE appointment_id=:i AND active",
                i=first["id"],
            )["n"]
            == 0
        )


def booking_fixture(env, flow=None, policy_overrides=None):
    from test_service_foundation import create, triage
    from test_workflow import incident, setup, transition

    f = flow or setup(env)
    admin, sup, _tech = f["admin"], f["supervisor"], f["technician"]
    base = f["base"]
    dispatch = base + "/dispatch"
    with env["owner"].begin() as c:
        m = one(
            c, "SELECT * FROM organization_memberships WHERE id=:i", i=f["tech_membership"]["id"]
        )
    enrollment = dict(
        membership_id=str(m["id"]),
        expected_membership_version=m["version"],
        skill_codes=["SYNTHETIC_INSPECTION"],
        service_area_codes=["SYNTHETIC_AREA"],
        max_daily_minutes=480,
        exclusive_dispatch_acknowledged=True,
        reason="SYNTHETIC technician enrollment",
    )
    p = expect(mutate(admin, dispatch + "/technicians", enrollment), 201)
    expect(
        mutate(
            admin,
            dispatch + "/policy",
            {**policy_body(), **(policy_overrides or {})},
            1,
            method="PUT",
        ),
        200,
    )
    start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=1)
    shift = dict(
        technician_membership_id=str(m["id"]),
        expected_calendar_version=1,
        interval={
            "start_at": (start - timedelta(hours=1)).isoformat(),
            "end_at": (start + timedelta(hours=7)).isoformat(),
        },
        reason="SYNTHETIC dated shift",
    )
    expect(mutate(sup, dispatch + "/shifts", shift, p["profile_version"]), 201)
    windows = []
    for hours in [0, 2, 4]:
        p = next(
            p
            for p in expect(sup.request("GET", dispatch + "/technicians"), 200)["items"]
            if p["membership_id"] == str(m["id"])
        )
        b = dict(
            technician_membership_id=str(m["id"]),
            expected_calendar_version=p["calendar_version"],
            expected_policy_version=2,
            arrival_start=(start + timedelta(hours=hours)).isoformat(),
            arrival_end=(start + timedelta(hours=hours, minutes=15)).isoformat(),
            expected_service_minutes=30,
            before_buffer_minutes=10,
            after_buffer_minutes=10,
            category_codes=["VISIBLE_LEAK"],
            service_area_codes=["SYNTHETIC_AREA"],
            reason="SYNTHETIC published visit window",
        )
        windows.append(
            expect(mutate(sup, dispatch + "/appointment-windows", b, p["profile_version"]), 201)
        )
    case = create(f["citizen"], base)
    cp = base + "/service-requests/" + case["id"]
    case = triage(sup, cp, case, "UNDER_REVIEW")
    case = triage(sup, cp, case, "ACCEPTED")
    item = incident(env, f)
    ip = base + "/incidents/" + item["id"]
    item = transition(sup, ip, item, "UNDER_REVIEW")
    item = transition(sup, ip, item, "ACCEPTED")
    work = expect(
        mutate(
            sup,
            base + "/work-orders",
            dict(
                incident_id=item["id"],
                priority="MEDIUM",
                instructions="SYNTHETIC investigation task",
                task_purpose="INVESTIGATION",
            ),
        ),
        201,
    )
    expect(
        mutate(
            sup,
            cp + "/work-order-links",
            dict(
                work_order_id=work["id"],
                expected_work_version=work["version"],
                purpose="INVESTIGATION",
                internal_reason="SYNTHETIC reviewed eligibility",
                dispatch_service_area_code="SYNTHETIC_AREA",
                dispatch_required_skill_codes=["SYNTHETIC_INSPECTION"],
            ),
            case["version"],
        ),
        201,
    )
    f.update(case_path=cp, windows=windows, work=work, start=start)
    return f


def request_visit(f, index=0, old=None):
    case = expect(f["citizen"].request("GET", f["case_path"]), 200)
    w = f["windows"][index]
    b = dict(
        kind="RESCHEDULE" if old else "INITIAL",
        window_id=w["id"],
        expected_window_version=w["version"],
        expected_preferences_version=None,
        replaces_appointment_id=old["id"] if old else None,
        expected_appointment_version=old["version"] if old else None,
        message="SYNTHETIC visit request",
    )
    return expect(
        mutate(f["citizen"], f["case_path"] + "/appointment-requests", b, case["version"]), 201
    )


def confirm(f, row):
    path = f["base"] + "/appointment-requests/" + row["id"]
    staff = expect(f["supervisor"].request("GET", path), 200)
    return expect(
        mutate(
            f["supervisor"],
            path + "/decisions",
            dict(
                decision="CONFIRM_REQUESTED",
                expectations=staff["expectations"],
                public_message="Your requested visit is confirmed.",
                internal_reason="SYNTHETIC reviewed confirmation",
            ),
            staff["version"],
        ),
        200,
    )


def test_booking_reschedule_cancellation_and_role_projections(env):
    f = booking_fixture(env)
    base = f["base"]
    f["supervisor"]
    citizen = f["citizen"]
    published = expect(
        f["supervisor"].request(
            "GET", base + "/dispatch/appointment-windows?state=PUBLISHED&category=VISIBLE_LEAK"
        ),
        200,
    )
    assert {w["id"] for w in published["items"]} == {w["id"] for w in f["windows"]}
    windows = expect(citizen.request("GET", f["case_path"] + "/appointment-windows"), 200)
    assert len(windows["items"]) == 3 and "technician_membership_id" not in windows["items"][0]
    row = request_visit(f)
    with env["owner"].begin() as c:
        assert (
            one(c, "SELECT count(*) AS n FROM dispatch_allocations WHERE kind='APPOINTMENT'")["n"]
            == 0
        )
    receipt = confirm(f, row)
    first = receipt["appointment"]
    assert first["status"] == "CONFIRMED"
    profile = expect(f["admin"].request("GET", base + "/dispatch/technicians"), 200)["items"][0]
    expect(
        mutate(
            f["admin"],
            base + "/dispatch/technicians/" + profile["membership_id"],
            dict(
                skill_codes=profile["skill_codes"],
                service_area_codes=profile["service_area_codes"],
                max_daily_minutes=1,
                active=True,
                reason="Synthetic lower capacity conflicting with active visits",
            ),
            profile["profile_version"],
            method="PATCH",
        ),
        409,
    )
    safe = expect(citizen.request("GET", base + "/appointments/" + first["id"]), 200)
    assert "work_order_id" not in safe and "internal_reason" not in safe
    request = request_visit(f, 1, first)
    second = confirm(f, request)["appointment"]
    assert second["replaces_id"] == first["id"]
    assert (
        expect(citizen.request("GET", base + "/appointments/" + first["id"]), 200)["status"]
        == "SUPERSEDED"
    )
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM dispatch_allocations WHERE active AND kind='APPOINTMENT'",
            )["n"]
            == 1
        )
    case = expect(citizen.request("GET", f["case_path"]), 200)
    cancellation = dict(
        caller_action="RESIDENT",
        reason_code="RESIDENT",
        public_reason="Please cancel this confirmed visit.",
        expected_service_version=case["version"],
    )
    result = expect(
        mutate(
            citizen,
            base + "/appointments/" + second["id"] + "/cancellations",
            cancellation,
            second["version"],
        ),
        200,
    )
    assert result["appointment"]["status"] == "CANCELLED"
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM dispatch_allocations WHERE active AND kind='APPOINTMENT'",
            )["n"]
            == 0
        )
        assert one(c, "SELECT count(*) AS n FROM repair_records")["n"] == 0


def test_alternative_acceptance_visit_events_and_legacy_guards(env):
    f = booking_fixture(env)
    base = f["base"]
    sup = f["supervisor"]
    citizen = f["citizen"]
    tech = f["technician"]
    row = request_visit(f)
    path = base + "/appointment-requests/" + row["id"]
    staff = expect(sup.request("GET", path), 200)
    window = f["windows"][1]
    expected = {
        **staff["expectations"],
        "window_version": window["version"],
        "calendar_version": window["calendar_version"],
        "policy_version": window["policy_version"],
    }
    offer = dict(
        decision="OFFER_ALTERNATIVE",
        alternative_window_id=window["id"],
        expected_window_version=window["version"],
        expectations=expected,
        offer_expires_at=(datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        public_message="Please review the offered alternative visit.",
        internal_reason="SYNTHETIC alternate reviewed plan",
    )
    # Current calendar has advanced since each window was published.
    expected["calendar_version"] = expect(sup.request("GET", base + "/dispatch/technicians"), 200)[
        "items"
    ][0]["calendar_version"]
    expect(mutate(sup, path + "/decisions", offer, staff["version"]), 200)["request"]
    safe = expect(citizen.request("GET", path), 200)
    assert "expectations" not in safe and safe["status"] == "ALTERNATIVE_OFFERED"
    case = expect(citizen.request("GET", f["case_path"]), 200)
    accept = dict(
        proposal_revision=safe["proposal_revision"],
        expected_window_version=window["version"],
        expected_service_version=case["version"],
        expected_replaced_appointment_version=None,
    )
    result = expect(mutate(citizen, path + "/accept-alternative", accept, safe["version"]), 200)
    visit = result["appointment"]
    expect(citizen.request("GET", f["case_path"] + "/appointment-requests"), 200)
    expect(sup.request("GET", f["case_path"] + "/appointments"), 200)
    wp = base + "/work-orders/" + f["work"]["id"]
    work = expect(sup.request("GET", wp), 200)
    expect(
        mutate(
            sup,
            wp + "/assignment",
            dict(
                assignee_membership_id=f["tech_membership"]["id"],
                due_at=None,
                reason="SYNTHETIC bypass attempt",
            ),
            work["version"],
        ),
        409,
    )
    expect(
        mutate(
            sup,
            wp + "/transitions",
            dict(target="CANCELLED", reason="SYNTHETIC bypass attempt"),
            work["version"],
        ),
        409,
    )
    brief = expect(tech.request("GET", base + "/appointments/" + visit["id"]), 200)
    assert "service_request_id" not in brief and "internal_reason" not in brief
    key = uuid4()
    body = dict(
        operation_id=str(uuid4()),
        event_type="CHECK_IN",
        observed_at=datetime.now(UTC).isoformat(),
        assignment_version=brief["assignment_version"],
        expected_work_version=brief["work_version"],
        note="SYNTHETIC manual check-in",
        supersedes_event_id=None,
    )
    checked = expect(
        mutate(
            tech,
            base + "/appointments/" + visit["id"] + "/visit-events",
            body,
            visit["version"],
            key=key,
        ),
        201,
    )
    replay = expect(
        mutate(
            tech,
            base + "/appointments/" + visit["id"] + "/visit-events",
            body,
            visit["version"],
            key=key,
        ),
        201,
    )
    assert replay["receipt"]["id"] == checked["receipt"]["id"]
    body.update(
        operation_id=str(uuid4()),
        event_type="VISIT_FINISHED",
        observed_at=datetime.now(UTC).isoformat(),
        note="SYNTHETIC investigation visit finished; no repair claimed",
    )
    finished = expect(
        mutate(
            tech,
            base + "/appointments/" + visit["id"] + "/visit-events",
            body,
            checked["appointment"]["version"],
        ),
        201,
    )
    assert finished["appointment"]["status"] == "VISIT_FINISHED"
    calendar = (
        base
        + "/dispatch/technicians/"
        + f["tech_membership"]["id"]
        + "/calendar?from="
        + f["start"].isoformat().replace("+00:00", "Z")
        + "&to="
        + (f["start"] + timedelta(days=2)).isoformat().replace("+00:00", "Z")
    )
    expect(tech.request("GET", calendar), 200)
    expect(sup.request("GET", calendar), 200)
    expect(
        sup.request(
            "GET",
            base
            + "/dispatch/workload?from="
            + f["start"].isoformat().replace("+00:00", "Z")
            + "&to="
            + (f["start"] + timedelta(days=2)).isoformat().replace("+00:00", "Z"),
        ),
        200,
    )
    with env["owner"].begin() as c:
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM dispatch_allocations WHERE active AND kind='APPOINTMENT'",
            )["n"]
            == 0
        )
        assert (
            one(c, "SELECT status FROM work_orders WHERE id=:w", w=f["work"]["id"])["status"]
            == "ASSIGNED"
        )
        assert one(c, "SELECT count(*) AS n FROM repair_records")["n"] == 0


def test_request_withdrawal_decline_and_pending_cancellation(env):
    f = booking_fixture(env, policy_overrides={"free_cancel_before_minutes": 2880})
    citizen = f["citizen"]
    sup = f["supervisor"]
    base = f["base"]
    row = request_visit(f)
    path = base + "/appointment-requests/" + row["id"]
    expect(
        mutate(
            citizen,
            path + "/withdrawals",
            dict(reason_code="RESIDENT", reason="Withdraw this synthetic request"),
            row["version"],
        ),
        200,
    )
    row = request_visit(f)
    path = base + "/appointment-requests/" + row["id"]
    expect(
        mutate(
            sup,
            path + "/decisions",
            dict(
                decision="DECLINE",
                public_message="No visit will be confirmed from this request.",
                internal_reason="SYNTHETIC reviewed decline",
                reason_code="REVIEW",
            ),
            row["version"],
        ),
        200,
    )
    row = request_visit(f)
    visit = confirm(f, row)["appointment"]
    case = expect(citizen.request("GET", f["case_path"]), 200)
    cancel = dict(
        caller_action="RESIDENT",
        reason_code="RESIDENT",
        public_reason="Please review this late cancellation.",
        expected_service_version=case["version"],
    )
    pending = expect(
        mutate(
            citizen,
            base + "/appointments/" + visit["id"] + "/cancellations",
            cancel,
            visit["version"],
        ),
        200,
    )
    assert (
        pending["appointment"]["status"] == "CONFIRMED"
        and pending["appointment"]["cancellation_pending"]
    )
    work = expect(sup.request("GET", base + "/work-orders/" + f["work"]["id"]), 200)
    staffcancel = {
        **cancel,
        "caller_action": "SUPERVISOR",
        "expected_service_version": pending["current_service_version"],
        "expected_work_version": work["version"],
        "expected_assignment_version": work["assignment_version"],
        "internal_reason": "SYNTHETIC cancellation review",
        "disposition": "ACCEPT_PENDING_CANCEL",
    }
    cancelled = expect(
        mutate(
            sup,
            base + "/appointments/" + visit["id"] + "/cancellations",
            staffcancel,
            pending["appointment"]["version"],
        ),
        200,
    )
    assert cancelled["appointment"]["status"] == "CANCELLED"


def test_concurrent_confirmation_and_unauthorized_booking_access(env):
    from concurrent.futures import ThreadPoolExecutor

    from test_service_foundation import resident

    f = booking_fixture(env)
    row = request_visit(f)
    base = f["base"]
    path = base + "/appointment-requests/" + row["id"]
    sup = f["supervisor"]
    staff = expect(sup.request("GET", path), 200)
    other = login(env, "supervisor@example.invalid")
    body = dict(
        decision="CONFIRM_REQUESTED",
        expectations=staff["expectations"],
        public_message="Confirmed through synthetic concurrent acceptance.",
        internal_reason="SYNTHETIC concurrent confirmation",
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: mutate(client, path + "/decisions", body, staff["version"]),
                [sup, other],
            )
        )
    assert sorted(r.status_code for r in results) == [200, 412]
    visit = next(r.json()["appointment"] for r in results if r.status_code == 200)
    stranger = resident(env, "dispatch-stranger@example.invalid")
    for p in [path, base + "/appointments/" + visit["id"], f["case_path"] + "/appointment-windows"]:
        expect(stranger.request("GET", p), 404)
    expect(f["admin"].request("GET", base + "/appointments/" + visit["id"]), 403)
    expect(f["technician"].request("GET", path), 404)
    with env["owner"].begin() as c:
        assert one(c, "SELECT count(*) AS n FROM appointments WHERE status='CONFIRMED'")["n"] == 1
        assert (
            one(
                c,
                "SELECT count(*) AS n FROM dispatch_allocations WHERE active AND kind='APPOINTMENT'",
            )["n"]
            == 1
        )


def foundation(env):
    admin = login(env, "admin-a@example.invalid")
    supervisor, _ = provision(env, "SUPERVISOR", "dispatch-supervisor@example.invalid", admin)
    technician, membership = provision(
        env, "TECHNICIAN", "dispatch-technician@example.invalid", admin
    )
    base = f"/api/v1/orgs/{env['org']['id']}/dispatch"
    with env["owner"].begin() as c:
        member = one(c, "SELECT * FROM organization_memberships WHERE id=:i", i=membership["id"])
    enroll = {
        "membership_id": str(member["id"]),
        "expected_membership_version": member["version"],
        "skill_codes": ["SYNTHETIC_INSPECTION"],
        "service_area_codes": ["SYNTHETIC_AREA"],
        "max_daily_minutes": 480,
        "exclusive_dispatch_acknowledged": True,
        "reason": "Synthetic acceptance enrollment",
    }
    return admin, supervisor, technician, base, enroll


def test_dispatch_enrollment_policy_and_access(env):
    admin, sup, tech, base, enroll = foundation(env)
    policy = expect(admin.request("GET", base + "/policy"), 200)
    assert not policy["configured"] and not policy["booking_enabled"]
    assert policy["horizon_days"] is None and policy["allowed_duration_minutes"] == []
    expect(mutate(sup, base + "/technicians", enroll), 403)
    key = uuid4()
    profile = expect(mutate(admin, base + "/technicians", enroll, key=key), 201)
    assert profile["scheduling_health"] == "UNCONFIGURED"
    assert expect(mutate(admin, base + "/technicians", enroll, key=key), 201) == profile
    expect(tech.request("GET", base + "/technicians"), 403)
    patch = {
        k: enroll[k] for k in ("skill_codes", "service_area_codes", "max_daily_minutes", "reason")
    }
    patch["active"] = False
    path = base + "/technicians/" + enroll["membership_id"]
    expect(mutate(admin, path, patch, method="PATCH"), 428)
    changed = expect(mutate(admin, path, patch, profile["profile_version"], method="PATCH"), 200)
    assert not changed["active"] and changed["calendar_version"] == 2
    expect(mutate(admin, path, patch, profile["profile_version"], method="PATCH"), 412)


def test_dispatch_shift_overlap_and_atomic_block_replacement(env):
    admin, sup, tech, base, enroll = foundation(env)
    profile = expect(mutate(admin, base + "/technicians", enroll), 201)
    start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=1)
    span = {"start_at": start.isoformat(), "end_at": (start + timedelta(hours=8)).isoformat()}
    shift = {
        "technician_membership_id": enroll["membership_id"],
        "expected_calendar_version": 1,
        "interval": span,
        "reason": "Synthetic dated shift for acceptance",
    }
    first = expect(mutate(sup, base + "/shifts", shift, profile["profile_version"]), 201)
    shift["expected_calendar_version"] = first["calendar_version"]
    expect(mutate(sup, base + "/shifts", shift, 2), 409)
    block = {
        "technician_membership_id": enroll["membership_id"],
        "expected_calendar_version": 2,
        "kind": "UNAVAILABLE",
        "interval": {
            "start_at": start.isoformat(),
            "end_at": (start + timedelta(hours=1)).isoformat(),
        },
        "work_order_id": None,
        "expected_work_version": None,
        "reason_code": "SYNTHETIC",
        "internal_reason": "Synthetic unavailability",
    }
    a = expect(mutate(sup, base + "/blocks", block, 2), 201)
    block["interval"] = {
        "start_at": (start + timedelta(hours=2)).isoformat(),
        "end_at": (start + timedelta(hours=3)).isoformat(),
    }
    block["expected_calendar_version"] = 3
    expect(mutate(sup, base + "/blocks", block, 3), 201)
    replacement = {
        "expected_calendar_version": 4,
        "expected_work_version": None,
        "reason": "Synthetic conflicting replacement",
        "interval": block["interval"],
    }
    expect(
        mutate(sup, base + "/blocks/" + a["id"] + "/replacements", replacement, a["version"]), 409
    )
    with env["owner"].begin() as c:
        saved = one(c, "SELECT * FROM dispatch_allocations WHERE id=:i", i=a["id"])
        assert saved["active"] and saved["version"] == a["version"]
    replacement["interval"] = {
        "start_at": (start + timedelta(hours=4)).isoformat(),
        "end_at": (start + timedelta(hours=5)).isoformat(),
    }
    replaced = expect(
        mutate(sup, base + "/blocks/" + a["id"] + "/replacements", replacement, a["version"]), 201
    )
    release = {
        "expected_calendar_version": replaced["calendar_version"],
        "expected_work_version": None,
        "reason": "Release synthetic block",
    }
    expect(
        mutate(sup, base + "/blocks/" + replaced["id"] + "/release", release, replaced["version"]),
        200,
    )
    # With an active block, withdrawing its containing shift must fail.
    shift_change = {
        "interval": span,
        "status": "WITHDRAWN",
        "expected_calendar_version": 6,
        "reason": "Synthetic shift withdrawal",
    }
    expect(
        mutate(
            sup, base + "/shifts/" + first["id"], shift_change, first["version"], method="PATCH"
        ),
        409,
    )


def test_empty_shift_withdrawal_and_window_withdrawal(env):
    f = booking_fixture(env)
    sup = f["supervisor"]
    base = f["base"]
    w = f["windows"][0]
    roster = expect(sup.request("GET", base + "/dispatch/technicians"), 200)["items"][0]
    expect(
        mutate(
            sup,
            base + "/dispatch/appointment-windows/" + w["id"] + "/withdrawals",
            dict(
                expected_calendar_version=roster["calendar_version"],
                reason="Synthetic window withdrawn",
            ),
            w["version"],
        ),
        200,
    )
    p = expect(sup.request("GET", base + "/dispatch/technicians"), 200)["items"][0]
    span = {
        "start_at": (f["start"] + timedelta(days=3)).isoformat(),
        "end_at": (f["start"] + timedelta(days=3, hours=1)).isoformat(),
    }
    shift = expect(
        mutate(
            sup,
            base + "/dispatch/shifts",
            dict(
                technician_membership_id=f["tech_membership"]["id"],
                expected_calendar_version=p["calendar_version"],
                interval=span,
                reason="Synthetic separate shift",
            ),
            p["profile_version"],
        ),
        201,
    )
    changed = expect(
        mutate(
            sup,
            base + "/dispatch/shifts/" + shift["id"],
            dict(
                interval=span,
                status="WITHDRAWN",
                expected_calendar_version=shift["calendar_version"],
                reason="Synthetic shift withdrawal",
            ),
            shift["version"],
            method="PATCH",
        ),
        200,
    )
    assert changed["status"] == "WITHDRAWN"
