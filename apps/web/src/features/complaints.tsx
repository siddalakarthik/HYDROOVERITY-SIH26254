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

const statusOptions = [
  "RECEIVED",
  "UNDER_REVIEW",
  "INVESTIGATING",
  "ACTION_PLANNED",
  "UPDATE_AVAILABLE",
  "RESOLVED",
  "CLOSED_NO_ACTION",
].map((value) => ({ value, label: label(value) }));
function ReportsList({
  org,
  supervisor = false,
  onSelect,
}: {
  org: string;
  supervisor?: boolean;
  onSelect?: (id: string) => void;
}) {
  const [status, setStatus] = useState("");
  const list = usePage<Model<"CitizenComplaint">>(
    orgPath(
      org,
      `/complaints${status ? `?status=${encodeURIComponent(status)}` : ""}`,
    ),
  );
  return (
    <>
      <div className="filter-bar">
        <Field label="Report status" name="status-filter">
          <select
            id="status-filter"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            {statusOptions.map((o) => (
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
          {!list.data?.items.length ? (
            <Empty title="No reports in this view">
              {supervisor
                ? "New reports will appear here when residents submit them."
                : "You have no reports matching this view. Create a report when you observe an issue."}
            </Empty>
          ) : (
            <ul className="record-list">
              {list.data.items.map((c) => (
                <li key={c.id}>
                  <div className="record-top">
                    <h3>
                      {supervisor ? (
                        <button
                          className="button secondary"
                          onClick={() => onSelect?.(c.id)}
                        >
                          {c.tracking_number}
                        </button>
                      ) : (
                        <Link href={`/citizen/${org}/reports/${c.id}`}>
                          {c.tracking_number}
                        </Link>
                      )}
                    </h3>
                    <Badge>{label(c.status)}</Badge>
                  </div>
                  <p>
                    {label(c.category)} · {c.coarse_area}
                  </p>
                  <p className="meta">{c.description}</p>
                </li>
              ))}
            </ul>
          )}
          <Pager {...list} />
        </section>
      </ResourceState>
    </>
  );
}
function ReportDetail({
  org,
  id,
  supervisor = false,
}: {
  org: string;
  id: string;
  supervisor?: boolean;
}) {
  const path = orgPath(org, `/complaints/${uuid(id)}`);
  const c = useResource<Model<"CitizenComplaint">>(path);
  return (
    <ResourceState {...c}>
      {c.data && (
        <>
          <section className="panel">
            <div className="record-top">
              <h2>{c.data.tracking_number}</h2>
              <Badge>{label(c.data.status)}</Badge>
            </div>
            <dl className="details-grid">
              <div>
                <dt>Category</dt>
                <dd>{label(c.data.category)}</dd>
              </div>
              <div>
                <dt>Rough area</dt>
                <dd>{c.data.coarse_area}</dd>
              </div>
            </dl>
            <p>{c.data.description}</p>
          </section>
          <section className="panel">
            <h2>Public-safe report history</h2>
            <ol className="timeline">
              {c.data.public_updates.map((u, i) => (
                <li key={`${u.occurred_at}-${i}`}>
                  <h3>{label(u.status)}</h3>
                  <p>{u.message}</p>
                  <p className="meta">{date(u.occurred_at)}</p>
                </li>
              ))}
            </ol>
          </section>
          {supervisor ? (
            <section className="panel">
              <h2>Review this report</h2>
              <ActionForm
                path={`${path}/review`}
                version={c.data.version}
                submit="Publish safe update"
                build={(f) =>
                  ({
                    public_status: value(
                      f,
                      "public_status",
                    ) as Model<"ComplaintStatus">,
                    public_message: value(f, "public_message"),
                    internal_reason: value(f, "internal_reason"),
                    incident_id: value(f, "incident_id") || null,
                  }) satisfies Model<"ComplaintReview">
                }
                onDone={c.refresh}
              >
                <Select
                  name="public_status"
                  label="Public status"
                  options={statusOptions}
                  defaultValue={c.data.status}
                />
                <TextArea
                  label="Message visible to the resident"
                  name="public_message"
                  maxLength={1000}
                />
                <Field
                  label="Incident ID (optional)"
                  name="incident_id"
                  help="Use an authorized operational incident. Leave blank if not linked."
                />
                <TextArea
                  label="Private review reason"
                  name="internal_reason"
                  help="This reason is stored privately and is not included in citizen history."
                />
              </ActionForm>
              <div className="actions">
                <Link href={`/app/${org}/incidents`}>
                  Review or create an incident
                </Link>
              </div>
            </section>
          ) : (
            !["RESOLVED", "CLOSED_NO_ACTION"].includes(c.data.status) && (
              <section className="panel">
                <h2>Add a follow-up</h2>
                <ActionForm
                  path={`${path}/follow-ups`}
                  version={c.data.version}
                  submit="Send follow-up"
                  build={(f) =>
                    ({
                      description: value(f, "description"),
                      photo_consent: false,
                      attachment_ids: [],
                    }) satisfies Model<"ComplaintFollowup">
                  }
                  onDone={c.refresh}
                >
                  <TextArea label="What has changed?" name="description" />
                </ActionForm>
              </section>
            )
          )}
        </>
      )}
    </ResourceState>
  );
}
export function CitizenReports({ org, rest }: { org: string; rest: string[] }) {
  const router = useRouter();
  if (rest[0] === "new")
    return (
      <>
        <Heading eyebrow="Citizen portal" title="Report a water issue">
          Describe what you observed. The report does not confirm a leak.
        </Heading>
        <section className="panel">
          <ActionForm
            path={orgPath(org, "/complaints")}
            submit="Submit report"
            build={(f) =>
              ({
                category: value(
                  f,
                  "category",
                ) as Model<"ComplaintWrite">["category"],
                description: value(f, "description"),
                coarse_area: value(f, "coarse_area"),
                photo_consent: false,
                attachment_ids: [],
              }) satisfies Model<"ComplaintWrite">
            }
            onDone={(data) =>
              router.push(
                `/citizen/${org}/reports/${(data as Model<"CitizenComplaint">).id}`,
              )
            }
          >
            <Select
              name="category"
              label="Issue category"
              options={[
                "VISIBLE_LEAK",
                "LOW_PRESSURE",
                "SERVICE_INTERRUPTION",
              ].map((value) => ({ value, label: label(value) }))}
            />
            <TextArea
              name="description"
              label="Describe the issue"
              minLength={10}
            />
            <Field
              name="coarse_area"
              label="Rough area or landmark"
              required
              minLength={2}
              maxLength={200}
              help="Do not enter precise home coordinates or unnecessary personal information."
            />
            <Notice>
              Photo upload is not enabled. This form stays in memory only;
              leaving the page discards unsent input. Submission requires an
              online server receipt.
            </Notice>
          </ActionForm>
        </section>
      </>
    );
  if (rest[0])
    return (
      <>
        <Heading eyebrow="Citizen portal" title="Your report" />
        <ReportDetail org={org} id={rest[0]} />
      </>
    );
  return (
    <>
      <Heading
        eyebrow="Citizen portal"
        title="My reports"
        action={
          <Link className="button" href={`/citizen/${org}/reports/new`}>
            Report a water issue
          </Link>
        }
      >
        Only reports submitted by your current utility membership appear here.
      </Heading>
      <ReportsList org={org} />
    </>
  );
}
export function SupervisorComplaints({ org }: { org: string }) {
  const [selected, setSelected] = useState<string>();
  return (
    <>
      <Heading eyebrow="Supervisor workspace" title="Citizen reports">
        Review concerns and author updates that are safe for residents.
      </Heading>
      {selected ? (
        <>
          <button
            className="button secondary"
            onClick={() => setSelected(undefined)}
          >
            Back to reports
          </button>
          <ReportDetail key={selected} org={org} id={selected} supervisor />
        </>
      ) : (
        <ReportsList org={org} supervisor onSelect={setSelected} />
      )}
    </>
  );
}
