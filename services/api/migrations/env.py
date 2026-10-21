"""Only the explicit migration URL is accepted; runtime credentials cannot migrate."""

import os

from alembic import context
from sqlalchemy import create_engine

with create_engine(os.environ["HYDRO_MIGRATION_URL"], hide_parameters=True).connect() as connection:
    context.configure(connection=connection, transactional_ddl=True)
    with context.begin_transaction():
        context.run_migrations()
