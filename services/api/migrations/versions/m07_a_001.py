"""Add service foundation and manual findings, preserving existing wire behavior."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "m07_a_001"
down_revision = "m03_004"
branch_labels = None
depends_on = None

TABLES = (
    "work_investigation_findings",
    "service_work_order_links",
    "service_public_updates",
    "service_request_events",
    "service_requests",
)


def upgrade():
    op.get_bind().exec_driver_sql(
        (Path(__file__).parents[1] / "m07_a.sql").read_text(encoding="utf-8")
    )
    for table in TABLES[:-1]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        if table == "work_investigation_findings":
            condition = "hydro_m07_role(ARRAY['SUPERVISOR','ENGINEER']) OR (hydro_m07_role(ARRAY['TECHNICIAN']) AND EXISTS(SELECT 1 FROM work_orders w WHERE w.id=work_order_id AND hydro_m07_own(w.assignee_id)))"
            write = "hydro_m07_role(ARRAY['TECHNICIAN']) AND EXISTS(SELECT 1 FROM work_orders w WHERE w.id=work_order_id AND hydro_m07_own(w.assignee_id))"
        elif table in {"service_request_events", "service_work_order_links"}:
            condition = "hydro_m07_role(ARRAY['SUPERVISOR'])"
            write = (
                "hydro_m07_role(ARRAY['SUPERVISOR'])"
                if table.endswith("links")
                else "EXISTS(SELECT 1 FROM service_requests s WHERE s.id=request_id)"
            )
        else:
            condition = write = "EXISTS(SELECT 1 FROM service_requests s WHERE s.id=request_id)"
        tenant = "organization_id::text=current_setting('hydro.organization_id',true)"
        op.execute(
            f"CREATE POLICY read_scope ON {table} FOR SELECT USING ({tenant} AND ({condition}))"
        )
        op.execute(
            f"CREATE POLICY insert_scope ON {table} FOR INSERT WITH CHECK ({tenant} AND ({write}))"
        )
        op.execute(
            f"CREATE POLICY migration_scope ON {table} TO hydro_migrator USING(true) WITH CHECK(true)"
        )
        op.execute(
            f"CREATE TRIGGER immutable_m07 BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable()"
        )
    from hydro.cli import seed_catalogue

    seed_catalogue(op.get_bind())


def downgrade():
    c = op.get_bind()
    for table in TABLES:
        if c.execute(text(f"SELECT 1 FROM {table} LIMIT 1")).first():
            raise RuntimeError(
                "Populated M07-A history is forward-only; restore an isolated snapshot"
            )
    if c.execute(text("SELECT 1 FROM work_orders WHERE task_purpose<>'REPAIR' LIMIT 1")).first():
        raise RuntimeError("Investigation work cannot be downgraded to repair")
    for table in TABLES:
        op.drop_table(table)
    op.execute(
        "DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code LIKE 'service_requests.%' OR code LIKE 'investigation_findings.%')"
    )
    op.execute(
        "DELETE FROM permissions WHERE code LIKE 'service_requests.%' OR code LIKE 'investigation_findings.%'"
    )
    op.execute("DROP FUNCTION hydro_m07_own(uuid),hydro_m07_role(text[])")
    op.drop_column("work_orders", "task_purpose")
