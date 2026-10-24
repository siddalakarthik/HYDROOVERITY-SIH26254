"use client";
import { useState } from "react";
import { date, label, orgPath, type Model } from "@/lib/api";
import {
  ActionForm,
  Badge,
  Empty,
  Field,
  Notice,
  ResourceState,
  Select,
  TextArea,
  useResource,
  value,
} from "@/components/ui";
import { Pager, usePage } from "@/components/pagination";

type Case = Model<"M07ServiceCaseCitizen"> | Model<"M07ServiceCaseStaff">;
type Request =
  Model<"M07AppointmentRequestCitizen"> | Model<"M07AppointmentRequestStaff">;
type Visit = Model<"M07AppointmentCitizen"> | Model<"M07AppointmentStaff">;
const reason = () => (
  <TextArea
    name="reason"
    label="Reason visible to the resident"
    minLength={5}
    maxLength={1000}
    required
  />
);

function Decision({
  org,
  row,
  refresh,
}: {
  org: string;
  row: Model<"M07AppointmentRequestStaff">;
  refresh: () => void;
}) {
  const windows = usePage<Model<"M07StaffWindow">>(
    orgPath(org, "/dispatch/appointment-windows?state=PUBLISHED"),
  );
  const [decision, setDecision] = useState("CONFIRM_REQUESTED");
  return (
    <details className="disclosure">
      <summary>Review appointment request</summary>
      <label>
        Decision
        <select value={decision} onChange={(e) => setDecision(e.target.value)}>
          <option value="CONFIRM_REQUESTED">Confirm requested window</option>
          <option value="OFFER_ALTERNATIVE">Offer an alternative</option>
          <option value="DECLINE">Decline request</option>
        </select>
      </label>
      <ActionForm
        path={orgPath(org, `/appointment-requests/${row.id}/decisions`)}
        version={row.version}
        submit="Record appointment decision"
        onDone={refresh}
        build={(f) => {
          const common = {
            public_message: value(f, "reason"),
            internal_reason: value(f, "internal_reason"),
          };
          if (decision === "DECLINE")
            return {
              decision: "DECLINE",
              ...common,
              reason_code: "UTILITY_REVIEW",
            } satisfies Model<"M07AppointmentDecision">;
          if (decision === "OFFER_ALTERNATIVE") {
            const w = windows.data?.items.find(
              (w) => w.id === value(f, "window"),
            );
            if (!w)
              throw new Error("Select a current published alternative window.");
            return {
              decision: "OFFER_ALTERNATIVE",
              ...common,
              alternative_window_id: w.id,
              expected_window_version: w.version,
              offer_expires_at: new Date(value(f, "expiry")).toISOString(),
              expectations: {
                ...row.expectations,
                window_version: w.version,
                calendar_version: w.calendar_version,
                policy_version: w.policy_version,
              },
            } satisfies Model<"M07AppointmentDecision">;
          }
          return {
            decision: "CONFIRM_REQUESTED",
            ...common,
            expectations: row.expectations,
          } satisfies Model<"M07AppointmentDecision">;
        }}
      >
        {decision === "OFFER_ALTERNATIVE" && (
          <ResourceState {...windows}>
            <Select
              name="window"
              label="Alternative window"
              options={(windows.data?.items ?? []).map((w) => ({
                value: w.id,
                label: `${date(w.arrival_start)} – ${date(w.arrival_end)}`,
              }))}
            />
            <Field
              name="expiry"
              label="Offer expires at (your browser timezone)"
              type="datetime-local"
              required
            />
            <Pager {...windows} />
          </ResourceState>
        )}
        {reason()}
        <TextArea
          name="internal_reason"
          label="Private dispatch reason"
          minLength={5}
          maxLength={2000}
          required
        />
      </ActionForm>
    </details>
  );
}

function Cancellation({
  org,
  row,
  service,
  staff,
  refresh,
}: {
  org: string;
  row: Visit;
  service: Case;
  staff: boolean;
  refresh: () => void;
}) {
  const work = useResource<Model<"WorkOrder">>(
    staff && "work_order_id" in row
      ? orgPath(org, `/work-orders/${row.work_order_id}`)
      : null,
  );
  return (
    <details className="disclosure">
      <summary>
        {row.cancellation_pending
          ? "Review cancellation pending"
          : "Cancel this appointment"}
      </summary>
      <Notice>
        Late resident requests remain pending until the utility decides. The
        current booking stays reserved until cancellation is confirmed.
      </Notice>
      <ActionForm
        path={orgPath(org, `/appointments/${row.id}/cancellations`)}
        version={row.version}
        submit={
          staff ? "Record cancellation decision" : "Request visit cancellation"
        }
        onDone={refresh}
        build={(f) => {
          const common = {
            reason_code: "VISIT_REVIEW",
            public_reason: value(f, "reason"),
            expected_service_version: service.version,
          };
          if (staff) {
            if (!work.data)
              throw new Error("Refresh current work before cancelling.");
            return {
              caller_action: "SUPERVISOR",
              ...common,
              internal_reason: value(f, "internal_reason"),
              expected_work_version: work.data.version,
              expected_assignment_version: work.data.assignment_version,
              disposition: value(f, "disposition") as
                "CANCEL" | "ACCEPT_PENDING_CANCEL" | "DECLINE_PENDING_CANCEL",
            } satisfies Model<"M07AppointmentCancel">;
          }
          return {
            caller_action: "RESIDENT",
            ...common,
          } satisfies Model<"M07AppointmentCancel">;
        }}
      >
        {reason()}
        {staff && (
          <>
            <ResourceState {...work}>
              <p className="meta">Current work version {work.data?.version}</p>
            </ResourceState>
            <Select
              name="disposition"
              label="Cancellation disposition"
              options={(row.cancellation_pending
                ? ["ACCEPT_PENDING_CANCEL", "DECLINE_PENDING_CANCEL"]
                : ["CANCEL"]
              ).map((v) => ({ value: v, label: label(v) }))}
            />
            <TextArea
              name="internal_reason"
              label="Private cancellation reason"
              required
              minLength={5}
            />
          </>
        )}
      </ActionForm>
    </details>
  );
}

export function Appointments({
  org,
  service,
  staff,
  onChange,
}: {
  org: string;
  service: Case;
  staff: boolean;
  onChange: () => void;
}) {
  const root = orgPath(org, `/service-requests/${service.id}`);
  const windows = useResource<Model<"M07Page_ResidentWindow">>(
    root + "/appointment-windows",
  );
  const requests = usePage<Request>(root + "/appointment-requests");
  const visits = usePage<Visit>(root + "/appointments");
  const refresh = () => {
    windows.refresh();
    requests.refresh();
    visits.refresh();
    onChange();
  };
  const active = visits.data?.items.find((v) =>
    ["CONFIRMED", "CHECKED_IN"].includes(v.status),
  );
  const pending = requests.data?.items.some((r) =>
    ["PENDING", "ALTERNATIVE_OFFERED"].includes(r.status),
  );
  return (
    <section className="panel appointment-panel">
      <div className="record-top">
        <div>
          <p className="eyebrow">Utility visits · Asia/Kolkata</p>
          <h2>Appointments and requests</h2>
        </div>
        <button className="button secondary" onClick={refresh}>
          Refresh visit status
        </button>
      </div>
      <Notice>
        A requested window holds no capacity. Only a server-confirmed
        appointment reserves a visit. Attendance does not establish repair
        completion or scientific verification.
      </Notice>
      <ResourceState {...visits}>
        {!visits.data?.items.length && (
          <Empty title="No confirmed visit">
            The utility must review service eligibility and publish an
            authorized window.
          </Empty>
        )}
        {visits.data?.items.map((v) => (
          <article className="dispatch-card" key={v.id}>
            <div className="record-top">
              <h3>
                {date(v.arrival_start)} – {date(v.arrival_end)}
              </h3>
              <Badge>{label(v.status)}</Badge>
            </div>
            <p>
              {v.expected_service_minutes} estimated service minutes ·
              Asia/Kolkata
            </p>
            {v.public_visit_message && <p>{v.public_visit_message}</p>}
            {v.cancellation_pending && (
              <Notice>
                Cancellation pending. This appointment is still confirmed and
                reserved.
              </Notice>
            )}
            {v.status === "CONFIRMED" && (
              <Cancellation
                org={org}
                row={v}
                service={service}
                staff={staff}
                refresh={refresh}
              />
            )}
          </article>
        ))}
        <Pager {...visits} />
      </ResourceState>
      <ResourceState {...requests}>
        {requests.data?.items.map((r) => (
          <article className="dispatch-card" key={r.id}>
            <div className="record-top">
              <h3>{label(r.kind)} visit request</h3>
              <Badge>{label(r.status)}</Badge>
            </div>
            <p>Requested: {date(r.requested_window.arrival_start)}</p>
            {r.public_message && <p>{r.public_message}</p>}
            {r.alternative_window && (
              <p>
                Alternative: {date(r.alternative_window.arrival_start)} · Offer
                expires {date(r.offer_expires_at ?? undefined)}
              </p>
            )}
            {staff &&
              "expectations" in r &&
              ["PENDING", "ALTERNATIVE_OFFERED"].includes(r.status) && (
                <Decision org={org} row={r} refresh={refresh} />
              )}
            {!staff &&
              r.status === "ALTERNATIVE_OFFERED" &&
              r.alternative_window && (
                <ActionForm
                  path={orgPath(
                    org,
                    `/appointment-requests/${r.id}/accept-alternative`,
                  )}
                  version={r.version}
                  submit="Accept offered alternative"
                  onDone={refresh}
                  build={() =>
                    ({
                      proposal_revision: r.proposal_revision!,
                      expected_window_version: r.alternative_window!.version,
                      expected_service_version: service.version,
                      expected_replaced_appointment_version:
                        active?.version ?? null,
                    }) satisfies Model<"M07AlternativeAccept">
                  }
                />
              )}
            {!staff &&
              ["PENDING", "ALTERNATIVE_OFFERED"].includes(r.status) && (
                <ActionForm
                  path={orgPath(
                    org,
                    `/appointment-requests/${r.id}/withdrawals`,
                  )}
                  version={r.version}
                  submit={
                    r.status === "ALTERNATIVE_OFFERED"
                      ? "Decline alternative and withdraw request"
                      : "Withdraw visit request"
                  }
                  onDone={refresh}
                  build={(f) =>
                    ({
                      reason_code: "RESIDENT",
                      reason: value(f, "reason"),
                    }) satisfies Model<"M07Reason">
                  }
                >
                  {reason()}
                </ActionForm>
              )}
          </article>
        ))}
        <Pager {...requests} />
      </ResourceState>
      <ResourceState {...windows}>
        <h3>Eligible published windows</h3>
        <p role="status">{windows.data?.message}</p>
        {!staff &&
          !pending &&
          active?.status !== "CHECKED_IN" &&
          !!windows.data?.items.length && (
            <ActionForm
              path={root + "/appointment-requests"}
              version={service.version}
              submit={active ? "Request rescheduling" : "Request a visit"}
              onDone={refresh}
              build={(f) => {
                const w = windows.data!.items.find(
                  (w) => w.id === value(f, "window"),
                )!;
                return {
                  kind: active ? "RESCHEDULE" : "INITIAL",
                  window_id: w.id,
                  expected_window_version: w.version,
                  expected_preferences_version: null,
                  replaces_appointment_id: active?.id ?? null,
                  expected_appointment_version: active?.version ?? null,
                  message: value(f, "message"),
                } satisfies Model<"M07AppointmentRequestCreate">;
              }}
            >
              <Select
                name="window"
                label="Eligible visit window"
                options={(windows.data?.items ?? []).map((w) => ({
                  value: w.id,
                  label: `${date(w.arrival_start)} – ${date(w.arrival_end)}`,
                }))}
              />
              <TextArea
                name="message"
                label="Optional visit request message"
                required={false}
                maxLength={500}
              />
              {active && (
                <Notice>
                  Your existing appointment stays confirmed until the
                  replacement commits.
                </Notice>
              )}
            </ActionForm>
          )}
        {!!windows.data?.next_cursor && (
          <Notice>
            More windows exist. Narrow the date range or refresh before
            selecting.
          </Notice>
        )}
      </ResourceState>
    </section>
  );
}
