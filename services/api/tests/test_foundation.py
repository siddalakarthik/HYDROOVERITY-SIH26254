from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
import pytest

from hydro.db import context, one, principal_is_safe
from hydro.repository import insert


def test_actual_postgres_postgis_and_readiness(env):
    with env['app'].state.engine.begin() as c:
        assert principal_is_safe(c)
        assert int(one(c,"SHOW server_version_num")['server_version_num'])>=170000
        assert one(c,'SELECT postgis_version() AS version')['version'].startswith('3.')
        assert one(c,'SELECT version_num FROM alembic_version')['version_num']=='m03_001'
    client=env['client']()
    assert client.request('GET','/internal/health/live').status_code==200
    assert client.request('GET','/internal/health/ready').status_code==200


def test_rls_blocks_cross_tenant_and_pool_context_clears(env):
    engine=env['app'].state.engine
    with engine.begin() as c:
        context(c,organization_id=env['org']['id'])
        rows=c.execute(text('SELECT organization_id FROM organization_memberships')).all()
        assert rows and all(r[0]==env['org']['id'] for r in rows)
        assert one(c,'SELECT id FROM organization_memberships WHERE organization_id=:o',o=env['other']['id']) is None
    with engine.begin() as c:
        assert not c.execute(text('SELECT id FROM organization_memberships')).all()
    with pytest.raises(DBAPIError):
        with engine.begin() as c:
            context(c,organization_id=env['org']['id'])
            insert(c,'water_zones',organization_id=env['other']['id'],name='Must fail',demand_boundary_version='synthetic-v1',demand_accounting={},topology_quality='UNVERIFIED')


def test_same_tenant_fk_and_immutable_history(env):
    with pytest.raises(DBAPIError):
        with env['owner'].begin() as c:
            insert(c,'role_assignments',organization_id=env['org']['id'],membership_id=env['other_admin']['id'],role_id=one(c,"SELECT id FROM roles WHERE code='TECHNICIAN'")['id'],granted_by_id=env['admin']['id'])
    with pytest.raises(DBAPIError):
        with env['app'].state.engine.begin() as c:
            context(c,organization_id=env['org']['id'])
            c.exec_driver_sql("UPDATE audit_logs SET action='forbidden'")


