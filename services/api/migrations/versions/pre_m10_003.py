"""Durable opaque event cursors; read access follows the current session/member."""

from alembic import op

revision = "pre_m10_003"
down_revision = "pre_m10_002"
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().exec_driver_sql("""
CREATE TABLE realtime_cursors (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 organization_id uuid NOT NULL REFERENCES organizations(id),
 membership_id uuid NOT NULL,
 session_id uuid NOT NULL REFERENCES sessions(id),
 created_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL DEFAULT now()+interval '168 hours',
 token_hash bytea NOT NULL UNIQUE CHECK(octet_length(token_hash)=32),
 revoked_at timestamptz,
 position bigint NOT NULL CHECK(position>=0),
 workspace_mode text NOT NULL CHECK(workspace_mode IN ('OPERATIONAL','SIMULATION')),
 permission_fingerprint text NOT NULL CHECK(char_length(permission_fingerprint)=64),
 FOREIGN KEY(organization_id,membership_id) REFERENCES organization_memberships(organization_id,id),
 UNIQUE(organization_id,membership_id,session_id,workspace_mode,permission_fingerprint,position),
 CHECK(expires_at>created_at AND expires_at<=created_at+interval '168 hours')
);
CREATE INDEX realtime_cursor_expiry ON realtime_cursors(expires_at);
ALTER TABLE realtime_cursors ENABLE ROW LEVEL SECURITY;
ALTER TABLE realtime_cursors FORCE ROW LEVEL SECURITY;
CREATE POLICY realtime_owner ON realtime_cursors TO hydro_migrator USING(true) WITH CHECK(true);
CREATE POLICY realtime_current ON realtime_cursors TO hydro_app
 USING(organization_id::text=current_setting('hydro.organization_id',true)
 AND session_id::text=current_setting('hydro.session_id',true)
 AND EXISTS(SELECT 1 FROM organization_memberships m JOIN sessions s ON s.user_id=m.user_id
 JOIN users u ON u.id=m.user_id AND u.deactivated_at IS NULL
 WHERE m.id=membership_id AND m.organization_id=realtime_cursors.organization_id
 AND m.user_id::text=current_setting('hydro.user_id',true) AND m.status='ACTIVE'
 AND s.id=session_id AND s.revoked_at IS NULL AND s.absolute_expires_at>now() AND s.idle_expires_at>now()))
 WITH CHECK(organization_id::text=current_setting('hydro.organization_id',true)
 AND session_id::text=current_setting('hydro.session_id',true)
 AND EXISTS(SELECT 1 FROM organization_memberships m JOIN sessions s ON s.user_id=m.user_id
 JOIN users u ON u.id=m.user_id AND u.deactivated_at IS NULL
 WHERE m.id=membership_id AND m.organization_id=realtime_cursors.organization_id
 AND m.user_id::text=current_setting('hydro.user_id',true) AND m.status='ACTIVE'
 AND s.id=session_id AND s.revoked_at IS NULL AND s.absolute_expires_at>now() AND s.idle_expires_at>now()));
REVOKE ALL ON realtime_cursors FROM PUBLIC,hydro_app;
GRANT SELECT,INSERT,UPDATE ON realtime_cursors TO hydro_app;
""")
    from hydro.cli import seed_catalogue

    seed_catalogue(op.get_bind())


def downgrade():
    connection = op.get_bind()
    connection.exec_driver_sql("LOCK TABLE realtime_cursors IN ACCESS EXCLUSIVE MODE")
    if connection.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM realtime_cursors)").scalar_one():
        raise RuntimeError("Replay cursors exist; non-destructive downgrade refused")
    op.drop_table("realtime_cursors")
    # Retain an already granted permission rather than revoke a reviewed role grant.
