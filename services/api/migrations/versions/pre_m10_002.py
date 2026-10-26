"""Fixed project inbox; runtime cannot retrieve contact content or select its owner."""

from alembic import op

revision = "pre_m10_002"
down_revision = "pre_m10_001"
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().exec_driver_sql("""
CREATE TABLE project_contact_submissions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 category text NOT NULL CHECK(category IN ('QUESTION','FEEDBACK')),
 message text NOT NULL CHECK(char_length(message) BETWEEN 10 AND 2000),
 reply_email text CHECK(char_length(reply_email)<=254),
 status text NOT NULL DEFAULT 'NEW' CHECK(status IN ('NEW','REVIEWED')),
 expires_at timestamptz NOT NULL DEFAULT now()+interval '720 hours',
 hold_reference text CHECK(char_length(hold_reference) BETWEEN 10 AND 128),
 capacity_marker smallint NOT NULL DEFAULT 1 CHECK(capacity_marker=1),
 CHECK(expires_at=created_at+interval '720 hours')
);
CREATE INDEX contact_expiry ON project_contact_submissions(expires_at);
CREATE INDEX contact_review ON project_contact_submissions(status,created_at);
ALTER TABLE project_contact_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_contact_submissions FORCE ROW LEVEL SECURITY;
CREATE POLICY contact_owner ON project_contact_submissions TO hydro_migrator
 USING(true) WITH CHECK(true);
CREATE POLICY contact_capacity_read ON project_contact_submissions FOR SELECT TO hydro_app USING(true);
CREATE POLICY contact_intake ON project_contact_submissions FOR INSERT TO hydro_app
 WITH CHECK(left(current_database(),17)='hydro_disposable_'
 AND status='NEW' AND version=1 AND hold_reference IS NULL);
REVOKE ALL ON project_contact_submissions FROM PUBLIC,hydro_app;
GRANT INSERT(category,message,reply_email) ON project_contact_submissions TO hydro_app;
GRANT SELECT(capacity_marker) ON project_contact_submissions TO hydro_app;

CREATE TABLE project_contact_operator_audit (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 created_at timestamptz NOT NULL DEFAULT now(),
 database_role text NOT NULL DEFAULT current_user,
 contact_id uuid NOT NULL,
 operator_reference text NOT NULL CHECK(char_length(operator_reference) BETWEEN 10 AND 128),
 action text NOT NULL CHECK(action IN ('READ','REVIEW','HOLD','RELEASE_HOLD','PURGE')),
 policy_reference text NOT NULL CHECK(char_length(policy_reference) BETWEEN 10 AND 128)
);
ALTER TABLE project_contact_operator_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_contact_operator_audit FORCE ROW LEVEL SECURITY;
CREATE POLICY contact_audit_owner ON project_contact_operator_audit TO hydro_migrator
 USING(true) WITH CHECK(true);
REVOKE ALL ON project_contact_operator_audit FROM PUBLIC,hydro_app;
CREATE TRIGGER immutable_contact_operator_audit BEFORE UPDATE OR DELETE ON project_contact_operator_audit
 FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
""")


def downgrade():
    connection = op.get_bind()
    connection.exec_driver_sql(
        "LOCK TABLE project_contact_submissions,project_contact_operator_audit IN ACCESS EXCLUSIVE MODE"
    )
    populated = connection.exec_driver_sql(
        "SELECT EXISTS(SELECT 1 FROM project_contact_submissions) OR "
        "EXISTS(SELECT 1 FROM project_contact_operator_audit)"
    ).scalar_one()
    if populated:
        raise RuntimeError(
            "Project contact data or audit exists; non-destructive downgrade refused"
        )
    op.drop_table("project_contact_operator_audit")
    op.drop_table("project_contact_submissions")
