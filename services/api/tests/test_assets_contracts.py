"""PostGIS persistence, manual evidence, all-route contract guards and pagination."""

from uuid import uuid4

from helpers import expect, login, mutate
from test_workflow import complaint_body, incident, setup

from hydro.contracts import DESIGN, OPERATIONS
from hydro.db import one


def test_postgis_assets_geodesic_length_versions_and_spatial_integrity(env):
    f = setup(env)
    base = f["base"]
    engineer = f["engineer"]
    zone = f["zone"]
    expect(engineer.request("GET", base + "/zones"), 200)
    original = engineer.request("GET", base + "/zones/" + zone["id"])
    expect(original, 200)
    body = {
        "name": "SYNTHETIC renamed service area",
        "demand_boundary_version": "synthetic-v2",
        "demand_accounting": {
            "outflow_includes_customer_demand": True,
            "storage_observed": False,
            "notes": "No measured boundary observations",
        },
    }
    expect(
        mutate(
            engineer,
            base + "/zones/" + zone["id"],
            body,
            version=int(original.headers["etag"].strip('"')),
            method="PATCH",
        ),
        200,
    )

    def junction(name, point):
        return {
            "zone_id": zone["id"],
            "external_ref": name,
            "geometry": {"type": "Point", "coordinates": point},
            "topology_quality": "UNVERIFIED",
        }

    first = expect(
        mutate(engineer, base + "/junctions", junction("SYNTHETIC-A", [78.0, 17.0])), 201
    )
    second = expect(
        mutate(engineer, base + "/junctions", junction("SYNTHETIC-B", [78.0001, 17.0])), 201
    )
    expect(engineer.request("GET", base + "/junctions?bbox=77.9,16.9,78.1,17.1"), 200)
    detail = engineer.request("GET", base + "/junctions/" + first["id"])
    expect(detail, 200)
    expect(
        mutate(
            engineer,
            base + "/junctions/" + first["id"],
            junction("SYNTHETIC-A-updated", [78.0, 17.0]),
            version=1,
            method="PATCH",
        ),
        200,
    )
    pipe = {
        "zone_id": zone["id"],
        "from_junction_id": first["id"],
        "to_junction_id": second["id"],
        "geometry": {"type": "LineString", "coordinates": [[78.0, 17.0], [78.0001, 17.0]]},
        "material": "SYNTHETIC PVC metadata",
        "diameter_mm": 32,
        "path_length_m": None,
        "topology_quality": "UNVERIFIED",
    }
    row = expect(mutate(engineer, base + "/pipes", pipe), 201)
    with env["owner"].begin() as c:
        lengths = one(
            c,
            "SELECT geometry_length_m,surveyed_length_m,length_basis FROM pipe_segments WHERE id=:i",
            i=row["id"],
        )
        assert 10 < float(lengths["geometry_length_m"]) < 12
        assert lengths["surveyed_length_m"] is None and lengths["length_basis"] == "GEODESIC"
    expect(engineer.request("GET", base + "/pipes?zone_id=" + zone["id"]), 200)
    detail = engineer.request("GET", base + "/pipes/" + row["id"])
    expect(detail, 200)
    changed = expect(
        mutate(
            engineer,
            base + "/pipes/" + row["id"],
            {**pipe, "path_length_m": 15},
            version=1,
            method="PATCH",
        ),
        200,
    )
    assert changed["path_length_m"] == 15 and changed["topology_quality"] == "REVIEW_REQUIRED"
    expect(
        mutate(
            engineer,
            base + "/junctions/" + first["id"],
            junction("Moved while referenced", [78.1, 17.0]),
            version=2,
            method="PATCH",
        ),
        409,
    )
    expect(
        mutate(
            engineer,
            base + "/pipes",
            {
                **pipe,
                "geometry": {"type": "LineString", "coordinates": [[78.01, 17.0], [78.0001, 17.0]]},
            },
        ),
        409,
    )
    expect(mutate(engineer, base + "/pipes", {**pipe, "diameter_mm": -1}), 422)
    expect(mutate(engineer, base + "/junctions", junction("Invalid latitude", [78, 120])), 422)


def test_manual_evidence_assessment_links_and_pagination(env):
    f = setup(env)
    base = f["base"]
    sup = f["supervisor"]
    engineer = f["engineer"]
    complaint = expect(mutate(f["citizen"], base + "/complaints", complaint_body()), 201)
    with env["owner"].begin() as c:
        evidence = one(
            c, "SELECT id FROM evidence_records WHERE complaint_id=:i", i=complaint["id"]
        )["id"]
    b = {
        "kind": "UNRESOLVED_CAUSE",
        "disposition": "UNRESOLVED",
        "evidence_record_ids": [str(evidence)],
        "reason": "SYNTHETIC citizen report is manual and does not establish a physical leak",
    }
    assessment = expect(mutate(engineer, base + "/evidence-assessments", b), 201)
    expect(engineer.request("GET", base + "/evidence-assessments/" + assessment["id"]), 200)
    expect(engineer.request("GET", base + "/evidence-assessments"), 200)
    expect(
        mutate(
            engineer,
            base + "/evidence-assessments",
            {**b, "kind": "ACOUSTIC_CANDIDATE", "disposition": "QUALIFIED_CANDIDATE"},
        ),
        422,
    )
    first = incident(env, f)
    second = incident(env, f)
    expect(
        mutate(
            sup,
            base + "/incidents/" + first["id"] + "/links",
            {
                "target_incident_id": second["id"],
                "relation": "DUPLICATE_OF",
                "reason": "SYNTHETIC reviewed duplicate concern",
            },
            version=first["version"],
        ),
        200,
    )
    expect(
        mutate(
            sup,
            base + "/incidents/" + second["id"] + "/links",
            {
                "target_incident_id": first["id"],
                "relation": "DUPLICATE_OF",
                "reason": "SYNTHETIC redirect cycle must be rejected",
            },
            version=second["version"],
        ),
        409,
    )
    expect(
        mutate(
            sup,
            base + "/incidents/" + first["id"] + "/links",
            {
                "target_incident_id": first["id"],
                "relation": "RELATED",
                "reason": "SYNTHETIC self link must be rejected",
            },
            version=first["version"],
        ),
        422,
    )
    page = expect(sup.request("GET", base + "/incidents?limit=1"), 200)
    assert len(page["items"]) == 1 and page["next_cursor"]
    next_page = expect(
        sup.request("GET", base + "/incidents?limit=1&cursor=" + page["next_cursor"]), 200
    )
    assert next_page["items"][0]["id"] != page["items"][0]["id"]
    expect(
        sup.request("GET", base + "/incidents?limit=1&status=NEW&cursor=" + page["next_cursor"]),
        422,
    )
    expect(sup.request("GET", base + "/incidents?workspace_mode=SIMULATION"), 422)
    expect(f["citizen"].request("GET", base + "/complaints"), 200)
    expect(f["admin"].request("GET", "/api/v1/public/utilities/synthetic-utility-a"), 200)
    expect(f["admin"].request("GET", "/api/v1/public/project-status"), 200)
    expect(f["citizen"].request("GET", base), 200)


def test_enabled_request_contracts_reject_unknown_writable_fields(env):
    client = login(env, "admin-a@example.invalid")
    for op in OPERATIONS:
        if not op["request"]:
            continue
        path = op["path"]
        for parameter in DESIGN["paths"][path][op["method"]].get("parameters", []):
            if parameter["in"] == "path":
                path = path.replace(
                    "{" + parameter["name"] + "}",
                    str(env["org"]["id"])
                    if parameter["name"] == "organization_id"
                    else str(uuid4()),
                )
        expect(
            client.request(
                op["method"].upper(),
                "/api/v1" + path,
                json={"unreviewed_owner_role_source_override": "forbidden"},
            ),
            422,
        )
    # The reviewed precondition gap has a machine-checkable correction.
    assert (
        DESIGN["components"]["schemas"]["MembershipView"]["properties"]["version"]["minimum"] == 1
    )
    assert len(OPERATIONS) == 58


def test_supported_filters_and_unknown_filters_do_not_widen_scope(env):
    f = setup(env)
    engineer = f["engineer"]
    base = f["base"]
    expect(engineer.request("GET", base + "/zones?zone_id=" + f["zone"]["id"]), 200)
    expect(engineer.request("GET", base + "/zones?arbitrary_owner=" + str(uuid4())), 422)
    expect(engineer.request("GET", base + "/zones?limit=101"), 422)
    expect(engineer.request("GET", base + "/zones?limit=1&limit=2"), 422)
    expect(engineer.request("GET", base + "/zones?bbox=nan,0,1,1"), 422)
    expect(
        f["admin"].request(
            "GET", base + "/audit-logs?from_time=2026-01-01T00:00:00Z&to_time=2026-03-01T00:00:00Z"
        ),
        422,
    )
