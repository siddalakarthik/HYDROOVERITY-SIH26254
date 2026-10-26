"use client";
import Link from "next/link";
import { date, label, orgPath, type Model } from "@/lib/api";
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
import { Pager, usePage } from "@/components/pagination";

const categories = [
  "COMPLAINT_PROGRESS",
  "SERVICE_PROGRESS",
  "APPOINTMENT",
  "WORK_ASSIGNMENT",
  "SERVICE_FEEDBACK",
] as const;

function Preferences({ org }: { org: string }) {
  const state = useResource<Model<"M07NotificationPreferences">>(
    orgPath(org, "/notification-preferences"),
  );
  return (
    <section className="panel" aria-labelledby="notification-preferences-title">
      <h2 id="notification-preferences-title">Notification preferences</h2>
      <p>
        Optional in-app alerts. Your report and service timelines and confirmed
        commitments remain available when alerts are off.
      </p>
      <ResourceState {...state}>
        {state.data && (
          <ActionForm
            key={state.data.version}
            path={orgPath(org, "/notification-preferences")}
            method="PUT"
            version={state.data.version}
            submit="Save notification preferences"
            onDone={state.refresh}
            build={(f) => {
              const start = value(f, "quiet_start"),
                end = value(f, "quiet_end");
              if (!!start !== !!end)
                throw new Error(
                  "Provide both quiet-hour boundaries or leave both empty.",
                );
              return {
                channels: {
                  in_app: f.get("in_app") === "on",
                  email: false,
                  sms: false,
                  push: false,
                },
                event_categories: categories.filter((c) => f.get(c) === "on"),
                quiet_hours: start
                  ? {
                      start_local: start,
                      end_local: end,
                      timezone: "Asia/Kolkata",
                    }
                  : null,
              } satisfies Model<"M07NotificationPreferencesWrite">;
            }}
          >
            <label className="check">
              <input
                type="checkbox"
                name="in_app"
                defaultChecked={state.data.channels.in_app}
              />{" "}
              Enable optional in-app notifications
            </label>
            <fieldset>
              <legend>Event categories</legend>
              {categories.map((c) => (
                <label className="check" key={c}>
                  <input
                    type="checkbox"
                    name={c}
                    defaultChecked={state.data!.event_categories.includes(c)}
                  />{" "}
                  {label(c)}
                </label>
              ))}
            </fieldset>
            <div className="form-grid">
              <Field
                name="quiet_start"
                label="Quiet hours start · Asia/Kolkata"
                type="time"
                defaultValue={state.data.quiet_hours?.start_local ?? ""}
              />
              <Field
                name="quiet_end"
                label="Quiet hours end · Asia/Kolkata"
                type="time"
                defaultValue={state.data.quiet_hours?.end_local ?? ""}
              />
            </div>
            <p className="help">
              Quiet hours defer optional alerts. Email, SMS and push are
              disabled. Preferences are stored only after server confirmation.
            </p>
          </ActionForm>
        )}
      </ResourceState>
    </section>
  );
}

function destination(org: string, item: Model<"M07Notification">) {
  const [kind, id] = item.resource_path.slice(1).split("/");
  if (kind === "complaints" && /^[0-9a-f-]{36}$/i.test(id ?? ""))
    return `/citizen/${org}/reports/${id}`;
  if (kind === "feedback") return `/app/${org}/feedback`;
  if (item.event_category === "WORK_ASSIGNMENT")
    return `/app/${org}/work-orders`;
  if (kind === "service-requests" && /^[0-9a-f-]{36}$/i.test(id ?? ""))
    return `/citizen/${org}/service-requests/${id}`;
  return `/citizen/${org}/service-requests`;
}

export function Notifications({ org }: { org: string }) {
  const inbox = usePage<Model<"M07Notification">>(
    orgPath(org, "/notifications"),
  );
  return (
    <>
      <Heading eyebrow="Your utility workspace" title="Notifications">
        Updates for your current membership. Delivery to this inbox does not
        mean an update has been read.
      </Heading>
      <div className="actions">
        <button className="button secondary" onClick={inbox.refresh}>
          Refresh notifications
        </button>
        <a className="button secondary" href="#notification-preferences-title">
          Manage preferences
        </a>
      </div>
      <ResourceState {...inbox}>
        {!inbox.data?.items.length && (
          <Empty title="No notifications available">
            Optional alerts may be off. Your service timeline and current task
            records remain authoritative.
          </Empty>
        )}
        <div className="card-grid">
          {inbox.data?.items.map((item) => (
            <article className="panel" key={item.id}>
              <div className="actions">
                <Badge>{item.read ? "READ" : "UNREAD"}</Badge>
                <span className="eyebrow">{label(item.event_category)}</span>
              </div>
              <p>{item.message}</p>
              <p className="meta">Received {date(item.created_at)}</p>
              <Link className="button secondary" href={destination(org, item)}>
                Open current authorized record
              </Link>
              {!item.read && (
                <ActionForm
                  path={orgPath(org, `/notifications/${item.id}/read`)}
                  version={item.version}
                  build={() => undefined}
                  submit="Mark as read"
                  onDone={inbox.refresh}
                />
              )}
            </article>
          ))}
        </div>
        <Pager {...inbox} />
      </ResourceState>
      <Preferences org={org} />
    </>
  );
}

function FeedbackForm({
  org,
  serviceId,
  refresh,
}: {
  org: string;
  serviceId?: string;
  refresh: () => void;
}) {
  return (
    <ActionForm
      path={orgPath(org, "/feedback")}
      submit="Submit feedback"
      onDone={refresh}
      description="Describe your experience. Feedback does not verify leak detection, repair effectiveness or water saved."
      build={(f) =>
        ({
          summary: value(f, "summary"),
          description: value(f, "description"),
          complaint_id: null,
          ...(serviceId
            ? {
                service_request_id: serviceId,
                service_rating: value(f, "rating")
                  ? Number(value(f, "rating"))
                  : null,
              }
            : {}),
        }) satisfies Model<"M07FeedbackWrite">
      }
    >
      <Field
        name="summary"
        label="Feedback summary"
        required
        minLength={5}
        maxLength={200}
      />
      <TextArea
        name="description"
        label="Your experience"
        minLength={5}
        maxLength={2000}
      />
      {serviceId && (
        <Field name="rating" label="Service experience rating (optional)">
          <select name="rating" defaultValue="">
            <option value="">No rating</option>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n} of 5
              </option>
            ))}
          </select>
        </Field>
      )}
    </ActionForm>
  );
}

function Review({
  org,
  item,
  refresh,
}: {
  org: string;
  item: Model<"M07Feedback">;
  refresh: () => void;
}) {
  return (
    <details className="disclosure">
      <summary>Review feedback</summary>
      <ActionForm
        path={orgPath(org, `/feedback/${item.id}/review`)}
        version={item.version}
        submit="Record feedback review"
        onDone={refresh}
        build={(f) =>
          ({
            status: value(f, "status") as Model<"M07FeedbackReview">["status"],
            severity: value(f, "severity"),
            assignee_membership_id: null,
            resolution_note: value(f, "resolution_note"),
            linked_github_issue_url: null,
          }) satisfies Model<"M07FeedbackReview">
        }
      >
        <Select
          name="status"
          label="Review status"
          defaultValue={item.status}
          options={["NEW", "TRIAGED", "PLANNED", "RESOLVED", "DECLINED"].map(
            (value) => ({ value, label: label(value) }),
          )}
        />
        <Field
          name="severity"
          label="Private review severity"
          required
          maxLength={30}
        />
        <TextArea
          name="resolution_note"
          label="Public response to the resident"
          minLength={1}
          maxLength={2000}
        />
        <Notice>
          This response is visible to the author. Do not include internal
          reasons, contact information or sensitive infrastructure details.
        </Notice>
      </ActionForm>
    </details>
  );
}

export function Feedback({
  org,
  roles,
  serviceId,
  eligible = true,
}: {
  org: string;
  roles: string[];
  serviceId?: string;
  eligible?: boolean;
}) {
  const page = usePage<Model<"M07Feedback">>(
    orgPath(
      org,
      `/feedback${serviceId ? `?service_request_id=${serviceId}` : ""}`,
    ),
  );
  const reviewer = roles.includes("SUPERVISOR") || roles.includes("ADMIN");
  return (
    <section aria-label="Feedback">
      {serviceId ? (
        <h2>Service experience feedback</h2>
      ) : (
        <Heading eyebrow="Resident experience" title="Feedback">
          Share your experience and view responses. Satisfaction, operational
          closure and independent scientific verification remain separate.
        </Heading>
      )}
      {!reviewer && eligible && (
        <FeedbackForm org={org} serviceId={serviceId} refresh={page.refresh} />
      )}
      {!reviewer && !eligible && (
        <Notice>
          Service feedback becomes available when this case is closed or
          cancelled. Use the service follow-up action for current concerns.
        </Notice>
      )}
      <div className="actions">
        <button className="button secondary" onClick={page.refresh}>
          Refresh feedback
        </button>
      </div>
      <ResourceState {...page}>
        {!page.data?.items.length && (
          <Empty title="No feedback available">
            Only feedback authorized for your current membership appears here.
          </Empty>
        )}
        {page.data?.items.map((item) => (
          <article className="panel" key={item.id}>
            <Badge>{item.status}</Badge>
            <h3>{item.summary}</h3>
            <p>{item.description}</p>
            {item.service_rating && (
              <p>
                Resident experience: {item.service_rating} of 5 · not scientific
                evidence
              </p>
            )}
            {item.resolution_note && (
              <div className="notice">
                <strong>Public response</strong>
                <p>{item.resolution_note}</p>
              </div>
            )}
            {reviewer && (
              <Review org={org} item={item} refresh={page.refresh} />
            )}
          </article>
        ))}
        <Pager {...page} />
      </ResourceState>
    </section>
  );
}

export function DeliveryAudit({
  org,
  requestId,
}: {
  org: string;
  requestId: string;
}) {
  const page = usePage<Model<"M07DeliveryAttempt">>(
    orgPath(org, `/service-requests/${requestId}/delivery-audit`),
  );
  return (
    <section className="panel" aria-label="Service delivery audit">
      <h2>In-app delivery audit</h2>
      <p>
        Delivery is inbox persistence, not proof of reading. No destinations or
        raw messages are exposed.
      </p>
      <button className="button secondary" onClick={page.refresh}>
        Refresh delivery audit
      </button>
      <ResourceState {...page}>
        {!page.data?.items.length && (
          <Empty title="No delivery records yet">
            Committed events may be awaiting the authorized worker. This is not
            a delivery confirmation.
          </Empty>
        )}
        <div className="card-grid">
          {page.data?.items.map((item) => (
            <article key={item.notification_id} className="dispatch-card">
              <h3>{label(item.event_kind)}</h3>
              <Badge>{item.state}</Badge>
              <p>In-app · {item.attempt_number} of 3 total attempts</p>
              <p className="meta">
                Attempted {date(item.attempted_at ?? undefined)}
              </p>
              {item.next_attempt_at && (
                <p>Next eligible attempt {date(item.next_attempt_at)}</p>
              )}
              {item.safe_error_code && <p>{label(item.safe_error_code)}</p>}
            </article>
          ))}
        </div>
        <Pager {...page} />
      </ResourceState>
    </section>
  );
}
