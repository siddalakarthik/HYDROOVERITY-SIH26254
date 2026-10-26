"""Parameterized synchronous Core repositories and transaction-local RLS scope."""

from typing import Any
from uuid import UUID

from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import Engine

from .config import Settings

MIGRATION_HEAD = "pre_m10_002"


def engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=settings.pool_size,
        max_overflow=0,
        pool_timeout=3,
        connect_args={"connect_timeout": 3, "options": "-c statement_timeout=5000"},
        hide_parameters=True,
    )


def query(connection: Connection, sql: str, **values: Any) -> list[dict[str, Any]]:
    return [dict(r) for r in connection.execute(text(sql), values).mappings()]


def one(connection: Connection, sql: str, **values: Any) -> dict[str, Any] | None:
    rows = query(connection, sql, **values)
    return rows[0] if rows else None


def execute(connection: Connection, sql: str, **values: Any) -> None:
    connection.execute(text(sql), values)


def context(
    c: Connection, user_id: UUID | str | None = None, organization_id: UUID | str | None = None
) -> None:
    execute(
        c,
        "SELECT set_config('hydro.user_id', :u, true), "
        "set_config('hydro.organization_id', :o, true)",
        u=str(user_id or ""),
        o=str(organization_id or ""),
    )


def principal_is_safe(c: Connection) -> bool:
    row = one(
        c,
        "SELECT NOT rolsuper AND NOT rolbypassrls AND "
        "NOT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public' "
        "AND tableowner=current_user) AS safe FROM pg_roles WHERE rolname=current_user",
    )
    return bool(row and row["safe"])
