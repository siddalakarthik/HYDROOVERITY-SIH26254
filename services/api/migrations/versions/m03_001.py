"""M03 selected operational tables, tenant constraints and restricted runtime grants."""
from pathlib import Path
from alembic import op

revision = "m03_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Static SQL is reviewed source, not generated from the runtime catalogue.
    sql = (Path(__file__).parents[1] / "schema.sql").read_text(encoding="utf-8")
    op.get_bind().exec_driver_sql(sql)
    op.get_bind().exec_driver_sql((Path(__file__).parents[1] / "security.sql").read_text())
    op.execute("GRANT SELECT ON alembic_version TO hydro_app")


def downgrade() -> None:
    raise RuntimeError("M03 is forward-only. Restore the tested disposable snapshot; never drop populated history.")
