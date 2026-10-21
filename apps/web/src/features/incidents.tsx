"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { date, label, orgPath, uuid, type Model } from "@/lib/api";
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

export type ScopeProps = { org: string; roles: string[] };
export const priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"].map((value) => ({
  value,
  label: label(value),
}));
const incidentEdges: Record<string, string[]> = {
  NEW: ["UNDER_REVIEW"],
  UNDER_REVIEW: ["INVESTIGATION_REQUIRED", "ACCEPTED", "DISMISSED"],
  INVESTIGATION_REQUIRED: ["ACCEPTED", "DISMISSED"],
  ACCEPTED: ["IN_PROGRESS"],
  IN_PROGRESS: ["VERIFICATION_PENDING"],
  VERIFICATION_PENDING: ["NOT_VERIFIABLE"],
  REOPENED: ["UNDER_REVIEW", "IN_PROGRESS"],
  NOT_VERIFIABLE: ["UNDER_REVIEW"],
  RESOLVED: ["REOPENED"],
  DISMISSED: ["UNDER_REVIEW"],
};
const options = (values: string[]) =>
  values.map((value) => ({ value, label: label(value) }));
export function Overview({ org, roles }: ScopeProps) {
  const incidents = usePage<Model<"Incident">>(
    orgPath(org, "/incidents?workspace_mode=OPERATIONAL"),
  );
  const work = usePage<Model<"WorkOrder">>(
    orgPath(org, "/work-orders?workspace_mode=OPERATIONAL"),
  );
  const zones = usePage<Model<"ZoneView">>(orgPath(org, "/zones"));
  return (
    <>
      <Heading
        eyebrow={
          roles.includes("SUPERVISOR")
            ? "Supervisor workspace"
            : "Engineering workspace"
        }
        title="Operations overview"
      >
        Review authorized records and decide what needs attention.
      </Heading>
      <Notice tone="warning">
        Hardware connection pending. Supply state is unknown without qualified
        observations. No measured leak rate or water-savings metric is
        available.
      </Notice>
      <div className="metrics">
        <div>
          <strong>{incidents.data?.items.length ?? "—"}</strong>
          <span>Incidents in current page</span>
        </div>
        <div>
          <strong>{work.data?.items.length ?? "—"}</strong>
          <span>Work orders in current page</span>
        </div>
        <div>
          <strong>{zones.data?.items.length ?? "—"}</strong>
          <span>Zones in current page</span>
        </div>
      </div>
      <div className="workspace-grid">
        <section className="panel">
          <h2>Recent incidents</h2>
          <ResourceState {...incidents}>
            {incidents.data?.items.length ? (
              <ul className="record-list">
                {incidents.data.items.slice(0, 5).map((i) => (
                  <li key={i.id}>
                    <Link href={`/app/${org}/incidents/${i.id}`}>
                      {i.title}
                    </Link>
                    <p>
                      <Badge>{label(i.status)}</Badge>{" "}
                      <span className="meta">Severity {label(i.severity)}</span>
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <Empty title="No incidents yet">
                A concern can be created after review of a report or authorized
                evidence.
              </Empty>
            )}
            <Pager {...incidents} />
          </ResourceState>
          <Link href={`/app/${org}/incidents`}>Review incidents</Link>
        </section>
        <section className="panel">
          <h2>Work awaiting attention</h2>
          <ResourceState {...work}>
            {work.data?.items.length ? (
              <ul className="record-list">
                {work.data.items.slice(0, 5).map((w) => (
                  <li key={w.id}>
                    <Link href={`/app/${org}/work-orders/${w.id}`}>
                      {w.instructions}
                    </Link>
                    <p>
                      <Badge>{label(w.status)}</Badge>
                    </p>
                    <p className="meta">Due {date(w.due_at)}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <Empty title="No work orders yet">
                Assignments follow an incident review. Completion is separate
                from verification.
              </Empty>
            )}
            <Pager {...work} />
          </ResourceState>
          <Link href={`/app/${org}/work-orders`}>Open work orders</Link>
        </section>
      </div>
      <ResourceState {...zones}>
        <section className="panel">
          <h2>Network context</h2>
          <p>
            {zones.data?.items.length ?? 0} authorized zones on this page.
            Geometry quality and supply-state limitations are retained.
          </p>
          <Link href={`/app/${org}/network`}>
            Explore authorized network records
          </Link>
        </section>
      </ResourceState>
    </>
  );
}
export function Incidents({ org, roles }: ScopeProps) {
  const router = useRouter();
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const list = usePage<Model<"Incident">>(
    orgPath(
      org,
      `/incidents?workspace_mode=OPERATIONAL${status ? `&status=${status}` : ""}${severity ? `&severity=${severity}` : ""}`,
    ),
  );
  const zones = usePage<Model<"ZoneView">>(orgPath(org, "/zones"));
  return (
    <>
      <Heading eyebrow="Investigation" title="Incidents">
        Keep severity separate from scientific confidence. Manual concerns are
        not confirmed sensor detections.
      </Heading>
      <div className="filter-bar">
        <Field name="incident-status" label="Status">
          <select
            id="incident-status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            {Object.keys(incidentEdges).map((s) => (
              <option value={s} key={s}>
                {label(s)}
              </option>
            ))}
          </select>
        </Field>
        <Field name="incident-severity" label="Severity">
          <select
            id="incident-severity"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
          >
            <option value="">All severities</option>
            {priorities.map((s) => (
              <option value={s.value} key={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </Field>
        <button className="button secondary" onClick={list.refresh}>
          Refresh incidents
        </button>
      </div>
      <ResourceState {...list}>
        <section className="panel">
          {list.data?.items.length ? (
            <ul className="record-list">
              {list.data.items.map((i) => (
                <li key={i.id}>
                  <div className="record-top">
                    <h3>
                      <Link href={`/app/${org}/incidents/${i.id}`}>
                        {i.title}
                      </Link>
                    </h3>
                    <Badge>{label(i.status)}</Badge>
                  </div>
                  <p className="meta">
                    Severity {label(i.severity)} · Operational record · Version{" "}
                    {i.version}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <Empty title="No incidents in this view">
              Create a concern from an authorized zone when an issue needs
              investigation.
            </Empty>
          )}
          <Pager {...list} />
        </section>
      </ResourceState>
      <details className="disclosure">
        <summary>Create an incident</summary>
        <ResourceState {...zones}>
          {zones.data?.items.length ? (
            <ActionForm
              path={orgPath(org, "/incidents")}
              submit="Create incident"
              build={(f) =>
                ({
                  zone_id: value(f, "zone_id"),
                  title: value(f, "title"),
                  severity: value(
                    f,
                    "severity",
                  ) as Model<"IncidentWrite">["severity"],
                  assessment_ids: value(f, "assessment_ids")
                    .split(/\s*,\s*/)
                    .filter(Boolean),
                  workspace_mode: "OPERATIONAL",
                  simulation_run_id: null,
                }) satisfies Model<"IncidentWrite">
              }
              onDone={(data) =>
                router.push(
                  `/app/${org}/incidents/${(data as Model<"Incident">).id}`,
                )
              }
            >
              <Select
                label="Authorized zone"
                name="zone_id"
                options={zones.data.items.map((z) => ({
                  value: z.id,
                  label: z.name,
                }))}
              />
              <Field
                label="Incident title"
                name="title"
                required
                minLength={5}
                maxLength={200}
              />
              <Select label="Severity" name="severity" options={priorities} />
              <Field
                label="Assessment IDs (optional, comma separated)"
                name="assessment_ids"
                help="Only current authorized manual assessments can be linked. Empty is allowed for an unqualified concern."
              />
            </ActionForm>
          ) : (
            <Notice>
              Create an authorized zone in Network before creating an incident.
            </Notice>
          )}
          <Pager {...zones} />
        </ResourceState>
      </details>
      {<EvidenceReviews org={org} editable={roles.includes("ENGINEER")} />}
    </>
  );
}
export function IncidentDetail({
  org,
  roles,
  id,
}: ScopeProps & { id: string }) {
  const path = orgPath(org, `/incidents/${uuid(id)}`);
  const incident = useResource<Model<"Incident">>(path);
  const events = usePage<Model<"TimelineEvent">>(`${path}/timeline`);
  const refresh = () => {
    incident.refresh();
    events.refresh();
  };
  return (
    <>
      <Heading
        eyebrow="Incident detail"
        title={incident.data?.title ?? "Review incident"}
        action={<Link href={`/app/${org}/incidents`}>All incidents</Link>}
      />
      <ResourceState {...incident}>
        {incident.data && (
          <>
            <section className="panel">
              <div className="record-top">
                <Badge>{label(incident.data.status)}</Badge>
                <span className="meta">
                  Version {incident.data.version} · Operational record
                </span>
              </div>
              <p>
                Severity {label(incident.data.severity)}. This lifecycle state
                does not itself establish a measured leak.
              </p>
              <dl className="details-grid">
                <div>
                  <dt>Incident ID</dt>
                  <dd className="mono">{id}</dd>
                </div>
                <div>
                  <dt>Zone ID</dt>
                  <dd className="mono">{incident.data.zone_id}</dd>
                </div>
              </dl>
            </section>
            <section className="panel">
              <h2>Evidence and decision history</h2>
              <ResourceState {...events}>
                {events.data?.items.length ? (
                  <ol className="timeline">
                    {events.data.items.map((e) => (
                      <li key={e.id}>
                        <h3>{label(e.event_type)}</h3>
                        <p>{e.safe_description}</p>
                        <p className="meta">
                          {e.actor_display} · {date(e.occurred_at)}
                        </p>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <Empty title="No timeline events in this page" />
                )}
                <Pager {...events} />
              </ResourceState>
            </section>
            {roles.includes("SUPERVISOR") && (
              <>
                <section className="panel">
                  <h2>Review lifecycle</h2>
                  <Notice>
                    Assignment, repair and independent-review requirements are
                    checked transactionally by the backend. Current manual
                    verification cannot establish PASSED or FAILED.
                  </Notice>
                  <ActionForm
                    path={`${path}/transitions`}
                    version={incident.data.version}
                    submit="Record transition"
                    build={(f) =>
                      ({
                        target: value(f, "target") as Model<"IncidentStatus">,
                        reason: value(f, "reason"),
                      }) satisfies Model<"IncidentTransition">
                    }
                    onDone={refresh}
                  >
                    <Select
                      name="target"
                      label="Next lifecycle state"
                      options={options(
                        incidentEdges[incident.data.status] ?? [],
                      )}
                    />
                    <TextArea
                      name="reason"
                      label="Reason for this transition"
                      minLength={10}
                    />
                  </ActionForm>
                </section>
                <details className="disclosure">
                  <summary>Link a related or duplicate incident</summary>
                  <ActionForm
                    path={`${path}/links`}
                    version={incident.data.version}
                    submit="Link incident"
                    build={(f) =>
                      ({
                        target_incident_id: value(f, "target_incident_id"),
                        relation: value(
                          f,
                          "relation",
                        ) as Model<"IncidentLinkWrite">["relation"],
                        reason: value(f, "link_reason"),
                      }) satisfies Model<"IncidentLinkWrite">
                    }
                    onDone={refresh}
                  >
                    <Field
                      name="target_incident_id"
                      label="Authorized target incident ID"
                      required
                    />
                    <Select
                      name="relation"
                      label="Relationship"
                      options={options(["RELATED", "DUPLICATE_OF"])}
                    />
                    <TextArea
                      name="link_reason"
                      label="Why are these related?"
                      minLength={10}
                    />
                  </ActionForm>
                </details>
                <div className="actions">
                  <Link
                    className="button secondary"
                    href={`/app/${org}/work-orders`}
                  >
                    Create or review work orders
                  </Link>
                </div>
              </>
            )}
          </>
        )}
      </ResourceState>
    </>
  );
}
function EvidenceReviews({
  org,
  editable,
}: {
  org: string;
  editable: boolean;
}) {
  const list = usePage<Model<"Evidence">>(
    orgPath(org, "/evidence-assessments?workspace_mode=OPERATIONAL"),
  );
  const [selected, setSelected] = useState<string>();
  const detail = useResource<Model<"Evidence">>(
    selected ? orgPath(org, `/evidence-assessments/${uuid(selected)}`) : null,
  );
  return (
    <details className="disclosure">
      <summary>Manual evidence assessments</summary>
      <ResourceState {...list}>
        {list.data?.items.length ? (
          <ul className="record-list">
            {list.data.items.map((e) => (
              <li key={e.id}>
                <button
                  className="button secondary"
                  onClick={() => setSelected(e.id)}
                >
                  {label(e.kind)} · {label(e.disposition)}
                </button>
                <p>{e.explanation}</p>
              </li>
            ))}
          </ul>
        ) : (
          <Empty title="No authorized assessments">
            Evidence discovery is limited to available authorized record IDs. No
            sensor observations are connected.
          </Empty>
        )}
        <Pager {...list} />
      </ResourceState>
      {selected && (
        <ResourceState {...detail}>
          {detail.data && (
            <section className="panel">
              <h3>{label(detail.data.kind)}</h3>
              <p>{detail.data.explanation}</p>
              <p className="meta">{detail.data.reason_codes.join(" · ")}</p>
              <p className="mono">
                Evidence IDs: {detail.data.evidence_record_ids.join(", ")}
              </p>
            </section>
          )}
        </ResourceState>
      )}
      {editable && (
        <ActionForm
          path={orgPath(org, "/evidence-assessments")}
          submit="Record manual assessment"
          description="Use only evidence record IDs obtained through authorized engineering records. There is no general raw-evidence discovery endpoint in M03."
          build={(f) =>
            ({
              kind: value(f, "kind") as Model<"EvidenceKind">,
              disposition: value(
                f,
                "disposition",
              ) as Model<"EvidenceDisposition">,
              evidence_record_ids: value(f, "evidence_ids")
                .split(/\s*,\s*/)
                .filter(Boolean),
              reason: value(f, "assessment_reason"),
            }) satisfies Model<"AssessmentWrite">
          }
          onDone={list.refresh}
        >
          <Select
            label="Evidence kind"
            name="kind"
            options={options([
              "HYDRAULIC_ANOMALY",
              "LOCAL_JOINT_SUSPICION",
              "ENVIRONMENTAL_WETNESS",
              "COLLECTION_FAILURE",
              "SENSOR_FAILURE",
              "INSUFFICIENT_SIGNAL",
              "UNRESOLVED_CAUSE",
            ])}
          />
          <Select
            label="Disposition"
            name="disposition"
            options={options(["OBSERVED", "SUSPECTED", "UNRESOLVED", "FAULT"])}
          />
          <Field
            label="Authorized evidence IDs (comma separated)"
            name="evidence_ids"
            required
          />
          <TextArea
            name="assessment_reason"
            label="Reason and limitations"
            minLength={10}
          />
        </ActionForm>
      )}
    </details>
  );
}
