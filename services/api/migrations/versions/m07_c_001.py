"""Add persisted in-app communications; no privileged worker or upload activation."""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "m07_c_001"
down_revision = "m07_b_005"
branch_labels = None
depends_on = None
TABLES = (
    "notification_delivery_attempts",
    "notifications",
    "background_jobs",
    "feedback_events",
    "feedback_items",
    "notification_preferences",
)


def upgrade():
    op.get_bind().exec_driver_sql((Path(__file__).parents[1] / "m07_c.sql").read_text())
    tenant = "organization_id::text=current_setting('hydro.organization_id',true)"
    supervisor = "hydro_m07_role(ARRAY['SUPERVISOR'])"
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY migration_scope ON {table} TO hydro_migrator USING(true) WITH CHECK(true)"
        )
        if table == "notification_preferences":
            read = f"hydro_m07_own(membership_id) OR {supervisor}"
            write = "hydro_m07_own(membership_id)"
            create = "(NOT in_app AND event_categories='[]'::jsonb AND quiet_hours IS NULL AND version=1 AND EXISTS(SELECT 1 FROM organization_memberships m WHERE m.id=membership_id AND m.user_id::text=current_setting('hydro.user_id',true))) OR hydro_m07_role(ARRAY['ADMIN'])"
        elif table == "feedback_items":
            read = write = (
                f"hydro_m07_own(owner_membership_id) OR {supervisor} OR (service_request_id IS NULL AND complaint_id IS NULL AND hydro_m07_role(ARRAY['ADMIN']))"
            )
            create = "hydro_m07_own(owner_membership_id)"
        elif table == "feedback_events":
            read = write = create = "EXISTS(SELECT 1 FROM feedback_items f WHERE f.id=feedback_id)"
        elif table == "background_jobs":
            read = write = supervisor
            create = "EXISTS(SELECT 1 FROM domain_events e WHERE e.id=domain_event_id)"
        elif table == "notifications":
            read = write = f"hydro_m07_own(recipient_id) OR {supervisor}"
            create = supervisor
        else:
            read = write = create = supervisor
        op.execute(f"CREATE POLICY read_scope ON {table} FOR SELECT USING ({tenant} AND ({read}))")
        op.execute(
            f"CREATE POLICY create_scope ON {table} FOR INSERT WITH CHECK ({tenant} AND ({create}))"
        )
        op.execute(f"GRANT SELECT,INSERT ON {table} TO hydro_app")
        if table not in {"feedback_events", "notification_delivery_attempts"}:
            op.execute(
                f"CREATE POLICY update_scope ON {table} FOR UPDATE USING ({tenant} AND ({write})) WITH CHECK ({tenant} AND ({write}))"
            )
            op.execute(f"GRANT UPDATE ON {table} TO hydro_app")
        else:
            op.execute(
                f"CREATE TRIGGER immutable_history BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable()"
            )
    from hydro.cli import seed_catalogue

    seed_catalogue(op.get_bind())


def downgrade():
    c = op.get_bind()
    for table in TABLES[:-1]:
        if c.execute(text(f"SELECT 1 FROM {table} LIMIT 1")).first():
            raise RuntimeError("Populated M07-C history is forward-only")
    if c.execute(
        text(
            "SELECT 1 FROM notification_preferences WHERE version<>1 OR in_app OR event_categories<>'[]'::jsonb OR quiet_hours IS NOT NULL LIMIT 1"
        )
    ).first():
        raise RuntimeError("Configured preferences are forward-only")
    op.execute("DROP TRIGGER notification_preferences_provision ON organization_memberships")
    op.execute("DROP FUNCTION hydro_notification_preferences_provision()")
    for table in TABLES:
        op.drop_table(table)
