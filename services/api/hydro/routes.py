"""Bind only implemented operations to their actual persistent services."""

import json

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool

from .contracts import DESIGN, OPERATIONS, runtime_openapi
from .dispatch import dispatch
from .errors import Problem, require


def endpoint(app, op, design=DESIGN, dispatcher=dispatch, body_limit=16384):
    async def handle(request: Request):
        spec = design["paths"][op["path"]][op["method"]]
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
                len(payload) <= body_limit,
                413,
                "BODY_TOO_LARGE",
                "Request body exceeds the operation limit",
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
            dispatcher, app, request, op, value, dict(request.path_params)
        )
        response = JSONResponse(result, status_code=status)
        for key, value in headers.raw_headers:
            if key.lower() not in {b"content-length", b"content-type"}:
                response.raw_headers.append((key, value))
        return response

    handle.__name__ = op["id"]
    return handle


def science_endpoint(app, op, design, dispatcher):
    ordinary = endpoint(app, op, design, dispatcher)
    if op["id"] != "m06_stream":
        return ordinary

    async def stream(request: Request):
        # Bounded replay batch; every reconnect repeats current session/tenant
        # authorization. It is not a live sensor feed or a long-lived grant.
        result = await ordinary(request)
        page = json.loads(result.body)
        chunks = [
            "event: provenance\ndata: "
            + json.dumps({k: v for k, v in page.items() if k != "items"})
            + "\n\n"
        ]
        chunks.extend(
            "id: "
            + str(item["sequence"])
            + "\nevent: observation\ndata: "
            + json.dumps(item)
            + "\n\n"
            for item in page["items"]
        )
        chunks.append(
            "event: checkpoint\ndata: "
            + json.dumps({"next_offset": page["next_offset"], "source_category": "SIMULATION"})
            + "\n\n"
        )
        response = StreamingResponse(iter(chunks), media_type="text/event-stream")
        for key, value in result.raw_headers:
            if key.lower() not in {b"content-length", b"content-type"}:
                response.raw_headers.append((key, value))
        return response

    return stream


def bind_routes(app):
    for op in OPERATIONS:
        app.add_api_route(
            "/api/v1" + op["path"],
            endpoint(app, op),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    from .service_contracts import DESIGN as service_design
    from .service_contracts import OPERATIONS as service_operations
    from .services.service_requests import dispatch as service_dispatch

    for op in service_operations:
        app.add_api_route(
            "/api/v1" + op["path"],
            endpoint(app, op, service_design, service_dispatch),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    from .science_contracts import OPERATIONS as science_operations
    from .science_contracts import extend_openapi
    from .services.science import dispatch as science_dispatch

    science_design = extend_openapi({"paths": {}, "components": {"schemas": {}}})
    for op in science_operations:
        app.add_api_route(
            "/api/v1" + op["path"],
            science_endpoint(app, op, science_design, science_dispatch),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    from .scheduling_contracts import DESIGN as scheduling_design
    from .scheduling_contracts import OPERATIONS as scheduling_operations
    from .services.scheduling import dispatch as scheduling_dispatch

    for op in scheduling_operations:
        app.add_api_route(
            "/api/v1" + op["path"],
            endpoint(app, op, scheduling_design, scheduling_dispatch),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    from .communications_contracts import DESIGN as communications_design
    from .communications_contracts import OPERATIONS as communications_operations
    from .services.communications import dispatch as communications_dispatch

    for op in communications_operations:
        app.add_api_route(
            "/api/v1" + op["path"],
            endpoint(app, op, communications_design, communications_dispatch),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    from .project_contact import OPERATIONS as contact_operations
    from .project_contact import dispatch as contact_dispatch

    for op in contact_operations:
        app.add_api_route(
            "/api/v1" + op["path"],
            endpoint(app, op, DESIGN, contact_dispatch, body_limit=8192),
            methods=[op["method"].upper()],
            operation_id=op["id"],
            include_in_schema=False,
        )

    from .realtime import bind as bind_realtime

    bind_realtime(app)

    @app.get("/internal/openapi.json", include_in_schema=False)
    def development_contract():
        return runtime_openapi()
