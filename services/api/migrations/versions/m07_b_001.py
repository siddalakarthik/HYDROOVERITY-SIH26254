"""Add explicit scheduling governance and constrained allocation foundations."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "m07_b_001"
down_revision = "m06_001"
branch_labels = None
depends_on = None

TABLES = (
    "dispatch_allocations",
    "dispatch_shifts",
    "dispatch_technician_profiles",
    "dispatch_policy",
    "dispatch_calendar_subjects",
)


def upgrade():
    op.get_bind().exec_driver_sql((Path(__file__).parents[1] / "m07_b.sql").read_text())
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY migration_scope ON {table} TO hydro_migrator USING(true) WITH CHECK(true)"
        )
        if table == "dispatch_calendar_subjects":
            continue
        tenant = "organization_id::text=current_setting('hydro.organization_id',true)"
        if table == "dispatch_technician_profiles":
            read = "hydro_m07_role(ARRAY['ADMIN','SUPERVISOR']) OR (hydro_m07_role(ARRAY['TECHNICIAN']) AND hydro_m07_own(membership_id))"
            write = "hydro_m07_role(ARRAY['ADMIN','SUPERVISOR'])"
        elif table == "dispatch_policy":
            read = "hydro_m07_role(ARRAY['ADMIN','SUPERVISOR'])"
            write = "hydro_m07_role(ARRAY['ADMIN'])"
        else:
            read = "hydro_m07_role(ARRAY['SUPERVISOR']) OR (hydro_m07_role(ARRAY['TECHNICIAN']) AND EXISTS(SELECT 1 FROM dispatch_technician_profiles p WHERE p.id=profile_id AND hydro_m07_own(p.membership_id)))"
            write = "hydro_m07_role(ARRAY['SUPERVISOR'])"
        op.execute(f"CREATE POLICY read_scope ON {table} FOR SELECT USING ({tenant} AND ({read}))")
        op.execute(
            f"CREATE POLICY insert_scope ON {table} FOR INSERT WITH CHECK ({tenant} AND ({write}))"
        )
        op.execute(
            f"CREATE POLICY update_scope ON {table} FOR UPDATE USING ({tenant} AND ({write})) WITH CHECK ({tenant} AND ({write}))"
        )
        op.execute(f"GRANT SELECT,INSERT,UPDATE ON {table} TO hydro_app")
    from hydro.cli import seed_catalogue

    seed_catalogue(op.get_bind())


def downgrade():
    c = op.get_bind()
    for table in TABLES:
        condition = (
            " WHERE configured OR booking_enabled OR version<>1"
            if table == "dispatch_policy"
            else ""
        )
        if c.execute(text(f"SELECT 1 FROM {table}{condition} LIMIT 1")).first():
            raise RuntimeError("Populated M07-B scheduling history is forward-only")
    op.execute("DROP TRIGGER dispatch_initial_policy ON organizations")
    op.execute("DROP FUNCTION hydro_dispatch_initial_policy(),hydro_dispatch_enroll(uuid,uuid)")
    for table in TABLES:
        op.drop_table(table)
    op.execute("DROP FUNCTION hydro_dispatch_profile_identity()")
