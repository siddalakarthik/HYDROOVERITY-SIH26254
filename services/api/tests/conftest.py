"""Disposable PostgreSQL only. Never infer permission to erase an unknown DB."""
import asyncio
import os
import secrets
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine

from hydro.cli import bootstrap
from hydro.config import Settings
from hydro.db import one
from hydro.main import create_app
from hydro.repository import TABLES


class Client:
    def __init__(self, app):
        self.runner=asyncio.Runner()
        self.http=httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url=app.state.settings.origin)
        self.origin=app.state.settings.origin

    def request(self, method, path, **kwargs):
        headers=kwargs.pop('headers',{})
        if method.lower() not in {'get','head'}:
            csrf=self.request('GET','/api/v1/auth/csrf')
            assert csrf.status_code==200, 'CSRF bootstrap failed'
            headers={'Origin':self.origin,'X-CSRF-Token':csrf.json()['csrf_token'],**headers}
        return self.runner.run(self.http.request(method,path,headers=headers,**kwargs))

    def raw(self,method,path,**kwargs):
        return self.runner.run(self.http.request(method,path,**kwargs))

    def close(self):
        self.runner.run(self.http.aclose());self.runner.close()


@pytest.fixture
def env(tmp_path):
    owner_url=os.environ.get('HYDRO_TEST_OWNER_URL')
    runtime_url=os.environ.get('HYDRO_TEST_RUNTIME_URL')
    confirmed=os.environ.get('HYDRO_TEST_DATABASE_CONFIRM')
    if not owner_url or not runtime_url or not confirmed:
        pytest.fail('Real PostgreSQL test URLs and explicit disposable database confirmation are required',pytrace=False)
    owner=create_engine(owner_url,hide_parameters=True,connect_args={'connect_timeout':3,'options':'-c lock_timeout=5000 -c statement_timeout=10000'})
    with owner.begin() as c:
        database=one(c,'SELECT current_database() AS name')['name']
        assert database==confirmed and database.startswith('hydro_disposable_'), 'Refusing to reset an unconfirmed database'
        c.exec_driver_sql('TRUNCATE '+','.join(sorted(TABLES))+' RESTART IDENTITY CASCADE')
        password=secrets.token_urlsafe(24)
        org,admin,_=bootstrap(c,confirmed_database=confirmed,slug='synthetic-utility-a',name='SYNTHETIC integration utility A',email='admin-a@example.invalid',display_name='Synthetic administrator A',password=password,reporting_enabled=True)
        other,other_admin,_=bootstrap(c,confirmed_database=confirmed,slug='synthetic-utility-b',name='SYNTHETIC integration utility B',email='admin-b@example.invalid',display_name='Synthetic administrator B',password=password,reporting_enabled=True)
    settings=Settings(database_url=runtime_url,hmac_key=secrets.token_urlsafe(48),mail_directory=tmp_path/'private-mail')
    app=create_app(settings)
    clients=[]
    def client():
        obj=Client(app);clients.append(obj);return obj
    yield {'app':app,'owner':owner,'settings':settings,'org':org,'admin':admin,'other':other,'other_admin':other_admin,'password':password,'client':client}
    for obj in clients:obj.close()
    app.state.engine.dispose();owner.dispose()
