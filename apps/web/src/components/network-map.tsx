"use client";
import { useEffect, useRef, useState } from "react";
import { type Model } from "@/lib/api";
import { featureCollection } from "@/lib/geometry";
import { Notice } from "./ui";
export default function NetworkMap({
  junctions,
  pipes,
  onSelect,
  selected,
}: {
  junctions: Model<"Junction">[];
  pipes: Model<"Pipe">[];
  onSelect: (kind: "junctions" | "pipes", id: string) => void;
  selected?: { kind: string; id: string };
}) {
  const container = useRef<HTMLDivElement>(null);
  const instance = useRef<import("maplibre-gl").Map | undefined>(undefined);
  const select = useRef(onSelect);
  const selection = useRef(selected);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    select.current = onSelect;
  }, [onSelect]);
  useEffect(() => {
    selection.current = selected;
    const map = instance.current;
    if (map?.getLayer("selected-pipe")) {
      for (const [layer, kind] of [
        ["selected-pipe", "pipes"],
        ["selected-junction", "junctions"],
      ])
        map.setFilter(layer, [
          "all",
          ["==", ["get", "kind"], kind],
          ["==", ["get", "id"], selected?.id ?? ""],
        ]);
    }
  }, [selected]);
  useEffect(() => {
    let disposed = false;
    let map: import("maplibre-gl").Map | undefined;
    void import("maplibre-gl")
      .then((m) => {
        if (disposed || !container.current) return;
        try {
          map = new m.Map({
            container: container.current,
            style: {
              version: 8,
              sources: {},
              layers: [
                {
                  id: "background",
                  type: "background",
                  paint: { "background-color": "#eaf0f3" },
                },
              ],
            },
            center: [0, 0],
            zoom: 1,
            attributionControl: false,
          });
          instance.current = map;
          map.addControl(
            new m.NavigationControl({ showCompass: false }),
            "top-right",
          );
          map.on("error", () => setFailed(true));
          map.on("load", () => {
            if (!map || disposed) return;
            const data = featureCollection(junctions, pipes);
            map.addSource("authorized-assets", { type: "geojson", data });
            map.addLayer({
              id: "pipes",
              type: "line",
              source: "authorized-assets",
              filter: ["==", ["get", "kind"], "pipes"],
              paint: { "line-color": "#075985", "line-width": 5 },
            });
            map.addLayer({
              id: "junctions",
              type: "circle",
              source: "authorized-assets",
              filter: ["==", ["get", "kind"], "junctions"],
              paint: {
                "circle-color": "#ffffff",
                "circle-radius": 7,
                "circle-stroke-width": 3,
                "circle-stroke-color": "#075985",
              },
            });
            map.addLayer({
              id: "selected-pipe",
              type: "line",
              source: "authorized-assets",
              filter: [
                "all",
                ["==", ["get", "kind"], "pipes"],
                ["==", ["get", "id"], selection.current?.id ?? ""],
              ],
              paint: { "line-color": "#9a3412", "line-width": 9 },
            });
            map.addLayer({
              id: "selected-junction",
              type: "circle",
              source: "authorized-assets",
              filter: [
                "all",
                ["==", ["get", "kind"], "junctions"],
                ["==", ["get", "id"], selection.current?.id ?? ""],
              ],
              paint: {
                "circle-color": "#ffffff",
                "circle-radius": 11,
                "circle-stroke-width": 4,
                "circle-stroke-color": "#9a3412",
              },
            });
            const bounds = new m.LngLatBounds();
            for (const j of junctions)
              bounds.extend(j.geometry.coordinates as [number, number]);
            for (const p of pipes)
              for (const c of p.geometry.coordinates)
                bounds.extend(c as [number, number]);
            if (!bounds.isEmpty())
              map.fitBounds(bounds, { padding: 64, maxZoom: 18, duration: 0 });
            for (const layer of ["pipes", "junctions"]) {
              map.on("click", layer, (e) => {
                const id = e.features?.[0]?.properties?.id;
                if (typeof id === "string")
                  select.current(layer as "pipes" | "junctions", id);
              });
              map.on("mouseenter", layer, () => {
                if (map) map.getCanvas().style.cursor = "pointer";
              });
              map.on("mouseleave", layer, () => {
                if (map) map.getCanvas().style.cursor = "";
              });
            }
          });
        } catch {
          setFailed(true);
        }
      })
      .catch(() => setFailed(true));
    return () => {
      disposed = true;
      instance.current = undefined;
      map?.remove();
    };
  }, [junctions, pipes]);
  return (
    <>
      <div className="map-wrap">
        <div className="map-label">
          Authorized geometry · No external basemap
          <br />
          Lines: pipes · Circles: junctions
        </div>
        <div
          ref={container}
          className="map-canvas"
          role="region"
          aria-label="Authorized network geometry; equivalent asset list follows"
        />
      </div>
      {failed && (
        <Notice tone="warning">
          Map rendering is unavailable in this browser. Use the equivalent
          authorized asset list below.
        </Notice>
      )}
    </>
  );
}
