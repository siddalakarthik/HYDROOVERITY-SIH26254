"""Application factory; development is private and database readiness is genuine."""

import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError, TimeoutError
from starlette.exceptions import HTTPException

from .config import Settings
from .db import MIGRATION_HEAD, engine, one, principal_is_safe
from .errors import Problem

LOG = logging.getLogger("hydro.security")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    application = FastAPI(title="HYDROOVERITY", docs_url=None, redoc_url=None, openapi_url=None)
    application.state.settings = settings
    application.state.engine = engine(settings)
    from .security import Limits, PrivateMail

    application.state.limits = Limits(settings.hmac_key.get_secret_value())
    application.state.mail = PrivateMail(settings.mail_directory)

    @application.middleware("http")
    async def boundary(request: Request, call_next):
        request.state.request_id = str(uuid4())
        started = time.monotonic()
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        # No URL/path IDs, query, cookie, user email, body, SQL, IP or token.
        LOG.info(
            "request id=%s method=%s status=%d elapsed_ms=%d",
            request.state.request_id,
            request.method,
            response.status_code,
            int((time.monotonic() - started) * 1000),
        )
        return response

    @application.exception_handler(Problem)
    async def safe_problem(request: Request, exc: Problem):
        headers = {"Cache-Control": "no-store", "X-Request-ID": request.state.request_id}
        if exc.status in {429, 503}:
            headers["Retry-After"] = "60"
        return JSONResponse(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request.state.request_id,
                    "field_errors": [],
                }
            },
            status_code=exc.status,
            headers=headers,
        )

    @application.exception_handler(IntegrityError)
    async def constraint_problem(request: Request, exc: IntegrityError):
        return await safe_problem(request, Problem(409, "CONFLICT", "Conflicting persisted state"))

    @application.exception_handler(HTTPException)
    async def routing_problem(request: Request, exc: HTTPException):
        return await safe_problem(
            request,
            Problem(
                exc.status_code,
                "NOT_FOUND" if exc.status_code == 404 else "INVALID_REQUEST",
                "Resource or operation unavailable",
            ),
        )

    @application.exception_handler(Exception)
    async def unexpected_problem(request: Request, exc: Exception):
        LOG.error("internal_failure id=%s", request.state.request_id)
        return await safe_problem(
            request,
            Problem(500, "INTERNAL_ERROR", "Unexpected server error; use request ID for support"),
        )

    @application.exception_handler(DBAPIError)
    @application.exception_handler(TimeoutError)
    async def database_problem(request: Request, exc: Exception):
        return await safe_problem(
            request, Problem(503, "UNAVAILABLE", "Persistence temporarily unavailable")
        )

    @application.get("/internal/health/live", include_in_schema=False)
    def live():
        return {"status": "alive"}

    @application.get("/internal/health/ready", include_in_schema=False)
    def ready():
        try:
            with application.state.engine.begin() as c:
                row = one(c, "SELECT version_num FROM alembic_version")
                ok = bool(row and row["version_num"] == MIGRATION_HEAD and principal_is_safe(c))
        except Exception:
            ok = False
        return JSONResponse(
            {"status": "ready" if ok else "unavailable"}, status_code=200 if ok else 503
        )

    from .routes import bind_routes

    bind_routes(application)
    return application
