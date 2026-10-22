"use client";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { label, orgPath, uuid, type Model } from "@/lib/api";
import { lineCoordinates, position } from "@/lib/geometry";
import {
  ActionForm,
  Badge,
  Empty,
  Field,
  Heading,
  Notice,
  ResourceState,
  Select,
  TextArea,
  useResource,
  value,
} from "@/components/ui";
import { usePage, Pager } from "@/components/pagination";
import { type ScopeProps } from "./incidents";
const Map = dynamic(() => import("@/components/network-map"), {
  ssr: false,
  loading: () => <div className="loading">Loading local map renderer…</div>,
});
type Kind = "zones" | "junctions" | "pipes";
const emptyJunctions: Model<"Junction">[] = [];
const emptyPipes: Model<"Pipe">[] = [];
export function NetworkPage({ org, roles }: ScopeProps) {
  const [zone, setZone] = useState("");
  const [material, setMaterial] = useState("");
  const [quality, setQuality] = useState("");
  const [kind, setKind] = useState<Kind>("zones");
  const [selected, setSelected] = useState<{ kind: Kind; id: string }>();
  const [create, setCreate] = useState(false);
  const zones = usePage<Model<"ZoneView">>(orgPath(org, "/zones"));
  const suffix = zone ? `?zone_id=${encodeURIComponent(zone)}` : "";
  const junctions = usePage<Model<"Junction">>(
    orgPath(org, `/junctions${suffix}`),
  );
  const pipes = usePage<Model<"Pipe">>(orgPath(org, `/pipes${suffix}`));
  const visibleJunctions = useMemo(
    () =>
      (junctions.data?.items ?? emptyJunctions).filter(
        (j) => !quality || j.topology_quality === quality,
      ),
    [junctions.data, quality],
  );
  const visiblePipes = useMemo(
    () =>
      (pipes.data?.items ?? emptyPipes).filter(
        (p) =>
          (!material || p.material === material) &&
          (!quality || p.topology_quality === quality),
      ),
    [pipes.data, material, quality],
  );
  const selectedPath = selected
    ? orgPath(org, `/${selected.kind}/${uuid(selected.id)}`)
    : null;
  const detail = useResource<
    Model<"ZoneView"> | Model<"Junction"> | Model<"Pipe">
  >(selectedPath);
  const refresh = () => {
    zones.refresh();
    junctions.refresh();
    pipes.refresh();
    detail.refresh();
    setCreate(false);
  };
  return (
    <>
      <Heading eyebrow="Engineering records" title="Network explorer">
        Authorized geometry, topology quality and path assumptions. No sensor
        coverage is inferred.
      </Heading>
      <Notice tone="warning">
        Topology is unverified unless supported by a reviewed record. A map line
        is not a surveyed acoustic path. This view shows the current junction
        and pipe pages only.
      </Notice>
      <div className="filter-bar">
        <Field name="zone-filter" label="Zone">
          <select
            id="zone-filter"
            value={zone}
            onChange={(e) => {
              setZone(e.target.value);
              setSelected(undefined);
            }}
          >
            <option value="">All permitted zones</option>
            {zones.data?.items.map((z) => (
              <option key={z.id} value={z.id}>
                {z.name}
              </option>
            ))}
          </select>
        </Field>
        <Field name="pipe-material-filter" label="Pipe material (current page)">
          <select
            value={material}
            onChange={(e) => setMaterial(e.target.value)}
          >
            <option value="">All materials</option>
            {[...new Set(pipes.data?.items.map((p) => p.material))].map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </Field>
        <Field name="topology-filter" label="Quality (current pages)">
          <select value={quality} onChange={(e) => setQuality(e.target.value)}>
            <option value="">All quality states</option>
            {[
              ...new Set([
                ...(junctions.data?.items.map((j) => j.topology_quality) ?? []),
                ...(pipes.data?.items.map((p) => p.topology_quality) ?? []),
              ]),
            ].map((q) => (
              <option key={q} value={q}>
                {q}
              </option>
            ))}
          </select>
        </Field>
        <button className="button secondary" onClick={refresh}>
          Refresh network
        </button>
      </div>
      <ResourceState
        loading={junctions.loading || pipes.loading}
        error={junctions.error ?? pipes.error}
        refresh={refresh}
      >
        {junctions.data?.items.length || pipes.data?.items.length ? (
          <Map
            selected={selected}
            junctions={visibleJunctions}
            pipes={visiblePipes}
            onSelect={(kind, id) => {
              setSelected({ kind, id });
              setCreate(false);
            }}
          />
        ) : (
          <Empty title="No geometry in this view">
            Choose another zone, page through authorized assets, or create
            reviewed records as an engineer.
          </Empty>
        )}
      </ResourceState>
      <div className="segmented" role="group" aria-label="Asset type">
        {(["zones", "junctions", "pipes"] as Kind[]).map((k) => (
          <button
            key={k}
            aria-pressed={kind === k}
            onClick={() => {
              setKind(k);
              setCreate(false);
              setSelected(undefined);
            }}
          >
            {label(k)}
          </button>
        ))}
      </div>
      <section className="panel">
        <h2>{label(kind)} · accessible list</h2>
        {kind === "zones" ? (
          <ResourceState {...zones}>
            {zones.data?.items.length ? (
              <ul className="record-list">
                {zones.data.items.map((z) => (
                  <li key={z.id}>
                    <div className="record-top">
                      <h3>{z.name}</h3>
                      <Badge>{z.topology_quality}</Badge>
                    </div>
                    <p className="meta">
                      Supply {label(z.supply_state)} · {z.id}
                    </p>
                    <button
                      className="button secondary"
                      onClick={() => {
                        setSelected({ kind: "zones", id: z.id });
                        setCreate(false);
                      }}
                    >
                      Inspect zone
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <Empty title="No zones yet" />
            )}
            <Pager {...zones} />
          </ResourceState>
        ) : kind === "junctions" ? (
          <ResourceState {...junctions}>
            {junctions.data?.items.length ? (
              <ul className="record-list">
                {visibleJunctions.map((j) => (
                  <li key={j.id}>
                    <div className="record-top">
                      <h3>{j.external_ref}</h3>
                      <Badge>{j.topology_quality}</Badge>
                    </div>
                    <p className="meta">
                      WGS84 longitude {j.geometry.coordinates[0]}, latitude{" "}
                      {j.geometry.coordinates[1]}
                    </p>
                    <button
                      className="button secondary"
                      onClick={() => {
                        setSelected({ kind: "junctions", id: j.id });
                        setCreate(false);
                      }}
                    >
                      Inspect junction
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <Empty title="No junctions in this view" />
            )}
            <Pager {...junctions} />
          </ResourceState>
        ) : (
          <ResourceState {...pipes}>
            {pipes.data?.items.length ? (
              <ul className="record-list">
                {visiblePipes.map((p) => (
                  <li key={p.id}>
                    <div className="record-top">
                      <h3>
                        {p.material} · {p.diameter_mm} mm
                      </h3>
                      <Badge>{p.topology_quality}</Badge>
                    </div>
                    <p>
                      {p.path_length_m === null
                        ? "Surveyed length not recorded"
                        : `Surveyed path length ${p.path_length_m} m`}
                    </p>
                    <p className="meta">{p.id}</p>
                    <button
                      className="button secondary"
                      onClick={() => {
                        setSelected({ kind: "pipes", id: p.id });
                        setCreate(false);
                      }}
                    >
                      Inspect pipe
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <Empty title="No pipes in this view" />
            )}
            <Pager {...pipes} />
          </ResourceState>
        )}
      </section>
      {roles.includes("ENGINEER") && (
        <button
          className="button"
          onClick={() => {
            setSelected(undefined);
            setCreate(!create);
          }}
        >
          {create
            ? "Cancel creation"
            : `Create ${kind === "pipes" ? "pipe" : kind === "junctions" ? "junction" : "zone"}`}
        </button>
      )}
      {selected && (
        <ResourceState {...detail}>
          {detail.data && (
            <section className="panel">
              <h2>Selected {selected.kind.slice(0, -1)}</h2>
              <dl className="details-grid">
                <div>
                  <dt>Resource ID</dt>
                  <dd>{detail.data.id}</dd>
                </div>
                <div>
                  <dt>Topology quality</dt>
                  <dd>{detail.data.topology_quality}</dd>
                </div>
                {"name" in detail.data && (
                  <>
                    <div>
                      <dt>Zone name</dt>
                      <dd>{detail.data.name}</dd>
                    </div>
                    <div>
                      <dt>Supply state</dt>
                      <dd>{label(detail.data.supply_state)}</dd>
                    </div>
                  </>
                )}
                {"external_ref" in detail.data && (
                  <>
                    <div>
                      <dt>Junction reference</dt>
                      <dd>{detail.data.external_ref}</dd>
                    </div>
                    <div>
                      <dt>WGS84 longitude, latitude</dt>
                      <dd>{detail.data.geometry.coordinates.join(", ")}</dd>
                    </div>
                  </>
                )}
                {"material" in detail.data && (
                  <>
                    <div>
                      <dt>Material / diameter</dt>
                      <dd>
                        {detail.data.material} / {detail.data.diameter_mm} mm
                      </dd>
                    </div>
                    <div>
                      <dt>From / to junction</dt>
                      <dd className="mono">
                        {detail.data.from_junction_id}
                        <br />
                        {detail.data.to_junction_id}
                      </dd>
                    </div>
                    <div>
                      <dt>Surveyed path length</dt>
                      <dd>
                        {detail.data.path_length_m === null
                          ? "Not recorded"
                          : `${detail.data.path_length_m} m`}
                      </dd>
                    </div>
                    <div>
                      <dt>WGS84 path (longitude, latitude)</dt>
                      <dd>
                        {detail.data.geometry.coordinates.map((pair, index) => (
                          <div key={index}>{pair.join(", ")}</div>
                        ))}
                      </dd>
                    </div>
                  </>
                )}
              </dl>
              {roles.includes("ENGINEER") ? (
                <AssetForm
                  key={`${selected.id}-${detail.etag}`}
                  org={org}
                  kind={selected.kind}
                  existing={detail.data}
                  version={detail.etag ?? undefined}
                  onDone={refresh}
                />
              ) : (
                <p className="meta">
                  Read-only supervisor view. Engineering changes require the
                  ENGINEER role.
                </p>
              )}
            </section>
          )}
        </ResourceState>
      )}
      {create && (
        <section className="panel">
          <h2>Create {kind.slice(0, -1)}</h2>
          <AssetForm org={org} kind={kind} onDone={refresh} />
        </section>
      )}
    </>
  );
}
function AssetForm({
  org,
  kind,
  existing,
  version,
  onDone,
}: {
  org: string;
  kind: Kind;
  existing?: Model<"ZoneView"> | Model<"Junction"> | Model<"Pipe">;
  version?: string;
  onDone: () => void;
}) {
  const j = existing && "external_ref" in existing ? existing : undefined;
  const p = existing && "material" in existing ? existing : undefined;
  const z = existing && "name" in existing ? existing : undefined;
  return (
    <ActionForm
      path={orgPath(org, `/${kind}${existing ? `/${uuid(existing.id)}` : ""}`)}
      method={existing ? "PATCH" : "POST"}
      version={version}
      submit={existing ? "Save reviewed asset edit" : "Create asset record"}
      onDone={onDone}
      build={(f) => {
        if (kind === "zones")
          return {
            name: value(f, "asset_name"),
            demand_boundary_version: value(f, "demand_boundary_version"),
            demand_accounting: {
              outflow_includes_customer_demand:
                value(f, "includes_demand") === "yes",
              storage_observed: value(f, "storage_observed") === "yes",
              notes: value(f, "accounting_notes"),
            },
          } satisfies Model<"ZoneWrite">;
        if (kind === "junctions")
          return {
            zone_id: value(f, "asset_zone"),
            external_ref: value(f, "external_ref"),
            topology_quality: value(f, "topology_quality"),
            geometry: {
              type: "Point",
              coordinates: position(
                Number(value(f, "longitude")),
                Number(value(f, "latitude")),
              ),
            },
          } satisfies Model<"JunctionWrite">;
        return {
          zone_id: value(f, "asset_zone"),
          from_junction_id: value(f, "from_junction_id"),
          to_junction_id: value(f, "to_junction_id"),
          geometry: {
            type: "LineString",
            coordinates: lineCoordinates(value(f, "coordinates")),
          },
          material: value(f, "material"),
          diameter_mm: Number(value(f, "diameter_mm")),
          path_length_m: value(f, "path_length_m")
            ? Number(value(f, "path_length_m"))
            : null,
          topology_quality: value(f, "topology_quality"),
        } satisfies Model<"PipeWrite">;
      }}
    >
      {kind === "zones" ? (
        <>
          <Field
            name="asset_name"
            label="Zone name"
            required
            maxLength={150}
            defaultValue={z?.name}
          />
          <Notice>
            The zone read projection omits demand-accounting settings. Enter the
            complete reviewed accounting definition; this form cannot infer the
            existing values.
          </Notice>
          <Field
            name="demand_boundary_version"
            label="Demand-boundary version"
            required
            maxLength={80}
          />
          <Select
            name="includes_demand"
            label="Does measured outflow include customer demand?"
            options={[
              { value: "yes", label: "Yes" },
              { value: "no", label: "No" },
            ]}
          />
          <Select
            name="storage_observed"
            label="Is storage change observed?"
            options={[
              { value: "yes", label: "Yes" },
              { value: "no", label: "No" },
            ]}
          />
          <TextArea
            name="accounting_notes"
            label="Accounting assumptions and limitations"
          />
        </>
      ) : (
        <>
          <Field
            name="asset_zone"
            label="Authorized zone ID"
            required
            defaultValue={j?.zone_id ?? p?.zone_id}
          />
          <Field
            name="topology_quality"
            label="Topology quality and review state"
            required
            maxLength={40}
            defaultValue={
              j?.topology_quality ?? p?.topology_quality ?? "UNVERIFIED"
            }
          />
          {kind === "junctions" ? (
            <>
              <Field
                name="external_ref"
                label="Junction reference"
                required
                maxLength={80}
                defaultValue={j?.external_ref}
              />
              <Field
                name="longitude"
                label="Longitude (WGS84 degrees)"
                type="number"
                required
                step="any"
                min={-180}
                max={180}
                defaultValue={j?.geometry.coordinates[0]}
              />
              <Field
                name="latitude"
                label="Latitude (WGS84 degrees)"
                type="number"
                required
                step="any"
                min={-90}
                max={90}
                defaultValue={j?.geometry.coordinates[1]}
              />
            </>
          ) : (
            <>
              <Field
                name="from_junction_id"
                label="From junction ID"
                required
                defaultValue={p?.from_junction_id}
              />
              <Field
                name="to_junction_id"
                label="To junction ID"
                required
                defaultValue={p?.to_junction_id}
              />
              <TextArea
                name="coordinates"
                label="WGS84 coordinates: longitude, latitude; one pair per line"
                minLength={5}
                maxLength={120000}
                defaultValue={p?.geometry.coordinates
                  .map((c) => c.join(", "))
                  .join("\n")}
              />
              <Field
                name="material"
                label="Pipe material"
                required
                maxLength={80}
                defaultValue={p?.material}
              />
              <Field
                name="diameter_mm"
                label="Diameter (mm)"
                type="number"
                min={0.000001}
                step="any"
                required
                defaultValue={p?.diameter_mm}
              />
              <Field
                name="path_length_m"
                label="Surveyed path length (m, optional)"
                type="number"
                min={0.000001}
                step="any"
                defaultValue={p?.path_length_m ?? ""}
                help="Leave empty if not surveyed. Rendered/geodesic length is not a surveyed acoustic path."
              />
            </>
          )}
        </>
      )}
    </ActionForm>
  );
}
