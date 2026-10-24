"""Atomic appointment and visit records with separate resident projections."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "m07_b_002"
down_revision = "m07_b_001"
branch_labels = None
depends_on = None
TABLES = ("appointment_events", "appointments", "appointment_requests", "appointment_windows")


def upgrade():
    op.get_bind().exec_driver_sql((Path(__file__).parents[1] / "m07_b_bookings.sql").read_text())
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY migration_scope ON {table} TO hydro_migrator USING(true) WITH CHECK(true)"
        )
        tenant = "organization_id::text=current_setting('hydro.organization_id',true)"
        staff = "hydro_m07_role(ARRAY['SUPERVISOR'])"
        if table == "appointment_windows":
            read = staff + " OR hydro_m07_role(ARRAY['CITIZEN'])"
        elif table == "appointment_events":
            read = (
                staff
                + " OR EXISTS(SELECT 1 FROM appointments a WHERE a.id=appointment_id AND hydro_m07_own(a.assignee_id))"
            )
        else:
            read = staff + " OR hydro_dispatch_service_visible(request_id)"
            if table == "appointments":
                read += " OR (hydro_m07_role(ARRAY['TECHNICIAN']) AND hydro_m07_own(assignee_id))"
        write = read if table != "appointment_windows" else staff
        op.execute(f"CREATE POLICY read_scope ON {table} FOR SELECT USING({tenant} AND ({read}))")
        op.execute(
            f"CREATE POLICY insert_scope ON {table} FOR INSERT WITH CHECK({tenant} AND ({write}))"
        )
        if table != "appointment_events":
            op.execute(
                f"CREATE POLICY update_scope ON {table} FOR UPDATE USING({tenant} AND ({write})) WITH CHECK({tenant} AND ({write}))"
            )
        op.execute(
            f"GRANT SELECT,INSERT{',UPDATE' if table != 'appointment_events' else ''} ON {table} TO hydro_app"
        )
    # Resident confirmations need constrained scheduler writes while retaining tenant RLS.
    for table in (
        "dispatch_technician_profiles",
        "dispatch_allocations",
        "dispatch_policy",
        "dispatch_shifts",
    ):
        op.execute(
            f"CREATE POLICY resident_scheduler_read ON {table} FOR SELECT USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['CITIZEN']))"
        )
    for table in ("dispatch_technician_profiles", "dispatch_allocations"):
        op.execute(
            f"CREATE POLICY resident_scheduler_write ON {table} FOR ALL USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['CITIZEN'])) WITH CHECK(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['CITIZEN']))"
        )
    from hydro.cli import seed_catalogue

    seed_catalogue(op.get_bind())


def downgrade():
    c = op.get_bind()
    if any(c.execute(text(f"SELECT 1 FROM {t} LIMIT 1")).first() for t in TABLES):
        raise RuntimeError("Populated appointment history is forward-only")
    if c.execute(
        text(
            "SELECT 1 FROM service_work_order_links WHERE dispatch_service_area_code IS NOT NULL LIMIT 1"
        )
    ).first():
        raise RuntimeError("Reviewed dispatch linkage is forward-only")
    for table in (
        "dispatch_technician_profiles",
        "dispatch_allocations",
        "dispatch_policy",
        "dispatch_shifts",
    ):
        op.execute(f"DROP POLICY resident_scheduler_read ON {table}")
    for table in ("dispatch_technician_profiles", "dispatch_allocations"):
        op.execute(f"DROP POLICY resident_scheduler_write ON {table}")
    op.execute("ALTER TABLE dispatch_allocations DROP CONSTRAINT dispatch_appointment_fk")
    for (name,) in c.execute(
        text(
            "SELECT conname FROM pg_constraint WHERE conrelid='appointment_requests'::regclass AND confrelid='appointments'::regclass"
        )
    ):
        op.drop_constraint(name, "appointment_requests", type_="foreignkey")
    for table in TABLES:
        op.drop_table(table)
    op.execute(
        "ALTER TABLE service_work_order_links DROP COLUMN dispatch_service_area_code, DROP COLUMN dispatch_required_skill_codes"
    )
    op.execute("DROP FUNCTION hydro_dispatch_case_links(uuid),hydro_dispatch_service_visible(uuid)")
