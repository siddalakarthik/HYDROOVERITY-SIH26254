"""Bind only implemented operations to their actual persistent services."""

import json

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from .contracts import DESIGN, OPERATIONS, runtime_openapi
from .dispatch import dispatch
from .errors import Problem, require


def endpoint(app, op):
    async def handle(request: Request):
        spec = DESIGN["paths"][op["path"]][op["method"]]
        allowed = {p["name"] for p in spec.get("parameters", []) if p["in"] == "query"}
        require(
            set(request.query_params) <= allowed,
            422,
            "INVALID_FILTER",
            "Unknown or unauthorized query parameter",
        )
        require(
            len(request.query_params.multi_items()) == len(request.query_params),
            422,
            "DUPLICATE_FILTER",
            "Duplicate query parameters are not accepted",
        )
        payload = bytearray()
        async for chunk in request.stream():
            payload.extend(chunk)
            require(
                len(payload) <= 16384, 413, "BODY_TOO_LARGE", "Request body exceeds the M03 limit"
            )
        value = None
        if payload:
            require(
                request.headers.get("content-type", "").split(";")[0] == "application/json",
                422,
                "JSON_REQUIRED",
                "JSON request body required",
            )
            try:
                value = json.loads(
                    payload, parse_constant=lambda _: (_ for _ in ()).throw(ValueError())
                )
            except (ValueError, UnicodeDecodeError):
                raise Problem(400, "INVALID_JSON", "Malformed JSON request")
        result, status, headers = await run_in_threadpool(
            dispatch, app, request, op, value, dict(request.path_params)
        )
        response = JSONResponse(result, status_code=status)
        for key, value in headers.raw_headers:
            if key.lower() not in {b"content-length", b"content-type"}:
                response.raw_headers.append((key, value))
        return response

    handle.__name__ = op["id"]
    return handle


def bind_routes(app):
    for op in OPERATIONS:
        app.add_api_route(
            "/api/v1" + op["path"],
            endpoint(app, op),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    @app.get("/internal/openapi.json", include_in_schema=False)
    def development_contract():
        return runtime_openapi()
