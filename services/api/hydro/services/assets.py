"""AssetService persistent operations and permission-aware projections."""

import json

from ..db import execute, one
from ..errors import require
from ..repository import change, insert
from .base import Service


class AssetService(Service):
    def run(self, b, parent):
        s, c = self.s, self.c
        method = s.op["method"]
        path = s.op["path"]
        table = (
            "water_zones"
            if s.op["group"] == "Water zones"
            else "network_junctions"
            if "/junctions" in path
            else "pipe_segments"
        )
        if method == "get":
            return (
                s.view(table, parent)
                if parent
                else s.page(table, dict(s.auth.request.query_params))
            )
        if table == "water_zones":
            values = {**b, "topology_quality": "UNVERIFIED"}
            row = (
                change(c, table, parent["id"], **values)
                if parent
                else insert(c, table, organization_id=self.o, **values)
            )
        else:
            geo = json.dumps(b["geometry"])
            values = {k: v for k, v in b.items() if k not in {"geometry", "path_length_m"}}
            if table == "network_junctions":
                row = (
                    change(c, table, parent["id"], **values)
                    if parent
                    else insert(
                        c,
                        table,
                        organization_id=self.o,
                        point=one(c, "SELECT ST_GeomFromGeoJSON(:g) AS value", g=geo)["value"],
                        **values,
                    )
                )
                if parent:
                    execute(
                        c,
                        "UPDATE network_junctions SET point=ST_GeomFromGeoJSON(:g) WHERE id=:i",
                        g=geo,
                        i=parent["id"],
                    )
            else:
                a = s.row("network_junctions", b["from_junction_id"])
                z = s.row("network_junctions", b["to_junction_id"])
                require(
                    a["zone_id"] == z["zone_id"] and str(a["zone_id"]) == b["zone_id"],
                    422,
                    "ZONE_CONFLICT",
                    "Pipe endpoints must belong to the selected zone",
                )
                length = one(c, "SELECT ST_Length(ST_GeomFromGeoJSON(:g)::geography) AS n", g=geo)[
                    "n"
                ]
                require(
                    length > 0, 422, "INVALID_GEOMETRY", "Pipe requires a positive geodesic length"
                )
                values.update(
                    surveyed_length_m=b["path_length_m"],
                    length_uncertainty_m=None,
                    geometry_length_m=length,
                    length_basis="SURVEYED" if b["path_length_m"] is not None else "GEODESIC",
                )
                if b["path_length_m"] is not None:
                    values["topology_quality"] = "REVIEW_REQUIRED"
                geometry = one(c, "SELECT ST_GeomFromGeoJSON(:g) AS value", g=geo)["value"]
                row = (
                    change(c, table, parent["id"], geometry=geometry, **values)
                    if parent
                    else insert(c, table, organization_id=self.o, geometry=geometry, **values)
                )
            row = s.row(table, row["id"])
        return self.save(table, row)
