"""Retain private complaint review reasons without exposing them to citizens."""

from alembic import op
from sqlalchemy import text

revision = "m03_004"
down_revision = "m03_003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE complaint_status_events ADD COLUMN internal_reason text CHECK(internal_reason IS NULL OR length(internal_reason) BETWEEN 5 AND 2000)"
    )


def downgrade():
    if (
        op.get_bind()
        .execute(
            text("SELECT 1 FROM complaint_status_events WHERE internal_reason IS NOT NULL LIMIT 1")
        )
        .first()
    ):
        raise RuntimeError(
            "Forward-only with populated private review history; restore an isolated snapshot instead"
        )
    op.drop_column("complaint_status_events", "internal_reason")
