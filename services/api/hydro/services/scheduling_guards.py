"""Legacy operations share scheduler serialization and cannot invalidate commitments."""

from ..db import one
from ..errors import require


def guard_work_change(scope, work, body):
    c = scope.c
    visit = one(
        c,
        "SELECT id,status FROM appointments WHERE work_order_id=:w AND status IN ('CONFIRMED','CHECKED_IN')",
        w=work["id"],
    )
    assignment = scope.op["path"].endswith("/assignment")
    if visit:
        require(
            not assignment and body.get("target") not in {"CANCELLED", "COMPLETED"},
            409,
            "VISIT_DISPOSITION_REQUIRED",
            "Cancel or finish the active appointment before changing assignment or closing work",
        )
        require(
            body.get("target") != "IN_PROGRESS" or visit["status"] == "CHECKED_IN",
            409,
            "VISIT_CHECKIN_REQUIRED",
            "Check in to the confirmed visit before starting scheduled work",
        )
    if assignment:
        profile = one(
            c,
            "SELECT * FROM dispatch_technician_profiles WHERE membership_id=:m",
            m=body["assignee_membership_id"],
        )
        if profile:
            planned = one(
                c,
                "SELECT id FROM dispatch_allocations WHERE profile_id=:p AND work_order_id=:w AND kind='WORK_BLOCK' AND active",
                p=profile["id"],
                w=work["id"],
            )
            commitments = one(
                c,
                "SELECT id FROM dispatch_allocations WHERE profile_id=:p AND kind='APPOINTMENT' AND active LIMIT 1",
                p=profile["id"],
            )
            require(
                profile["active"] and (planned or not commitments),
                409,
                "WORK_PLAN_REQUIRED",
                "Review existing commitments and create a work plan before assigning additional work",
            )
    if body.get("target") in {"CANCELLED", "COMPLETED"}:
        require(
            not one(
                c,
                "SELECT id FROM dispatch_allocations WHERE work_order_id=:w AND active LIMIT 1",
                w=work["id"],
            ),
            409,
            "ALLOCATION_DISPOSITION_REQUIRED",
            "Release the work allocation before closing work",
        )
