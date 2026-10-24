"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  api,
  ApiError,
  date,
  label,
  orgPath,
  query,
  uuid,
  type Model,
} from "@/lib/api";
import {
  ActionForm,
  Badge,
  Empty,
  ErrorPanel,
  Field,
  Heading,
  Notice,
  ResourceState,
  Select,
  TextArea,
  useResource,
  value,
} from "@/components/ui";
import { Pager, usePage } from "@/components/pagination";
import { Appointments } from "./appointments";

type Case = Model<"M07ServiceCaseCitizen"> | Model<"M07ServiceCaseStaff">;
const options = (items: string[]) =>
  items.map((v) => ({ value: v, label: label(v) }));
const statuses = [
  "SUBMITTED",
  "UNDER_REVIEW",
  "AWAITING_RESIDENT",
  "ACCEPTED",
  "SERVICE_IN_PROGRESS",
  "SERVICE_REVIEW_PENDING",
  "SERVICE_CLOSED",
  "DECLINED",
  "WITHDRAWN",
  "CANCELLED",
];

function TrackingLookup({ org, root }: { org: string; root: string }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<unknown>();
  return (
    <form
      className="panel"
      onSubmit={async (e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        setPending(true);
        setError(undefined);
        try {
          const result = await api<Model<"M07ReferenceResult">>(
            orgPath(org, "/service-request-lookups"),
            {
              method: "POST",
              body: {
                tracking_reference: value(form, "reference"),
              } satisfies Model<"M07ReferenceLookup">,
            },
          );
          router.push(`${root}/${result.data.id}`);
        } catch (err) {
          setError(err);
        } finally {
          setPending(false);
        }
      }}
      aria-busy={pending}
    >
      <h2>Find a service request</h2>
      <Field
        name="reference"
        label="Tracking reference"
        required
        pattern="HYS-[0-9A-HJKMNP-TV-Z]{26}"
        maxLength={30}
        help="Sign-in and current ownership are required. A reference alone does not grant access."
      />
      <button className="button" disabled={pending}>
        {pending ? "Checking access…" : "Find request"}
      </button>
      {error !== undefined && <ErrorPanel error={error} />}
    </form>
  );
}

function Intake({ org, root }: { org: string; root: string }) {
  const router = useRouter();
  const reports = usePage<Model<"CitizenComplaint">>(
    orgPath(org, "/complaints"),
  );
  const previous = usePage<Case>(orgPath(org, "/service-requests"));
  return (
    <>
      <Heading eyebrow="Resident services" title="Request utility service">
        Ask the utility to review a water concern. Submission does not confirm a
        leak, acceptance or a visit.
      </Heading>
      <section className="panel">
        <ActionForm
          path={orgPath(org, "/service-requests")}
          submit="Submit service request"
          build={(f) =>
            ({
              category: value(f, "category") as Model<"M07ServiceCategory">,
              description: value(f, "description"),
              coarse_area: value(f, "coarse_area"),
              origin_complaint_id: value(f, "origin") || null,
              expected_complaint_version: value(f, "origin")
                ? (reports.data?.items.find(
                    (item) => item.id === value(f, "origin"),
                  )?.version ?? null)
                : null,
              follow_up_of_id: value(f, "follow_up") || null,
              service_privacy_acknowledged: true,
            }) satisfies Model<"M07ServiceCreate">
          }
          onDone={(data) => router.push(`${root}/${(data as Case).id}`)}
        >
          <Select
            name="category"
            label="Service category"
            options={options([
              "VISIBLE_LEAK",
              "LOW_PRESSURE",
              "SERVICE_INTERRUPTION",
            ])}
          />
          <TextArea
            name="description"
            label="What needs attention?"
            minLength={10}
          />
          <Field
            name="coarse_area"
            label="Rough area or public landmark"
            required
            minLength={2}
            maxLength={200}
            help="Keep home entry instructions, contact details and sensitive personal information out of this form."
          />
          <details className="disclosure">
            <summary>
              Connect an existing report or closed request (optional)
            </summary>
            <ResourceState {...reports}>
              <Select
                name="origin"
                label="Existing report (optional)"
                required={false}
                options={(reports.data?.items ?? []).map((item) => ({
                  value: item.id,
                  label: `${item.tracking_number} · ${item.coarse_area}`,
                }))}
              />
              <Pager {...reports} />
            </ResourceState>
            <ResourceState {...previous}>
              <Select
                name="follow_up"
                label="Closed request for a recurring concern (optional)"
                required={false}
                options={(previous.data?.items ?? [])
                  .filter((item) =>
                    [
                      "SERVICE_CLOSED",
                      "DECLINED",
                      "WITHDRAWN",
                      "CANCELLED",
                    ].includes(item.status),
                  )
                  .map((item) => ({
                    value: item.id,
                    label: `${item.tracking_reference} · ${item.coarse_area}`,
                  }))}
              />
              <Pager {...previous} />
            </ResourceState>
            <p className="help">
              Choose one source only. Both are optional. The server verifies
              ownership and current versions.
            </p>
          </details>
          <Field
            name="privacy"
            label="I understand this submits my description and rough area to the utility for review."
            type="checkbox"
            required
          />
          <Notice>
            Private development service. No appointment booking, visit-access
            collection, uploads or notifications are enabled. No service SLA or
            live retention policy is approved. Unsent input stays in memory; an
            online server receipt is required.
          </Notice>
        </ActionForm>
      </section>
    </>
  );
}

function List({
  org,
  root,
  staff,
}: {
  org: string;
  root: string;
  staff: boolean;
}) {
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const list = usePage<Case>(
    orgPath(org, `/service-requests${query({ status, category })}`),
  );
  return (
    <>
      <Heading
        eyebrow={staff ? "Supervisor workspace" : "Resident services"}
        title={staff ? "Service review queue" : "My service requests"}
        action={
          !staff && (
            <Link className="button" href={`${root}/new`}>
              Request utility service
            </Link>
          )
        }
      >
        Complaints, accepted service, work and independent verification remain
        separate records.
      </Heading>
      <TrackingLookup org={org} root={root} />
      <div className="filter-bar">
        <Field name="service-status" label="Service status">
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            {options(statuses).map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Field>
        <Field name="service-category" label="Service category">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All categories</option>
            {options([
              "VISIBLE_LEAK",
              "LOW_PRESSURE",
              "SERVICE_INTERRUPTION",
            ]).map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Field>
        <button className="button secondary" onClick={list.refresh}>
          Refresh
        </button>
      </div>
      <ResourceState {...list}>
        <section className="panel">
          {list.data?.items.length ? (
            <ul className="record-list">
              {list.data.items.map((row) => (
                <li key={row.id}>
                  <div className="record-top">
                    <h2>
                      <Link href={`${root}/${row.id}`}>
                        {row.tracking_reference}
                      </Link>
                    </h2>
                    <Badge>{label(row.status)}</Badge>
                  </div>
                  <p>
                    {label(row.category)} · {row.coarse_area}
                  </p>
                  <p>{row.description}</p>
                  <p className="meta">Submitted {date(row.created_at)}</p>
                  {row.cancellation_pending && (
                    <Notice>
                      Cancellation requested; service has not yet been
                      cancelled.
                    </Notice>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <Empty title="No service requests in this view">
              {staff
                ? "Resident submissions will appear here for review."
                : "Your own submissions will appear here after the server confirms receipt."}
            </Empty>
          )}
          <Pager {...list} />
        </section>
      </ResourceState>
    </>
  );
}

function LinkWork({
  org,
  path,
  row,
  refresh,
}: {
  org: string;
  path: string;
  row: Case;
  refresh: () => void;
}) {
  const work = usePage<Model<"WorkOrder">>(
    orgPath(org, "/work-orders?workspace_mode=OPERATIONAL"),
  );
  return (
    <details className="disclosure">
      <summary>Link authorized work</summary>
      <Notice>
        Only active work from a genuinely triaged operational incident can be
        linked. A deadline is not an appointment. Creating or triaging an
        incident is a separate utility decision.
      </Notice>
      <ResourceState {...work}>
        <ActionForm
          path={`${path}/work-order-links`}
          version={row.version}
          submit="Link work order"
          build={(f) => {
            const selected = work.data!.items.find(
              (w) => w.id === value(f, "work_order_id"),
            )!;
            return {
              work_order_id: selected.id,
              expected_work_version: selected.version,
              purpose: value(f, "purpose") as Model<"M07TaskPurpose">,
              internal_reason: value(f, "internal_reason"),
              dispatch_service_area_code: value(f, "dispatch_area") || null,
              dispatch_required_skill_codes: value(f, "dispatch_skills")
                ? value(f, "dispatch_skills")
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean)
                : null,
            } satisfies Model<"M07WorkLinkWrite">;
          }}
          onDone={refresh}
        >
          <Select
            name="work_order_id"
            label="Authorized work order"
            options={(work.data?.items ?? [])
              .filter((w) => !["COMPLETED", "CANCELLED"].includes(w.status))
              .map((w) => ({
                value: w.id,
                label: `${w.id} · ${label(w.status)}`,
              }))}
          />
          <Select
            name="purpose"
            label="Existing work purpose"
            options={options(["INVESTIGATION", "INSPECTION", "REPAIR"])}
          />
          <TextArea name="internal_reason" label="Private linkage reason" />
          <Field
            name="dispatch_area"
            label="Supervisor-reviewed service-area code (optional)"
            maxLength={40}
            help="Without reviewed area and skills this link cannot be scheduled."
          />
          <Field
            name="dispatch_skills"
            label="Required skill codes, separated by commas (optional)"
          />
        </ActionForm>
        <Pager {...work} />
      </ResourceState>
      <Link href={`/app/${org}/work-orders`}>
        Review or create authorized work separately
      </Link>
    </details>
  );
}

function LinkedWorkVersion({
  org,
  link,
}: {
  org: string;
  link: Model<"M07WorkLink">;
}) {
  const work = useResource<Model<"WorkOrder">>(
    orgPath(org, `/work-orders/${link.work_order_id}`),
  );
  return (
    <ResourceState {...work}>
      {work.data && (
        <div className="panel">
          <Link href={`/app/${org}/work-orders/${link.work_order_id}`}>
            {work.data.instructions}
          </Link>
          <p>
            {label(work.data.status)} · {label(link.purpose)}
          </p>
          <input
            type="hidden"
            name={`work-version-${link.work_order_id}`}
            value={work.data.version}
          />
          <button
            type="button"
            className="button secondary"
            onClick={work.refresh}
          >
            Refresh linked work status
          </button>
        </div>
      )}
    </ResourceState>
  );
}

function Detail({
  org,
  id,
  root,
  staff,
}: {
  org: string;
  id: string;
  root: string;
  staff: boolean;
}) {
  const path = orgPath(org, `/service-requests/${uuid(id)}`);
  const request = useResource<Case>(path);
  const timeline = usePage<Model<"M07PublicUpdate">>(`${path}/timeline`);
  const internal = usePage<Model<"M07InternalEvent">>(
    staff ? `${path}/timeline?audience=INTERNAL` : null,
  );
  const refresh = () => {
    request.refresh();
    timeline.refresh();
    if (staff) internal.refresh();
  };
  const row = request.data;
  const final =
    row &&
    ["SERVICE_CLOSED", "DECLINED", "WITHDRAWN", "CANCELLED"].includes(
      row.status,
    );
  const before =
    row &&
    ["SUBMITTED", "UNDER_REVIEW", "AWAITING_RESIDENT"].includes(row.status);
  const triageTargets =
    row?.status === "SUBMITTED"
      ? ["UNDER_REVIEW"]
      : row?.status === "UNDER_REVIEW"
        ? ["AWAITING_RESIDENT", "ACCEPTED", "DECLINED"]
        : row?.status === "AWAITING_RESIDENT"
          ? ["UNDER_REVIEW"]
          : [];
  const transitions =
    row?.status === "ACCEPTED"
      ? ["START_SERVICE", "REQUEST_REVIEW", "CANCEL"]
      : row?.status === "SERVICE_IN_PROGRESS"
        ? ["REQUEST_REVIEW", "CANCEL"]
        : row?.status === "SERVICE_REVIEW_PENDING"
          ? ["RETURN_TO_WORK", "CLOSE", "CANCEL"]
          : [];
  return (
    <>
      <Heading
        eyebrow={staff ? "Supervisor workspace" : "Resident services"}
        title="Service request"
        action={<Link href={root}>Back to service requests</Link>}
      />
      <ResourceState {...request}>
        {row && (
          <>
            <section className="panel">
              <div className="record-top">
                <h2 className="tracking-reference">{row.tracking_reference}</h2>
                <Badge>{label(row.status)}</Badge>
              </div>
              <p>{row.description}</p>
              <dl className="details-grid">
                <div>
                  <dt>Category</dt>
                  <dd>{label(row.category)}</dd>
                </div>
                <div>
                  <dt>Rough area</dt>
                  <dd>{row.coarse_area}</dd>
                </div>
                <div>
                  <dt>Submitted</dt>
                  <dd>{date(row.created_at)}</dd>
                </div>
                <div>
                  <dt>Accepted</dt>
                  <dd>{date(row.accepted_at)}</dd>
                </div>
                <div>
                  <dt>Operational outcome</dt>
                  <dd>
                    {row.service_outcome
                      ? label(row.service_outcome)
                      : "Not closed"}
                  </dd>
                </div>
                <div>
                  <dt>Scientific verification</dt>
                  <dd>{label(row.verification_summary)}</dd>
                </div>
              </dl>
              <p className="meta">
                Version {row.version} ·{" "}
                {row.current_appointment
                  ? label(row.current_appointment.status)
                  : "No appointment confirmed"}
              </p>
              {row.cancellation_pending && (
                <Notice>
                  Cancellation is pending utility review. The request remains
                  active.
                </Notice>
              )}
              <button className="button secondary" onClick={refresh}>
                Refresh request and history
              </button>
            </section>
            <Appointments
              org={org}
              service={row}
              staff={staff}
              onChange={refresh}
            />
            <section className="panel">
              <h2>Resident-visible timeline</h2>
              <ResourceState {...timeline}>
                <ol className="timeline">
                  {timeline.data?.items.map((item) => (
                    <li key={item.id}>
                      <h3>
                        {label(item.event_kind)}
                        {item.supersedes_id ? " · Correction" : ""}
                      </h3>
                      <p>{item.message}</p>
                      <p className="meta">{date(item.published_at)}</p>
                    </li>
                  ))}
                </ol>
                <Pager {...timeline} />
              </ResourceState>
            </section>
            {staff && (
              <section className="panel">
                <h2>Private utility history</h2>
                <ResourceState {...internal}>
                  <ol className="timeline">
                    {internal.data?.items.map((item) => (
                      <li key={item.id}>
                        <h3>{label(item.event_kind)}</h3>
                        <p>{item.internal_reason}</p>
                        <p className="meta">
                          {date(item.received_at)} · Version{" "}
                          {item.resulting_version}
                        </p>
                      </li>
                    ))}
                  </ol>
                  <Pager {...internal} />
                </ResourceState>
              </section>
            )}
            {!final && !staff && (
              <section className="panel">
                <h2>Add information</h2>
                <ActionForm
                  path={`${path}/follow-ups`}
                  version={row.version}
                  submit="Send service follow-up"
                  build={(f, key) =>
                    ({
                      operation_id: key,
                      message: value(f, "message"),
                    }) satisfies Model<"M07Followup">
                  }
                  onDone={refresh}
                >
                  <TextArea
                    name="message"
                    label="Additional information for this request"
                    minLength={1}
                  />
                </ActionForm>
                <h2>
                  {before ? "Withdraw this request" : "Request cancellation"}
                </h2>
                <ActionForm
                  path={`${path}/transitions`}
                  version={row.version}
                  submit={before ? "Withdraw request" : "Request cancellation"}
                  build={(f) =>
                    ({
                      action: before ? "WITHDRAW" : "REQUEST_CANCELLATION",
                      reason_code: "RESIDENT_REQUEST",
                      public_message: value(f, "reason"),
                    }) satisfies Model<"M07ServiceTransition">
                  }
                  onDone={refresh}
                >
                  <TextArea
                    name="reason"
                    label="Reason for this request"
                    maxLength={1000}
                  />
                </ActionForm>
              </section>
            )}
            {!final && staff && (
              <>
                {triageTargets.length > 0 && (
                  <section className="panel">
                    <h2>Utility triage</h2>
                    <ActionForm
                      path={`${path}/triage`}
                      version={row.version}
                      submit="Record triage decision"
                      build={(f) =>
                        ({
                          target: value(
                            f,
                            "target",
                          ) as Model<"M07Triage">["target"],
                          public_message: value(f, "public_message"),
                          internal_reason: value(f, "internal_reason"),
                        }) satisfies Model<"M07Triage">
                      }
                      onDone={refresh}
                    >
                      <Select
                        name="target"
                        label="Review decision"
                        options={options(triageTargets)}
                      />
                      <TextArea
                        name="public_message"
                        label="Message visible to the resident"
                        maxLength={1000}
                      />
                      <TextArea
                        name="internal_reason"
                        label="Private triage reason"
                      />
                    </ActionForm>
                  </section>
                )}
                <section className="panel">
                  <h2>Publish customer-safe progress</h2>
                  <ActionForm
                    path={`${path}/public-updates`}
                    version={row.version}
                    submit="Publish service update"
                    build={(f) =>
                      ({
                        event_kind: value(
                          f,
                          "event_kind",
                        ) as Model<"M07PublicUpdateWrite">["event_kind"],
                        message: value(f, "message"),
                        supersedes_update_id: value(f, "supersedes") || null,
                      }) satisfies Model<"M07PublicUpdateWrite">
                    }
                    onDone={refresh}
                  >
                    <Select
                      name="event_kind"
                      label="Update kind"
                      options={options([
                        "INFORMATION",
                        "PROGRESS",
                        "CORRECTION",
                      ])}
                    />
                    <TextArea name="message" label="Resident-visible update" />
                    <Select
                      name="supersedes"
                      label="Update being corrected (corrections only)"
                      required={false}
                      options={(timeline.data?.items ?? []).map((u) => ({
                        value: u.id,
                        label: `${date(u.published_at)} · ${u.message.slice(0, 70)}`,
                      }))}
                    />
                  </ActionForm>
                </section>
                {!before && (
                  <LinkWork org={org} path={path} row={row} refresh={refresh} />
                )}
                {transitions.length > 0 && (
                  <section className="panel">
                    <h2>Service disposition</h2>
                    <Notice>
                      Final disposition requires current linked work to be
                      reviewed or cancelled. Closing service does not resolve an
                      incident or verify a repair.
                    </Notice>
                    <ActionForm
                      path={`${path}/transitions`}
                      version={row.version}
                      submit="Record service disposition"
                      build={(f) => {
                        const action = value(f, "action");
                        const common = {
                          action,
                          reason_code: "UTILITY_REVIEW",
                          public_message: value(f, "public_message"),
                          internal_reason: value(f, "internal_reason"),
                        };
                        if (action === "CLOSE" || action === "CANCEL") {
                          const versions = [...f.entries()]
                            .filter(([key]) => key.startsWith("work-version-"))
                            .map(([key, version]) => ({
                              work_order_id: key.slice(13),
                              version: Number(version),
                            }));
                          return {
                            ...common,
                            expected_work_versions: versions,
                            child_dispositions: [],
                            ...(action === "CLOSE"
                              ? { service_outcome: value(f, "outcome") }
                              : {}),
                          };
                        }
                        return common;
                      }}
                      onDone={refresh}
                    >
                      <Select
                        name="action"
                        label="Service action"
                        options={options(transitions)}
                      />
                      <Select
                        name="outcome"
                        label="Closure outcome (close only)"
                        required={false}
                        options={options([
                          "ADVICE_PROVIDED",
                          "REPAIR_REPORTED",
                          "REFERRED",
                          "NO_ACTION_WITH_REASON",
                        ])}
                      />
                      <TextArea
                        name="public_message"
                        label="Disposition message visible to resident"
                        maxLength={1000}
                      />
                      <TextArea
                        name="internal_reason"
                        label="Private disposition reason"
                      />
                      {"work_links" in row &&
                        row.work_links.map((link) => (
                          <LinkedWorkVersion
                            key={`${link.id}-${row.version}`}
                            org={org}
                            link={link}
                          />
                        ))}
                    </ActionForm>
                  </section>
                )}
              </>
            )}
            {staff && "work_links" in row && (
              <section className="panel">
                <h2>Authorized work links</h2>
                {row.work_links.length ? (
                  <ul className="record-list">
                    {row.work_links.map((link) => (
                      <li key={link.id}>
                        <Link
                          href={`/app/${org}/work-orders/${link.work_order_id}`}
                        >
                          {link.work_order_id}
                        </Link>
                        <p>{label(link.purpose)}</p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No work linked.</p>
                )}
              </section>
            )}
            <Notice>
              Visit preferences, access instructions, uploads and notifications
              are disabled. Please do not enter access codes or sensitive home
              information.
            </Notice>
          </>
        )}
      </ResourceState>
    </>
  );
}

export function ServiceRequests({
  org,
  rest,
  staff = false,
}: {
  org: string;
  rest: string[];
  staff?: boolean;
}) {
  const root = `/${staff ? "app" : "citizen"}/${org}/service-requests`;
  if (!staff && rest[0] === "new") return <Intake org={org} root={root} />;
  if (rest[0])
    return <Detail org={org} id={rest[0]} root={root} staff={staff} />;
  return <List org={org} root={root} staff={staff} />;
}

export function InvestigationFindings({
  org,
  work,
  assigned,
  refresh,
}: {
  org: string;
  work: Model<"WorkOrder">;
  assigned: boolean;
  refresh: () => void;
}) {
  const path = orgPath(org, `/work-orders/${work.id}/findings`);
  const findings = usePage<Model<"M07Findings">>(path);
  const [observed] = useState(() => new Date().toISOString().slice(0, 16));
  if (
    findings.error instanceof ApiError &&
    findings.error.code === "FINDINGS_PURPOSE"
  )
    return null;
  return (
    <section className="panel">
      <h2>Investigation findings</h2>
      <Notice>
        Manual findings document investigation or inspection. They do not claim
        a repair or independent scientific verification.
      </Notice>
      <ResourceState {...findings}>
        <ul className="record-list">
          {findings.data?.items.map((row) => (
            <li key={row.id}>
              <p>{row.findings}</p>
              <p>{row.no_repair_reason}</p>
              <p className="meta">
                {date(row.observed_at)} · MANUAL
                {row.supersedes_id ? " · Corrects earlier findings" : ""}
              </p>
            </li>
          ))}
        </ul>
        <Pager {...findings} />
        {assigned && ["IN_PROGRESS", "BLOCKED"].includes(work.status) && (
          <ActionForm
            path={path}
            version={work.version}
            submit="Record investigation findings"
            build={(f, key) =>
              ({
                operation_id: key,
                assignment_version: work.assignment_version,
                observed_at: new Date(`${value(f, "observed")}Z`).toISOString(),
                findings: value(f, "findings"),
                no_repair_reason: value(f, "no_repair_reason"),
                attachment_ids: [],
                supersedes_id: value(f, "supersedes") || null,
              }) satisfies Model<"M07FindingsWrite">
            }
            onDone={() => {
              findings.refresh();
              refresh();
            }}
          >
            <Field
              name="observed"
              label="Observed at (UTC)"
              type="datetime-local"
              defaultValue={observed}
              required
            />
            <TextArea
              name="findings"
              label="Investigation findings"
              minLength={10}
              maxLength={4000}
            />
            <TextArea
              name="no_repair_reason"
              label="Why no repair was performed"
            />
            <Select
              name="supersedes"
              label="Your earlier findings to correct (optional)"
              required={false}
              options={(findings.data?.items ?? []).map((f) => ({
                value: f.id,
                label: `${date(f.received_at)} · ${f.findings.slice(0, 60)}`,
              }))}
            />
          </ActionForm>
        )}
      </ResourceState>
    </section>
  );
}
