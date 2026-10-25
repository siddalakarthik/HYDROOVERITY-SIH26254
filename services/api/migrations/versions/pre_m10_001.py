"""Add opt-in complaint notifications without changing existing preferences."""

from alembic import op
from sqlalchemy import text

revision = "pre_m10_001"
down_revision = "m07_c_001"
branch_labels = None
depends_on = None


def replace_check(table, column, expression):
    # Resolve the existing PostgreSQL-generated constraint name by column metadata.
    # Exactly one relevant CHECK is expected; refuse ambiguity instead of dropping others.
    rows = (
        op.get_bind()
        .execute(
            text(
                "SELECT c.conname FROM pg_constraint c JOIN pg_attribute a "
                "ON a.attrelid=c.conrelid AND a.attnum=ANY(c.conkey) "
                "WHERE c.conrelid=CAST(:table AS regclass) AND c.contype='c' AND a.attname=:column"
            ),
            {"table": table, "column": column},
        )
        .scalars()
        .all()
    )
    if len(rows) != 1:
        raise RuntimeError("Unexpected notification constraint; migration refused")
    op.drop_constraint(rows[0], table, type_="check")
    op.create_check_constraint(rows[0], table, expression)


def constraints(complaints):
    categories = "'SERVICE_PROGRESS','APPOINTMENT','WORK_ASSIGNMENT','SERVICE_FEEDBACK'"
    resources = (
        "'service_requests','appointments','appointment_requests','work_orders','feedback_items'"
    )
    preference_categories = '["SERVICE_PROGRESS","APPOINTMENT","WORK_ASSIGNMENT","SERVICE_FEEDBACK"'
    if complaints:
        categories += ",'COMPLAINT_PROGRESS'"
        resources += ",'citizen_complaints'"
        preference_categories += ',"COMPLAINT_PROGRESS"'
    preference_categories += "]"
    replace_check("notifications", "event_category", f"event_category IN ({categories})")
    replace_check("notifications", "resource_type", f"resource_type IN ({resources})")
    replace_check(
        "notification_preferences",
        "event_categories",
        "jsonb_typeof(event_categories)='array' AND event_categories <@ '"
        + preference_categories
        + "'::jsonb",
    )


def upgrade():
    constraints(True)


def downgrade():
    # Retain all audit/delivery records and consent. Never erase them to fit old constraints.
    connection = op.get_bind()
    connection.exec_driver_sql(
        "LOCK TABLE notifications, notification_preferences, background_jobs IN ACCESS EXCLUSIVE MODE"
    )
    exists = connection.exec_driver_sql(
        "SELECT EXISTS(SELECT 1 FROM notifications WHERE event_category='COMPLAINT_PROGRESS' "
        "OR resource_type='citizen_complaints') OR EXISTS(SELECT 1 FROM notification_preferences "
        "WHERE event_categories ? 'COMPLAINT_PROGRESS') OR EXISTS(SELECT 1 FROM background_jobs "
        'WHERE targets @> \'[{"resource_type":"citizen_complaints"}]\'::jsonb)'
    ).scalar_one()
    if exists:
        raise RuntimeError("Complaint notification data exists; non-destructive downgrade refused")
    constraints(False)
