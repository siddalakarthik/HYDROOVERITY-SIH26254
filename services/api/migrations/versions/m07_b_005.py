"""Owner-approved boolean governance check; no resident case projection."""

from alembic import op

revision = "m07_b_005"
down_revision = "m07_b_004"
branch_labels = None
depends_on = None


def upgrade():
    # Explicit owner approval: current ADMIN/SUPERVISOR, own utility only,
    # one boolean, fixed search path, no PUBLIC execution or case details.
    op.execute("""
    CREATE FUNCTION hydro_dispatch_has_commitments(member uuid) RETURNS boolean
    LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public AS $$
      SELECT public.hydro_m07_role(ARRAY['ADMIN','SUPERVISOR']) AND EXISTS(
       SELECT 1 FROM public.appointments a
       WHERE a.organization_id::text=current_setting('hydro.organization_id',true)
       AND (member IS NULL OR a.assignee_id=member) AND a.status IN ('CONFIRMED','CHECKED_IN'))
    $$;
    REVOKE ALL ON FUNCTION hydro_dispatch_has_commitments(uuid) FROM PUBLIC;
    GRANT EXECUTE ON FUNCTION hydro_dispatch_has_commitments(uuid) TO hydro_app;
    """)


def downgrade():
    op.execute("DROP FUNCTION hydro_dispatch_has_commitments(uuid)")
