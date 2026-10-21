"""Reject PostgreSQL numeric NaN/infinities in pipe length metadata."""

from alembic import op

revision = "m03_003"
down_revision = "m03_002"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE pipe_segments ADD CONSTRAINT finite_pipe_lengths CHECK(geometry_length_m::text NOT IN ('NaN','Infinity','-Infinity') AND (surveyed_length_m IS NULL OR surveyed_length_m::text NOT IN ('NaN','Infinity','-Infinity')) AND (length_uncertainty_m IS NULL OR length_uncertainty_m::text NOT IN ('NaN','Infinity','-Infinity')))"
    )


def downgrade():
    op.drop_constraint("finite_pipe_lengths", "pipe_segments", type_="check")
