"""Proposed device identity and test-only one-time credential foundation."""

from alembic import op

revision = "pre_m10_004"
down_revision = "pre_m10_003"
branch_labels = None
depends_on = None


def upgrade():
    op.get_bind().exec_driver_sql("""
CREATE TABLE devices (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 organization_id uuid NOT NULL REFERENCES organizations(id),
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 serial_ref text NOT NULL CHECK(char_length(serial_ref) BETWEEN 1 AND 80),
 device_kind text NOT NULL CHECK(device_kind IN ('WATCH','GUARD5','EAR_PAIR','VIRTUAL')),
 origin_profile text NOT NULL CHECK(origin_profile IN ('LABORATORY','FIELD','SIMULATION')),
 supervision_capabilities jsonb NOT NULL DEFAULT '{"physical_provisioning":"NOT_APPROVED","health":"UNKNOWN"}',
 retired_at timestamptz,
 UNIQUE(organization_id,id), UNIQUE(organization_id,id,origin_profile),
 UNIQUE(organization_id,serial_ref),
 CHECK((device_kind='VIRTUAL')=(origin_profile='SIMULATION'))
);
CREATE TABLE device_provisioning_bindings (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 organization_id uuid NOT NULL,
 device_id uuid NOT NULL,
 environment text NOT NULL CHECK(environment IN ('LABORATORY','FIELD')),
 created_at timestamptz NOT NULL DEFAULT now(),
 review_reference text NOT NULL CHECK(char_length(review_reference) BETWEEN 10 AND 128),
 classification text NOT NULL CHECK(classification='SYNTHETIC_TEST_ONLY'),
 CHECK(left(current_database(),17)='hydro_disposable_'),
 FOREIGN KEY(organization_id,device_id,environment) REFERENCES devices(organization_id,id,origin_profile),
 UNIQUE(organization_id,device_id,id,environment)
);
CREATE TABLE device_credentials (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 organization_id uuid NOT NULL,
 device_id uuid NOT NULL,
 binding_id uuid NOT NULL,
 issued_by_id uuid NOT NULL,
 issuance_key uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 version bigint NOT NULL DEFAULT 1 CHECK(version>0),
 token_hash bytea NOT NULL UNIQUE CHECK(octet_length(token_hash)=32),
 allowed_environment text NOT NULL CHECK(allowed_environment IN ('LABORATORY','FIELD')),
 scope text NOT NULL DEFAULT 'SCALAR_TEST_ONLY' CHECK(scope='SCALAR_TEST_ONLY'),
 expires_at timestamptz NOT NULL CHECK(expires_at>created_at AND expires_at<=created_at+interval '30 days'),
 revoked_at timestamptz,
 FOREIGN KEY(organization_id,device_id,binding_id,allowed_environment)
 REFERENCES device_provisioning_bindings(organization_id,device_id,id,environment),
 UNIQUE(organization_id,id)
 ,FOREIGN KEY(organization_id,issued_by_id) REFERENCES organization_memberships(organization_id,id)
 ,UNIQUE(organization_id,issued_by_id,issuance_key)
);
CREATE FUNCTION hydro_fixed_device_profile() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF ROW(NEW.organization_id,NEW.device_kind,NEW.origin_profile,NEW.serial_ref,NEW.supervision_capabilities)
 IS DISTINCT FROM ROW(OLD.organization_id,OLD.device_kind,OLD.origin_profile,OLD.serial_ref,OLD.supervision_capabilities)
 THEN RAISE EXCEPTION 'device profile is immutable' USING ERRCODE='42501'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER immutable_device_profile BEFORE UPDATE ON devices
 FOR EACH ROW EXECUTE FUNCTION hydro_fixed_device_profile();
CREATE TRIGGER immutable_device_binding BEFORE UPDATE OR DELETE ON device_provisioning_bindings
 FOR EACH ROW EXECUTE FUNCTION hydro_history_immutable();
CREATE FUNCTION hydro_credential_revocation_only() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS DISTINCT FROM OLD.revoked_at
 THEN RAISE EXCEPTION 'credential revocation is permanent' USING ERRCODE='42501'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER permanent_device_revocation BEFORE UPDATE ON device_credentials
 FOR EACH ROW EXECUTE FUNCTION hydro_credential_revocation_only();
""")
    c = op.get_bind()
    for table in ("devices", "device_provisioning_bindings", "device_credentials"):
        c.exec_driver_sql(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        c.exec_driver_sql(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        c.exec_driver_sql(
            f"CREATE POLICY device_owner ON {table} TO hydro_migrator USING(true) WITH CHECK(true)"
        )
        allowed = "('ADMIN','ENGINEER','SUPERVISOR')" if table == "devices" else "('ADMIN')"
        condition = f"""organization_id::text=current_setting('hydro.organization_id',true)
AND EXISTS(SELECT 1 FROM organization_memberships m JOIN users u ON u.id=m.user_id
JOIN role_assignments a ON a.membership_id=m.id AND a.revoked_at IS NULL
JOIN roles r ON r.id=a.role_id WHERE m.organization_id={table}.organization_id
AND m.user_id::text=current_setting('hydro.user_id',true) AND m.status='ACTIVE'
AND u.deactivated_at IS NULL AND r.code IN {allowed})"""
        c.exec_driver_sql(
            f"CREATE POLICY device_read ON {table} FOR SELECT TO hydro_app USING({condition})"
        )
        if table != "device_provisioning_bindings":
            admin = condition.replace(allowed, "('ADMIN')")
            c.exec_driver_sql(
                f"CREATE POLICY device_insert ON {table} FOR INSERT TO hydro_app WITH CHECK({admin})"
            )
            if table == "device_credentials":
                c.exec_driver_sql(
                    f"CREATE POLICY credential_revoke ON {table} FOR UPDATE TO hydro_app USING({admin}) WITH CHECK({admin})"
                )
        c.exec_driver_sql(f"REVOKE ALL ON {table} FROM PUBLIC,hydro_app")
        c.exec_driver_sql(f"GRANT SELECT ON {table} TO hydro_app")
    c.exec_driver_sql(
        "GRANT INSERT(organization_id,serial_ref,device_kind,origin_profile) ON devices TO hydro_app"
    )
    c.exec_driver_sql(
        "GRANT INSERT(organization_id,device_id,binding_id,issued_by_id,issuance_key,token_hash,allowed_environment,expires_at) ON device_credentials TO hydro_app"
    )
    c.exec_driver_sql(
        "GRANT UPDATE(revoked_at,updated_at,version) ON device_credentials TO hydro_app"
    )
    from hydro.cli import seed_catalogue

    seed_catalogue(c)


def downgrade():
    c = op.get_bind()
    c.exec_driver_sql(
        "LOCK TABLE devices,device_credentials,device_provisioning_bindings IN ACCESS EXCLUSIVE MODE"
    )
    if any(
        c.exec_driver_sql(f"SELECT EXISTS(SELECT 1 FROM {table})").scalar_one()
        for table in ("devices", "device_credentials", "device_provisioning_bindings")
    ):
        raise RuntimeError(
            "Device identity or credential records exist; non-destructive downgrade refused"
        )
    op.drop_table("device_credentials")
    op.drop_table("device_provisioning_bindings")
    op.drop_table("devices")
    c.exec_driver_sql("DROP FUNCTION hydro_fixed_device_profile()")
    c.exec_driver_sql("DROP FUNCTION hydro_credential_revocation_only()")
