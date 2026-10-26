"""Proposed identities and non-redisclosing credentials; no physical activation."""

import base64
import copy
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Response
from fastapi.encoders import jsonable_encoder

from .auth import Auth
from .contracts import DESIGN, INVENTORY, validator
from .db import MIGRATION_HEAD, execute, one, principal_is_safe, query
from .errors import Problem, require
from .events import record
from .security import now, secret, verifier
from .tenant import Tenant

PATHS = {
    "/orgs/{organization_id}/devices",
    "/orgs/{organization_id}/devices/{device_id}",
    "/orgs/{organization_id}/devices/{device_id}/credentials",
    "/orgs/{organization_id}/devices/{device_id}/credentials/{credential_id}",
}
OPERATIONS = [o for o in INVENTORY if o["path"] in PATHS]


def extend_openapi(spec):
    for op in OPERATIONS:
        spec["paths"].setdefault(op["path"], {})[op["method"]] = copy.deepcopy(
            DESIGN["paths"][op["path"]][op["method"]]
        )
    pending = [spec["paths"][path] for path in PATHS]
    seen = set()
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            reference = value.get("$ref", "")
            if reference.startswith("#/components/") and reference not in seen:
                seen.add(reference)
                _, _, kind, name = reference.split("/")
                target = DESIGN["components"][kind][name]
                spec["components"].setdefault(kind, {}).setdefault(name, copy.deepcopy(target))
                pending.append(target)
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    return spec


def view(row):
    return {
        "id": row["id"],
        "serial_ref": row["serial_ref"],
        "device_kind": row["device_kind"],
        "environment": row["origin_profile"],
        "health": "UNKNOWN",
        "version": row["version"],
    }


def dispatch(app, request, op, body, params):
    response = Response()
    method, path = op["method"], op["path"]
    if op["request"]:
        require(
            not list(validator(op["request"]).iter_errors(body)),
            422,
            "INVALID_BODY",
            "Body does not match the device contract",
        )
    else:
        require(body is None, 422, "UNEXPECTED_BODY", "This operation accepts no body")
    status = 200
    with app.state.engine.begin() as c:
        require(principal_is_safe(c), 503, "UNSAFE_DATABASE_PRINCIPAL", "Unsafe runtime identity")
        require(
            one(c, "SELECT version_num FROM alembic_version")["version_num"] == MIGRATION_HEAD,
            503,
            "MIGRATION_REQUIRED",
            "Database migration is required",
        )
        auth = Auth(c, request, response, app)
        auth.identify()
        auth.authenticated()
        try:
            params = {key: str(UUID(value)) for key, value in params.items()}
        except ValueError:
            require(False, 422, "INVALID_IDENTIFIER", "Invalid device reference")
        execute(
            c,
            "SELECT pg_advisory_xact_lock(hashtextextended(:key,0))",
            key="hydro-dispatch:" + str(params["organization_id"]),
        )
        tenant = Tenant(auth, op, params)
        device = None
        if "device_id" in params:
            device = one(
                c,
                "SELECT * FROM devices WHERE organization_id=:o AND id=:i",
                o=tenant.organization_id,
                i=params["device_id"],
            )
            require(device, 404, "NOT_FOUND", "Resource unavailable")
        credential = None
        if "credential_id" in params:
            credential = one(
                c,
                "SELECT * FROM device_credentials WHERE organization_id=:o AND device_id=:d AND id=:i FOR UPDATE",
                o=tenant.organization_id,
                d=device["id"],
                i=params["credential_id"],
            )
            require(credential, 404, "NOT_FOUND", "Resource unavailable")
        if method == "get":
            if device:
                result = view(device)
                response.headers["ETag"] = f'"{device["version"]}"'
            else:
                result = devices_page(c, request, tenant)
        else:
            auth.csrf()
            require(
                auth.session["reauthenticated_at"]
                and (now() - auth.session["reauthenticated_at"]).total_seconds() <= 600,
                403,
                "REAUTHENTICATE",
                "Authenticate again before device governance",
            )
            app.state.limits.hit("device-governance", str(tenant.member_id), 10, 60)
            try:
                key = UUID(request.headers.get("idempotency-key", ""))
            except ValueError:
                require(False, 400, "IDEMPOTENCY_REQUIRED", "A UUID Idempotency-Key is required")
            issue = path.endswith("/credentials")
            binding = None
            if issue:
                require(device["retired_at"] is None, 409, "DEVICE_RETIRED", "Device is retired")
                require(
                    body["environment"] == device["origin_profile"],
                    422,
                    "PROFILE_MISMATCH",
                    "Credential must match the fixed device profile",
                )
                binding = one(
                    c,
                    "SELECT * FROM device_provisioning_bindings WHERE organization_id=:o AND device_id=:d AND environment=:e ORDER BY created_at DESC,id DESC LIMIT 1",
                    o=tenant.organization_id,
                    d=device["id"],
                    e=body["environment"],
                )
                require(
                    binding
                    and binding["classification"] == "SYNTHETIC_TEST_ONLY"
                    and one(c, "SELECT current_database() AS name")["name"].startswith(
                        "hydro_disposable_"
                    ),
                    503,
                    "PHYSICAL_PROVISIONING_NOT_APPROVED",
                    "Credential issuance requires an independently reviewed physical binding; synthetic test bindings do not authorize field hardware",
                )
                require(
                    not one(
                        c,
                        "SELECT id FROM device_credentials WHERE organization_id=:o AND issued_by_id=:a AND issuance_key=:k",
                        o=tenant.organization_id,
                        a=tenant.member_id,
                        k=key,
                    ),
                    409,
                    "CREDENTIAL_NOT_REDISCLOSED",
                    "A credential cannot be redisclosed; revoke and issue with a new key",
                )
            actor = str(tenant.member_id)
            fingerprint = hashlib.sha256(
                json.dumps(
                    {"body": body, "path": {k: str(v) for k, v in params.items()}},
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode()
            ).hexdigest()
            prior = one(
                c,
                "SELECT * FROM idempotency_records WHERE organization_id=:o AND actor_scope=:a AND method=:m AND route_template=:r AND operation_key=:k",
                o=tenant.organization_id,
                a=actor,
                m=method,
                r=path,
                k=key,
            )
            if prior:
                require(
                    prior["request_hash"] == fingerprint,
                    409,
                    "IDEMPOTENCY_CONFLICT",
                    "Key was used with different content",
                )
                require(
                    not issue,
                    409,
                    "CREDENTIAL_NOT_REDISCLOSED",
                    "A credential cannot be redisclosed; revoke and issue with a new key",
                )
                if credential:
                    result = {"message": "Credential revoked"}
                else:
                    row = one(
                        c,
                        "SELECT * FROM devices WHERE id=:i AND organization_id=:o",
                        i=prior["result_resource_id"],
                        o=tenant.organization_id,
                    )
                    require(row, 404, "NOT_FOUND", "Resource unavailable")
                    result = view(row)
                status = prior["result_status"]
            else:
                if credential:
                    row = one(
                        c,
                        "UPDATE device_credentials SET revoked_at=coalesce(revoked_at,now()),updated_at=now(),version=version+1 WHERE id=:i RETURNING id",
                        i=credential["id"],
                    )
                    result = {"message": "Credential revoked"}
                elif issue:
                    expires = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
                    created = one(c, "SELECT now() AS stamp")["stamp"]
                    require(
                        created < expires <= created + timedelta(days=30),
                        422,
                        "INVALID_EXPIRY",
                        "Credential expiry must be future and within 30 days",
                    )
                    raw = secret()
                    row = one(
                        c,
                        "INSERT INTO device_credentials(organization_id,device_id,binding_id,issued_by_id,issuance_key,token_hash,allowed_environment,expires_at) VALUES(:o,:d,:b,:a,:k,:h,:e,:x) RETURNING id,expires_at",
                        o=tenant.organization_id,
                        d=device["id"],
                        b=binding["id"],
                        a=tenant.member_id,
                        k=key,
                        h=verifier(raw),
                        e=device["origin_profile"],
                        x=expires,
                    )
                    result = {
                        "id": row["id"],
                        "expires_at": row["expires_at"],
                        "one_time_secret": raw,
                    }
                    status = 201
                else:
                    serial = body["serial_ref"].strip()
                    require(
                        serial and "\x00" not in serial,
                        422,
                        "INVALID_DEVICE",
                        "Nonempty device reference required",
                    )
                    require(
                        (body["device_kind"] == "VIRTUAL")
                        == (body["provisioning_environment"] == "SIMULATION")
                        and body["provisioning_environment"] != "MANUAL",
                        422,
                        "PROFILE_MISMATCH",
                        "Physical and virtual device profiles must remain distinct",
                    )
                    row = one(
                        c,
                        "INSERT INTO devices(organization_id,serial_ref,device_kind,origin_profile) VALUES(:o,:s,:k,:e) RETURNING *",
                        o=tenant.organization_id,
                        s=serial,
                        k=body["device_kind"],
                        e=body["provisioning_environment"],
                    )
                    result, status = view(row), 201
                resource_table = "device_credentials" if (issue or credential) else "devices"
                record(
                    c,
                    tenant.organization_id,
                    tenant.member_id,
                    op["id"],
                    resource_table,
                    row["id"],
                    request.state.request_id,
                    op["permission"],
                )
                execute(
                    c,
                    "INSERT INTO idempotency_records(organization_id,actor_scope,operation_key,method,route_template,request_hash,result_resource_id,result_status,expires_at) VALUES(:o,:a,:k,:m,:r,:h,:i,:s,now()+interval '7 days')",
                    o=tenant.organization_id,
                    a=actor,
                    k=key,
                    m=method,
                    r=path,
                    h=fingerprint,
                    i=row["id"],
                    s=status,
                )
        wire = jsonable_encoder(result)
        response_name = "Page_" + op["response"] if op.get("list") else op["response"]
        require(
            not list(validator(response_name).iter_errors(wire)),
            500,
            "RESPONSE_CONTRACT",
            "Device projection failed validation",
        )
    return wire, status, response


def devices_page(c, request, tenant):
    params = dict(request.query_params)
    try:
        limit = int(params.get("limit", "50"))
    except ValueError:
        require(False, 422, "INVALID_LIMIT", "Invalid page limit")
    require(1 <= limit <= 100, 422, "INVALID_LIMIT", "Invalid page limit")
    stamp = now()
    conditions, values = ["organization_id=:o"], {"o": tenant.organization_id, "n": limit + 1}
    filters = {key: value for key, value in params.items() if key not in {"cursor", "limit"}}
    scope = hashlib.sha256(
        json.dumps(
            [str(tenant.organization_id), str(tenant.member_id), sorted(tenant.roles), filters],
            sort_keys=True,
        ).encode()
    ).hexdigest()
    signing_key = tenant.auth.app.state.settings.hmac_key.get_secret_value().encode()
    if params.get("cursor"):
        try:
            raw, signature = params["cursor"].split(".")
            require(
                hmac.compare_digest(
                    signature, hmac.new(signing_key, raw.encode(), "sha256").hexdigest()
                )
            )
            decoded = json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
            require(decoded["scope"] == scope)
            stamp = datetime.fromisoformat(decoded["as_of"])
            require(stamp.tzinfo and timedelta(0) <= now() - stamp <= timedelta(days=1))
            values.update(
                after_time=datetime.fromisoformat(decoded["time"]), after_id=UUID(decoded["id"])
            )
            conditions.append("(created_at,id)<(:after_time,:after_id)")
        except (ValueError, KeyError, TypeError, Problem):
            raise Problem(
                422, "INVALID_CURSOR", "Device cursor is invalid for this scope"
            ) from None
    values["as_of"] = stamp
    conditions.append("created_at<=:as_of")
    if "health" in params:
        require(
            params["health"] == "UNKNOWN",
            422,
            "UNKNOWN_HEALTH",
            "Physical health is not established",
        )
    if "environment" in params:
        require(
            params["environment"] in {"LABORATORY", "FIELD", "SIMULATION"},
            422,
            "INVALID_FILTER",
            "Invalid acquisition environment",
        )
        conditions.append("origin_profile=:e")
        values["e"] = params["environment"]
    rows = query(
        c,
        "SELECT * FROM devices WHERE "
        + " AND ".join(conditions)
        + " ORDER BY created_at DESC,id DESC LIMIT :n",
        **values,
    )
    cursor = None
    if len(rows) > limit:
        last = rows[limit - 1]
        raw = (
            base64.urlsafe_b64encode(
                json.dumps(
                    {
                        "scope": scope,
                        "as_of": stamp.isoformat(),
                        "time": last["created_at"].isoformat(),
                        "id": str(last["id"]),
                    },
                    separators=(",", ":"),
                ).encode()
            )
            .decode()
            .rstrip("=")
        )
        cursor = raw + "." + hmac.new(signing_key, raw.encode(), "sha256").hexdigest()
    return {"items": [view(row) for row in rows[:limit]], "next_cursor": cursor, "as_of": stamp}
