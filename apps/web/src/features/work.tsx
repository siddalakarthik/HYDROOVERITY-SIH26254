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
import { priorities, type ScopeProps } from "./incidents";

const options = (values: string[]) =>
  values.map((value) => ({ value, label: label(value) }));
const edges: Record<string, string[]> = {
  ASSIGNED: ["ACCEPTED"],
  ACCEPTED: ["IN_PROGRESS"],
  IN_PROGRESS: ["BLOCKED", "SUBMITTED_FOR_REVIEW"],
  BLOCKED: ["IN_PROGRESS"],
};
function utcInput() {
  return new Date().toISOString().slice(0, 16);
}
function iso(form: FormData, name: string) {
  return new Date(`${value(form, name)}Z`).toISOString();
}
function Materials() {
  const [rows, setRows] = useState<number[]>([]);
  const [counter, setCounter] = useState(0);
  return (
    <div>
      <p className="help">Materials (optional; actual quantities and units)</p>
      {rows.map((n) => (
        <div className="panel" key={n}>
          <Field
            name={`material-name-${n}`}
            label={`Material ${n + 1} name`}
            maxLength={120}
            required
          />
          <Field
            name={`material-quantity-${n}`}
            label="Quantity"
            type="number"
            min="0.000001"
            step="any"
            required
          />
          <Field
            name={`material-unit-${n}`}
            label="Unit"
            maxLength={30}
            required
          />
          <button
            type="button"
            className="button secondary"
            onClick={() => setRows(rows.filter((i) => i !== n))}
          >
            Remove material {n + 1}
          </button>
        </div>
      ))}
      <button
        type="button"
        className="button secondary"
        disabled={rows.length >= 30}
        onClick={() => {
          setRows([...rows, counter]);
          setCounter(counter + 1);
        }}
      >
        Add material
      </button>
    </div>
  );
}
function materials(form: FormData): Model<"MaterialItem">[] {
  return [...form.keys()]
    .filter((k) => k.startsWith("material-name-"))
    .map((k) => {
      const id = k.slice("material-name-".length);
      return {
        name: value(form, k),
        quantity: Number(value(form, `material-quantity-${id}`)),
        unit: value(form, `material-unit-${id}`),
      };
    });
}
export function WorkOrders({ org, roles }: ScopeProps) {
  const router = useRouter();
  const [status, setStatus] = useState("");
  const list = usePage<Model<"WorkOrder">>(
    orgPath(
      org,
      `/work-orders?workspace_mode=OPERATIONAL${status ? `&status=${status}` : ""}`,
    ),
  );
  const supervisor = roles.includes("SUPERVISOR");
  const incidents = usePage<Model<"Incident">>(
    supervisor ? orgPath(org, "/incidents?workspace_mode=OPERATIONAL") : null,
  );
  return (
    <>
      <Heading
        eyebrow={
          roles.includes("TECHNICIAN") && !supervisor
            ? "Technician workspace"
            : "Maintenance operations"
        }
        title={
          roles.includes("TECHNICIAN") && !supervisor
            ? "My assigned work"
            : "Work orders"
        }
      >
        Assignments, work receipts and independent verification remain separate.
      </Heading>
      <div className="filter-bar">
        <Field name="work-status" label="Work status">
          <select
            id="work-status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            {[
              "CREATED",
              "ASSIGNED",
              "ACCEPTED",
              "IN_PROGRESS",
              "BLOCKED",
              "SUBMITTED_FOR_REVIEW",
              "COMPLETED",
              "CANCELLED",
            ].map((s) => (
              <option value={s} key={s}>
                {label(s)}
              </option>
            ))}
          </select>
        </Field>
        <button className="button secondary" onClick={list.refresh}>
          Refresh work orders
        </button>
      </div>
      <ResourceState {...list}>
        <section className="panel">
          {list.data?.items.length ? (
            <ul className="record-list">
              {list.data.items.map((w) => (
                <li key={w.id}>
                  <div className="record-top">
                    <h3>
                      <Link href={`/app/${org}/work-orders/${w.id}`}>
                        {w.instructions}
                      </Link>
                    </h3>
                    <Badge>{label(w.status)}</Badge>
                  </div>
                  <p className="meta">
                    Priority {label(w.priority)} · Due {date(w.due_at)}
                  </p>
                  <p className="meta">
                    {w.assignee_membership_id
                      ? "Assigned to an authorized member"
                      : "Awaiting assignment"}{" "}
                    · Version {w.version}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <Empty title="No work orders in this view">
              Technicians see current assignments only. A supervisor creates
              work after incident review.
            </Empty>
          )}
          <Pager {...list} />
        </section>
      </ResourceState>
      {supervisor && (
        <details className="disclosure">
          <summary>Create a work order</summary>
          <ResourceState {...incidents}>
            {incidents.data?.items.some((i) =>
              [
                "ACCEPTED",
                "IN_PROGRESS",
                "REOPENED",
                "INVESTIGATION_REQUIRED",
              ].includes(i.status),
            ) ? (
              <ActionForm
                path={orgPath(org, "/work-orders")}
                submit="Create work order"
                build={(f) =>
                  ({
                    incident_id: value(f, "incident_id"),
                    priority: value(
                      f,
                      "priority",
                    ) as Model<"WorkOrderWrite">["priority"],
                    instructions: value(f, "instructions"),
                  }) satisfies Model<"WorkOrderWrite">
                }
                onDone={(data) =>
                  router.push(
                    `/app/${org}/work-orders/${(data as Model<"WorkOrder">).id}`,
                  )
                }
              >
                <Select
                  name="incident_id"
                  label="Reviewed incident"
                  options={incidents.data.items
                    .filter((i) =>
                      [
                        "ACCEPTED",
                        "IN_PROGRESS",
                        "REOPENED",
                        "INVESTIGATION_REQUIRED",
                      ].includes(i.status),
                    )
                    .map((i) => ({ value: i.id, label: i.title }))}
                />
                <Select name="priority" label="Priority" options={priorities} />
                <TextArea
                  name="instructions"
                  label="Visit instructions"
                  maxLength={4000}
                />
              </ActionForm>
            ) : (
              <Notice>
                Review an incident before creating work, or page through the
                incident list to find an eligible record.
              </Notice>
            )}
            <Pager {...incidents} />
          </ResourceState>
        </details>
      )}
    </>
  );
}
export function WorkDetail({
  org,
  roles,
  id,
  membershipId,
}: ScopeProps & { id: string; membershipId: string }) {
  const path = orgPath(org, `/work-orders/${uuid(id)}`);
  const work = useResource<Model<"WorkOrder">>(path);
  const supervisor = roles.includes("SUPERVISOR");
  const assigned =
    roles.includes("TECHNICIAN") &&
    work.data?.assignee_membership_id === membershipId;
  const brief = useResource<Model<"WorkerBrief">>(
    assigned ? `${path}/brief` : null,
  );
  const repairs = usePage<Model<"Repair">>(`${path}/repairs`);
  const [recordedAt] = useState(utcInput);
  const refresh = () => {
    work.refresh();
    repairs.refresh();
    if (assigned) brief.refresh();
  };
  const final =
    work.data && ["COMPLETED", "CANCELLED"].includes(work.data.status);
  return (
    <>
      <Heading
        eyebrow="Work order detail"
        title="Investigation and repair record"
        action={<Link href={`/app/${org}/work-orders`}>All work orders</Link>}
      />
      <ResourceState {...work}>
        {work.data && (
          <>
            <section className="panel">
              <div className="record-top">
                <Badge>{label(work.data.status)}</Badge>
                <span className="meta">
                  Version {work.data.version} · Assignment version{" "}
                  {work.data.assignment_version}
                </span>
              </div>
              <h2>Visit instructions</h2>
              <p>{work.data.instructions}</p>
              <dl className="details-grid">
                <div>
                  <dt>Priority</dt>
                  <dd>{label(work.data.priority)}</dd>
                </div>
                <div>
                  <dt>Due</dt>
                  <dd>{date(work.data.due_at)}</dd>
                </div>
                <div>
                  <dt>Work order ID</dt>
                  <dd className="mono">{id}</dd>
                </div>
                <div>
                  <dt>Assigned membership ID</dt>
                  <dd className="mono">
                    {work.data.assignee_membership_id ?? "Unassigned"}
                  </dd>
                </div>
              </dl>
            </section>
            {assigned && (
              <ResourceState {...brief}>
                {brief.data && (
                  <section className="panel">
                    <h2>Assigned-task brief</h2>
                    <p>{brief.data.approximate_site}</p>
                    <p>{brief.data.safe_evidence_summary}</p>
                    <ul>
                      {brief.data.safety_instructions.map((s) => (
                        <li key={s}>{s}</li>
                      ))}
                    </ul>
                    <p className="meta">
                      Brief validity {date(brief.data.lease_expires_at)}. This
                      is not an offline write authorization.
                    </p>
                  </section>
                )}
              </ResourceState>
            )}
            <Notice tone="warning">
              Online authorization is required. No offline queue or persistent
              local draft is enabled. A completed work order is not a verified
              repair.
            </Notice>
            {supervisor && !final && (
              <details className="disclosure">
                <summary>Assign or reassign technician</summary>
                <ActionForm
                  path={`${path}/assignment`}
                  version={work.data.version}
                  submit="Record assignment"
                  build={(f) =>
                    ({
                      assignee_membership_id: value(
                        f,
                        "assignee_membership_id",
                      ),
                      due_at: value(f, "due_at") ? iso(f, "due_at") : null,
                      reason: value(f, "assignment_reason"),
                    }) satisfies Model<"AssignmentWrite">
                  }
                  onDone={refresh}
                >
                  <Field
                    name="assignee_membership_id"
                    label="Technician membership ID"
                    required
                    help="Obtain this utility's active TECHNICIAN membership ID from an authorized administrator. The backend validates current eligibility; supervisors have no member-directory API."
                  />
                  <Field
                    name="due_at"
                    label="Due date/time (UTC, optional)"
                    type="datetime-local"
                  />
                  <TextArea
                    name="assignment_reason"
                    label="Assignment reason"
                  />
                </ActionForm>
              </details>
            )}
            {!final && (assigned || supervisor) && (
              <section className="panel">
                <h2>Next work action</h2>
                <ActionForm
                  path={`${path}/transitions`}
                  version={work.data.version}
                  submit="Record work transition"
                  build={(f) =>
                    ({
                      target: value(f, "target") as Model<"WorkOrderStatus">,
                      reason: value(f, "transition_reason"),
                    }) satisfies Model<"WorkTransition">
                  }
                  onDone={refresh}
                >
                  <Select
                    name="target"
                    label="Next work state"
                    options={options([
                      ...new Set([
                        ...(assigned ? (edges[work.data.status] ?? []) : []),
                        ...(supervisor
                          ? [
                              ...(work.data.status === "SUBMITTED_FOR_REVIEW"
                                ? ["COMPLETED", "IN_PROGRESS"]
                                : []),
                              "CANCELLED",
                            ]
                          : []),
                      ]),
                    ])}
                  />
                  <TextArea
                    name="transition_reason"
                    label="Reason for work transition"
                  />
                </ActionForm>
              </section>
            )}
            {assigned &&
              ["ACCEPTED", "IN_PROGRESS", "BLOCKED"].includes(
                work.data.status,
              ) && (
                <section className="panel">
                  <h2>Record an inspection note</h2>
                  <ActionForm
                    path={`${path}/actions`}
                    submit="Save inspection note"
                    build={(f, key) =>
                      ({
                        operation_id: key,
                        observed_at: iso(f, "observed_at"),
                        base_version: work.data!.version,
                        assignment_version: work.data!.assignment_version,
                        note: value(f, "note"),
                        materials: materials(f),
                        attachment_ids: [],
                      }) satisfies Model<"WorkerAction">
                    }
                    onDone={refresh}
                  >
                    <Field
                      label="Observed date/time (UTC)"
                      name="observed_at"
                      type="datetime-local"
                      defaultValue={recordedAt}
                      required
                    />
                    <TextArea
                      label="Inspection note"
                      name="note"
                      maxLength={4000}
                      minLength={1}
                    />
                    <Materials />
                  </ActionForm>
                </section>
              )}
            {assigned &&
              ["IN_PROGRESS", "BLOCKED"].includes(work.data.status) && (
                <section className="panel">
                  <h2>Record a repair receipt</h2>
                  <ActionForm
                    path={`${path}/repairs`}
                    version={work.data.version}
                    submit="Save repair receipt"
                    build={(f) =>
                      ({
                        performed_at: iso(f, "performed_at"),
                        description: value(f, "repair_description"),
                        materials: materials(f),
                        attachment_ids: [],
                      }) satisfies Model<"RepairWrite">
                    }
                    onDone={refresh}
                  >
                    <Field
                      label="Performed date/time (UTC)"
                      name="performed_at"
                      type="datetime-local"
                      defaultValue={recordedAt}
                      required
                    />
                    <TextArea
                      label="Work performed and limitations"
                      name="repair_description"
                      minLength={10}
                      maxLength={4000}
                    />
                    <Materials />
                  </ActionForm>
                </section>
              )}
            <section className="panel">
              <h2>Repair receipts</h2>
              <ResourceState {...repairs}>
                {repairs.data?.items.length ? (
                  <ul className="record-list">
                    {repairs.data.items.map((r) => (
                      <li key={r.id}>
                        <h3>{r.description}</h3>
                        <p className="meta">
                          Manual work receipt · {date(r.performed_at)}
                        </p>
                        <Link href={`/app/${org}/repairs/${r.id}/verification`}>
                          Review verification history
                        </Link>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <Empty title="No repair receipt yet">
                    Work completion cannot be submitted as repair proof without
                    evidence.
                  </Empty>
                )}
                <Pager {...repairs} />
              </ResourceState>
            </section>
          </>
        )}
      </ResourceState>
    </>
  );
}
export function VerificationPage({
  org,
  roles,
  id,
}: ScopeProps & { id: string }) {
  const path = orgPath(org, `/repairs/${uuid(id)}/verifications`);
  const list = usePage<Model<"Verification">>(path);
  return (
    <>
      <Heading eyebrow="Independent review" title="Repair verification">
        A manual repair receipt cannot establish measured before/after
        comparability.
      </Heading>
      <Notice tone="warning">
        Current evidence supports only NOT_VERIFIABLE. Supply state,
        pressure/demand/storage, calibration/quality/freshness and
        unit/time-window comparability are not established. The repair actor
        cannot review their own outcome.
      </Notice>
      <ResourceState {...list}>
        <section className="panel">
          <h2>Verification history</h2>
          {list.data?.items.length ? (
            <ol className="timeline">
              {list.data.items.map((v) => (
                <li key={v.id}>
                  <h3>{label(v.outcome)}</h3>
                  <p>{v.reason}</p>
                  <p>{v.comparability.limitations}</p>
                  <p className="meta">Reviewed {date(v.reviewed_at)}</p>
                </li>
              ))}
            </ol>
          ) : (
            <Empty title="No independent review recorded" />
          )}
          <Pager {...list} />
        </section>
        {roles.includes("SUPERVISOR") && (
          <section className="panel">
            <h2>Record the evidence limitation</h2>
            <ActionForm
              path={path}
              version={1}
              submit="Record NOT_VERIFIABLE"
              build={(f) =>
                ({
                  outcome: "NOT_VERIFIABLE",
                  before_evidence_record_ids: [],
                  after_evidence_record_ids: [],
                  comparability: {
                    supply_state_comparable: false,
                    pressure_demand_storage_comparable: false,
                    calibration_quality_freshness_comparable: false,
                    unit_windows_comparable: false,
                    limitations: value(f, "limitations"),
                  },
                  reason: value(f, "verification_reason"),
                }) satisfies Model<"VerificationWrite">
              }
              onDone={list.refresh}
            >
              <TextArea
                name="limitations"
                label="Missing comparability and evidence"
                minLength={10}
                maxLength={4000}
              />
              <TextArea
                name="verification_reason"
                label="Independent reviewer reason"
                minLength={10}
                maxLength={4000}
              />
            </ActionForm>
          </section>
        )}
      </ResourceState>
    </>
  );
}
