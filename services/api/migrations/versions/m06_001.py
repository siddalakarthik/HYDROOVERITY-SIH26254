"""Immutable tenant-isolated observation replays; no operational linkage."""

from alembic import op
from sqlalchemy import text

revision = "m06_001"
down_revision = "m07_a_001"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE scientific_replays(
          id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
          organization_id uuid NOT NULL REFERENCES organizations(id),
          creator_id uuid NOT NULL,
          created_at timestamptz NOT NULL DEFAULT now(),
          source_category text NOT NULL DEFAULT 'SIMULATION' CHECK(source_category='SIMULATION'),
          operation_key uuid NOT NULL,
          scenario_code text NOT NULL CHECK(length(scenario_code) BETWEEN 3 AND 80),
          catalogue_hash text NOT NULL CHECK(catalogue_hash ~ '^[0-9a-f]{64}$'),
          content_hash text NOT NULL CHECK(content_hash ~ '^[0-9a-f]{64}$'),
          snapshot jsonb NOT NULL CHECK(jsonb_typeof(snapshot)='object'),
          UNIQUE(organization_id,id),
          UNIQUE(organization_id,creator_id,operation_key),
          FOREIGN KEY(organization_id,creator_id) REFERENCES organization_memberships(organization_id,id)
        )
    """)
    op.execute(
        "CREATE INDEX scientific_replay_list ON scientific_replays(organization_id,created_at DESC,id DESC)"
    )
    op.execute("ALTER TABLE scientific_replays ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE scientific_replays FORCE ROW LEVEL SECURITY")
    scope = "organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['ENGINEER'])"
    op.execute(f"CREATE POLICY read_scope ON scientific_replays FOR SELECT USING ({scope})")
    op.execute(
        f"CREATE POLICY insert_scope ON scientific_replays FOR INSERT WITH CHECK ({scope} AND hydro_m07_own(creator_id))"
    )
    op.execute(
        "CREATE POLICY migration_scope ON scientific_replays TO hydro_migrator USING(true) WITH CHECK(true)"
    )
    op.execute(
        "CREATE TRIGGER immutable_science BEFORE UPDATE OR DELETE ON scientific_replays FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable()"
    )
    op.execute("GRANT SELECT,INSERT ON scientific_replays TO hydro_app")
    from hydro.cli import seed_catalogue

    seed_catalogue(op.get_bind())


def downgrade():
    if op.get_bind().execute(text("SELECT 1 FROM scientific_replays LIMIT 1")).first():
        raise RuntimeError("Populated scientific replay provenance is forward-only")
    op.drop_table("scientific_replays")
    op.execute(
        "DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code IN ('simulations.read','simulations.write'))"
    )
    op.execute("DELETE FROM permissions WHERE code IN ('simulations.read','simulations.write')")
