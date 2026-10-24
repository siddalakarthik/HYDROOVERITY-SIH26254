"""Permit audited eligibility review on existing immutable work relationships."""

from alembic import op
from sqlalchemy import text

revision = "m07_b_004"
down_revision = "m07_b_003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE service_work_order_links ADD COLUMN dispatch_review_service_version bigint CHECK(dispatch_review_service_version>0)"
    )
    op.execute("DROP TRIGGER immutable_m07 ON service_work_order_links")
    op.execute("""
    CREATE FUNCTION hydro_dispatch_link_review() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' AND hydro_m07_role(ARRAY['SUPERVISOR'])
       AND NEW.organization_id::text=current_setting('hydro.organization_id',true)
       AND NEW.version=OLD.version+1
       AND (to_jsonb(NEW)-ARRAY['dispatch_service_area_code','dispatch_required_skill_codes','dispatch_review_service_version','version'])
         =(to_jsonb(OLD)-ARRAY['dispatch_service_area_code','dispatch_required_skill_codes','dispatch_review_service_version','version'])
       AND NEW.dispatch_review_service_version>coalesce(OLD.dispatch_review_service_version,0)
       AND NEW.dispatch_service_area_code IS NOT NULL AND NEW.dispatch_required_skill_codes IS NOT NULL
       AND EXISTS(SELECT 1 FROM service_request_events e WHERE e.request_id=NEW.request_id AND e.event_kind='DISPATCH_ELIGIBILITY_REVIEWED'
        AND e.sequence=NEW.dispatch_review_service_version AND e.sequence=(SELECT s.version FROM service_requests s WHERE s.id=NEW.request_id))
      THEN RETURN NEW; END IF;
      RAISE EXCEPTION 'immutable relationship or missing review' USING ERRCODE='42501';
    END $$;
    REVOKE ALL ON FUNCTION hydro_dispatch_link_review() FROM PUBLIC;
    CREATE TRIGGER immutable_m07 BEFORE UPDATE OR DELETE ON service_work_order_links FOR EACH ROW EXECUTE FUNCTION hydro_dispatch_link_review();
    CREATE POLICY review_scope ON service_work_order_links FOR UPDATE USING(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['SUPERVISOR'])) WITH CHECK(organization_id::text=current_setting('hydro.organization_id',true) AND hydro_m07_role(ARRAY['SUPERVISOR']));
    GRANT UPDATE(dispatch_service_area_code,dispatch_required_skill_codes,dispatch_review_service_version,version) ON service_work_order_links TO hydro_app;
    """)


def downgrade():
    if (
        op.get_bind()
        .execute(text("SELECT 1 FROM service_work_order_links WHERE version>1 LIMIT 1"))
        .first()
    ):
        raise RuntimeError("Reviewed dispatch relationship history is forward-only")
    op.execute("DROP TRIGGER immutable_m07 ON service_work_order_links")
    op.execute("DROP POLICY review_scope ON service_work_order_links")
    op.execute(
        "REVOKE UPDATE(dispatch_service_area_code,dispatch_required_skill_codes,dispatch_review_service_version,version) ON service_work_order_links FROM hydro_app"
    )
    op.execute("DROP FUNCTION hydro_dispatch_link_review()")
    op.drop_column("service_work_order_links", "dispatch_review_service_version")
    op.execute(
        "CREATE TRIGGER immutable_m07 BEFORE UPDATE OR DELETE ON service_work_order_links FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable()"
    )
