"use client";
import Link from "next/link";
import { useState } from "react";
import { date, label, orgPath, query, type Model } from "@/lib/api";
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

const codes = (f: FormData, k: string) =>
  value(f, k)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
const iso = (f: FormData, k: string) => new Date(value(f, k)).toISOString();
const policyFields = [
  "horizon_days",
  "minimum_lead_minutes",
  "free_cancel_before_minutes",
  "max_arrival_width_minutes",
  "request_expiry_hours",
  "offer_expiry_hours",
  "max_daily_minutes",
  "minimum_before_buffer_minutes",
  "minimum_after_buffer_minutes",
] as const;
function Policy({ org }: { org: string }) {
  const path = orgPath(org, "/dispatch/policy");
  const policy = useResource<Model<"M07DispatchPolicy">>(path);
  const row = policy.data;
  return (
    <section className="panel">
      <h2>Scheduling policy</h2>
      <ResourceState {...policy}>
        {row && (
          <>
            <Badge>
              {row.configured
                ? row.booking_enabled
                  ? "Enabled"
                  : "Disabled"
                : "Unconfigured"}
            </Badge>
            <Notice>
              Only actual authorized utility policy belongs here. Values are
              required explicitly; the application supplies no operating
              defaults. Recent reauthentication is required.
            </Notice>
            <details className="disclosure">
              <summary>Configure or disable scheduling</summary>
              <ActionForm
                path={path}
                method="PUT"
                version={row.version}
                submit="Save authorized policy"
                onDone={policy.refresh}
                build={(f) => ({
                  booking_enabled: f.get("booking_enabled") === "on",
                  ...Object.fromEntries(
                    policyFields.map((k) => [k, Number(value(f, k))]),
                  ),
                  allowed_duration_minutes: codes(f, "durations").map(Number),
                  reason: value(f, "reason"),
                })}
              >
                <Field
                  name="booking_enabled"
                  label="Enable booking after all authorized configuration exists"
                  type="checkbox"
                  defaultChecked={row.booking_enabled}
                />
                <div className="details-grid">
                  {policyFields.map((k) => (
                    <Field
                      key={k}
                      name={k}
                      label={label(k)}
                      type="number"
                      required
                      min={
                        k.includes("lead") ||
                        k.includes("buffer") ||
                        k.includes("cancel")
                          ? 0
                          : 1
                      }
                      defaultValue={row[k] ?? undefined}
                    />
                  ))}
                </div>
                <Field
                  name="durations"
                  label="Approved service durations in minutes, separated by commas"
                  required
                  defaultValue={row.allowed_duration_minutes.join(", ")}
                />
                <TextArea
                  name="reason"
                  label="Governance reason"
                  required
                  minLength={5}
                />
              </ActionForm>
            </details>
          </>
        )}
      </ResourceState>
    </section>
  );
}

export function DispatchGovernance({ org }: { org: string }) {
  const roster = usePage<Model<"M07DispatchTechnician">>(
    orgPath(org, "/dispatch/technicians"),
  );
  const members = usePage<Model<"MembershipView">>(
    orgPath(org, "/memberships"),
  );
  return (
    <>
      <Policy org={org} />
      <section className="panel">
        <h2>Exclusive technician enrollment</h2>
        <Notice>
          Enroll only authorized active technicians. One global person can
          schedule for one utility. No roster entry creates a role or a shift.
        </Notice>
        <ResourceState {...roster}>
          {roster.data?.items.map((p) => (
            <details className="disclosure" key={p.membership_id}>
              <summary>
                {p.display_name} · {label(p.enrollment_state)}
              </summary>
              <p>
                {label(p.scheduling_health)} · Calendar{" "}
                {p.calendar_version ?? "not configured"}
              </p>
              {p.enrollment_state !== "UNAVAILABLE" && (
                <ActionForm
                  path={orgPath(
                    org,
                    "/dispatch/technicians" +
                      (p.profile_version ? `/${p.membership_id}` : ""),
                  )}
                  method={p.profile_version ? "PATCH" : "POST"}
                  version={p.profile_version ?? undefined}
                  submit={
                    p.profile_version
                      ? "Review technician profile"
                      : "Enroll authorized technician"
                  }
                  onDone={roster.refresh}
                  build={(f) => {
                    const common = {
                      skill_codes: codes(f, "skills"),
                      service_area_codes: codes(f, "areas"),
                      max_daily_minutes: Number(value(f, "cap")),
                      reason: value(f, "reason"),
                    };
                    if (p.profile_version)
                      return {
                        ...common,
                        active: f.get("active") === "on",
                      } satisfies Model<"M07TechnicianProfilePatch">;
                    const membership = members.data?.items.find(
                      (m) => m.id === p.membership_id,
                    );
                    if (!membership)
                      throw new Error(
                        "Load current membership before enrollment.",
                      );
                    if (f.get("exclusive") !== "on")
                      throw new Error(
                        "Acknowledge exclusive utility enrollment.",
                      );
                    return {
                      ...common,
                      membership_id: p.membership_id,
                      expected_membership_version: membership.version!,
                      exclusive_dispatch_acknowledged: true,
                    } satisfies Model<"M07TechnicianEnroll">;
                  }}
                >
                  <Field
                    name="skills"
                    label="Reviewed skill codes, separated by commas"
                    required
                    defaultValue={p.skill_codes.join(", ")}
                  />
                  <Field
                    name="areas"
                    label="Reviewed service-area codes, separated by commas"
                    required
                    defaultValue={p.service_area_codes.join(", ")}
                  />
                  <Field
                    name="cap"
                    label="Authorized maximum daily occupied minutes"
                    type="number"
                    min={1}
                    max={960}
                    required
                    defaultValue={p.max_daily_minutes ?? undefined}
                  />
                  {p.profile_version ? (
                    <Field
                      name="active"
                      label="Active scheduling profile"
                      type="checkbox"
                      defaultChecked={p.active}
                    />
                  ) : (
                    <Field
                      name="exclusive"
                      label="I confirm exclusive scheduling enrollment in this utility"
                      type="checkbox"
                      required
                    />
                  )}
                  <TextArea
                    name="reason"
                    label="Governance review reason"
                    required
                    minLength={5}
                  />
                </ActionForm>
              )}
            </details>
          ))}
          <Pager {...roster} />
          <ResourceState {...members}>
            <Pager {...members} />
          </ResourceState>
        </ResourceState>
      </section>
    </>
  );
}

function RangeFilter({
  setRange,
}: {
  setRange: (range: { from: string; to: string }) => void;
}) {
  return (
    <form
      className="filter-grid"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        setRange({ from: iso(f, "from"), to: iso(f, "to") });
      }}
    >
      <Field
        name="from"
        label="Calendar from (your browser timezone)"
        type="datetime-local"
        required
      />
      <Field
        name="to"
        label="Calendar to (your browser timezone)"
        type="datetime-local"
        required
      />
      <button className="button secondary">Load schedule range</button>
    </form>
  );
}

function Calendar({
  org,
  member,
  range,
  staff,
}: {
  org: string;
  member: string;
  range: { from: string; to: string };
  staff: boolean;
}) {
  const path =
    orgPath(org, `/dispatch/technicians/${member}/calendar`) + query(range);
  type Calendar =
    Model<"M07StaffCalendarSnapshot"> | Model<"M07TechnicianCalendarSnapshot">;
  const calendar = useResource<Calendar>(path);
  const row = calendar.data;
  const refresh = calendar.refresh;
  return (
    <ResourceState {...calendar}>
      {row && (
        <>
          <p className="meta">
            Asia/Kolkata · Calendar revision {row.calendar_version} · Snapshot{" "}
            {date(row.as_of)}
          </p>
          <button className="button secondary" onClick={refresh}>
            Refresh current assignments
          </button>
          <h3>Dated shifts</h3>
          {row.shifts.items.map((s) => (
            <article className="dispatch-card" key={s.id}>
              <p>
                {date(s.interval.start_at)} – {date(s.interval.end_at)} ·{" "}
                {label(s.status)}
              </p>
              {staff && (
                <ActionForm
                  path={orgPath(org, `/dispatch/shifts/${s.id}`)}
                  method="PATCH"
                  version={s.version}
                  submit="Withdraw shift safely"
                  onDone={refresh}
                  build={(f) =>
                    ({
                      interval: s.interval,
                      status: "WITHDRAWN",
                      expected_calendar_version: row.calendar_version,
                      reason: value(f, "reason"),
                    }) satisfies Model<"M07ShiftChange">
                  }
                >
                  <TextArea
                    name="reason"
                    label="Shift withdrawal reason"
                    required
                    minLength={5}
                  />
                </ActionForm>
              )}
            </article>
          ))}
          <h3>Availability and work blocks</h3>
          {row.blocks.items.map((b) => (
            <article className="dispatch-card" key={b.id}>
              <p>
                {label(b.kind)} · {date(b.interval.start_at)} –{" "}
                {date(b.interval.end_at)}
              </p>
              {staff && (
                <>
                  <BlockChange
                    org={org}
                    block={b}
                    calendarVersion={row.calendar_version}
                    refresh={refresh}
                  />
                </>
              )}
            </article>
          ))}
          <h3>Assigned visits</h3>
          {!row.appointments.items.length && (
            <Empty title="No visits in this range">
              No booking is inferred from a work deadline.
            </Empty>
          )}
          {row.appointments.items.map((v) => (
            <article className="dispatch-card" key={v.id}>
              <div className="record-top">
                <h4>
                  {date(v.arrival_start)} – {date(v.arrival_end)}
                </h4>
                <Badge>{label(v.status)}</Badge>
              </div>
              {"service_request_id" in v ? (
                <Link
                  href={`/app/${org}/service-requests/${v.service_request_id}`}
                >
                  Review service and appointment decisions
                </Link>
              ) : (
                <>
                  <p>{v.safe_task_instructions}</p>
                  <p>{v.safe_access_instructions}</p>
                  <p className="meta">
                    Assignment revision {v.assignment_version} · Brief expires{" "}
                    {date(v.brief_expires_at)}
                  </p>
                  <Link href={`/app/${org}/work-orders/${v.work_order_id}`}>
                    Open currently assigned task
                  </Link>
                  {v.allowed_actions.length > 0 && (
                    <ActionForm
                      path={orgPath(org, `/appointments/${v.id}/visit-events`)}
                      version={v.version}
                      submit="Record visit event"
                      onDone={refresh}
                      build={(f, key) =>
                        ({
                          operation_id: key,
                          event_type: value(
                            f,
                            "event",
                          ) as Model<"M07VisitEventWrite">["event_type"],
                          observed_at: new Date().toISOString(),
                          assignment_version: v.assignment_version,
                          expected_work_version: v.work_version,
                          note: value(f, "note"),
                          supersedes_event_id: null,
                        }) satisfies Model<"M07VisitEventWrite">
                      }
                    >
                      <Select
                        name="event"
                        label="Permitted visit event"
                        options={v.allowed_actions.map((a) => ({
                          value: a,
                          label: label(a),
                        }))}
                      />
                      <TextArea
                        name="note"
                        label="Visit event note"
                        required
                        maxLength={2000}
                      />
                    </ActionForm>
                  )}
                </>
              )}
            </article>
          ))}
          {(row.appointments.next_cursor ||
            row.blocks.next_cursor ||
            row.shifts.next_cursor) && (
            <Notice>
              Schedule incomplete. Narrow the range before making capacity
              decisions.
            </Notice>
          )}
        </>
      )}
    </ResourceState>
  );
}

function BlockChange({
  org,
  block,
  calendarVersion,
  refresh,
}: {
  org: string;
  block: Model<"M07DispatchBlock">;
  calendarVersion: number;
  refresh: () => void;
}) {
  const work = useResource<Model<"WorkOrder">>(
    block.work_order_id
      ? orgPath(org, `/work-orders/${block.work_order_id}`)
      : null,
  );
  return (
    <details className="disclosure">
      <summary>Release or replace block</summary>
      <ActionForm
        path={orgPath(org, `/dispatch/blocks/${block.id}/release`)}
        version={block.version}
        submit="Release block"
        onDone={refresh}
        build={(f) =>
          ({
            expected_calendar_version: calendarVersion,
            expected_work_version: work.data?.version ?? null,
            reason: value(f, "reason"),
          }) satisfies Model<"M07BlockRelease">
        }
      >
        <TextArea
          name="reason"
          label="Block release reason"
          required
          minLength={5}
        />
      </ActionForm>
      <ActionForm
        path={orgPath(org, `/dispatch/blocks/${block.id}/replacements`)}
        version={block.version}
        submit="Replace interval atomically"
        onDone={refresh}
        build={(f) =>
          ({
            expected_calendar_version: calendarVersion,
            expected_work_version: work.data?.version ?? null,
            reason: value(f, "reason"),
            interval: { start_at: iso(f, "start"), end_at: iso(f, "end") },
          }) satisfies Model<"M07BlockReplace">
        }
      >
        <Field
          name="start"
          label="Replacement starts (browser timezone)"
          type="datetime-local"
          required
        />
        <Field
          name="end"
          label="Replacement ends (browser timezone)"
          type="datetime-local"
          required
        />
        <TextArea
          name="reason"
          label="Block replacement reason"
          required
          minLength={5}
        />
      </ActionForm>
    </details>
  );
}

function StaffTools({
  org,
  profile,
  refresh,
}: {
  org: string;
  profile: Model<"M07DispatchTechnician">;
  refresh: () => void;
}) {
  const policy = useResource<Model<"M07DispatchPolicy">>(
    orgPath(org, "/dispatch/policy"),
  );
  const work = usePage<Model<"WorkOrder">>(orgPath(org, "/work-orders"));
  const base = orgPath(org, "/dispatch");
  return (
    <details className="disclosure">
      <summary>Manage shifts, blocks and published windows</summary>
      <Notice>
        Enter actual dated intervals. The complete arrival interval, service
        duration and buffers must fit the technician’s reviewed shift and daily
        cap.
      </Notice>
      <ActionForm
        path={base + "/shifts"}
        version={profile.profile_version!}
        submit="Add authorized dated shift"
        onDone={refresh}
        build={(f) =>
          ({
            technician_membership_id: profile.membership_id,
            expected_calendar_version: profile.calendar_version!,
            interval: { start_at: iso(f, "start"), end_at: iso(f, "end") },
            reason: value(f, "reason"),
          }) satisfies Model<"M07ShiftWrite">
        }
      >
        <Field
          name="start"
          label="Shift starts (browser timezone)"
          type="datetime-local"
          required
        />
        <Field
          name="end"
          label="Shift ends (browser timezone)"
          type="datetime-local"
          required
        />
        <TextArea
          name="reason"
          label="Shift authorization reason"
          required
          minLength={5}
        />
      </ActionForm>
      <h3>Add an availability or work block</h3>
      <ActionForm
        path={base + "/blocks"}
        version={profile.profile_version!}
        submit="Reserve explicit block"
        onDone={refresh}
        build={(f) => {
          const selected = work.data?.items.find(
            (w) => w.id === value(f, "work"),
          );
          return {
            technician_membership_id: profile.membership_id,
            expected_calendar_version: profile.calendar_version!,
            kind: selected ? "WORK_BLOCK" : "UNAVAILABLE",
            work_order_id: selected?.id ?? null,
            expected_work_version: selected?.version ?? null,
            interval: { start_at: iso(f, "start"), end_at: iso(f, "end") },
            reason_code: "UTILITY_REVIEW",
            internal_reason: value(f, "reason"),
          };
        }}
      >
        <Field
          name="start"
          label="Block starts (browser timezone)"
          type="datetime-local"
          required
        />
        <Field
          name="end"
          label="Block ends (browser timezone)"
          type="datetime-local"
          required
        />
        <Select
          name="work"
          label="Assigned work, or leave empty for unavailable time"
          required={false}
          options={(work.data?.items ?? [])
            .filter((w) => w.assignee_membership_id === profile.membership_id)
            .map((w) => ({ value: w.id, label: w.id }))}
        />
        <TextArea
          name="reason"
          label="Private block reason"
          required
          minLength={5}
        />
      </ActionForm>
      <Pager {...work} />
      <ResourceState {...policy}>
        {policy.data?.booking_enabled ? (
          <>
            <h3>Publish a visit window</h3>
            <ActionForm
              path={base + "/appointment-windows"}
              version={profile.profile_version!}
              submit="Validate and publish window"
              onDone={refresh}
              build={(f) =>
                ({
                  technician_membership_id: profile.membership_id,
                  expected_calendar_version: profile.calendar_version!,
                  expected_policy_version: policy.data!.version,
                  arrival_start: iso(f, "start"),
                  arrival_end: iso(f, "end"),
                  expected_service_minutes: Number(value(f, "duration")),
                  before_buffer_minutes: Number(value(f, "before")),
                  after_buffer_minutes: Number(value(f, "after")),
                  category_codes: [
                    value(f, "category") as Model<"M07ServiceCategory">,
                  ],
                  service_area_codes: codes(f, "areas"),
                  reason: value(f, "reason"),
                }) satisfies Model<"M07WindowPublish">
              }
            >
              <Field
                name="start"
                label="Arrival window starts (browser timezone)"
                type="datetime-local"
                required
              />
              <Field
                name="end"
                label="Arrival window ends (browser timezone)"
                type="datetime-local"
                required
              />
              <Select
                name="duration"
                label="Approved service duration in minutes"
                options={policy.data.allowed_duration_minutes.map((n) => ({
                  value: String(n),
                  label: String(n),
                }))}
              />
              <Field
                name="before"
                label="Before buffer in minutes"
                type="number"
                min={policy.data.minimum_before_buffer_minutes ?? 0}
                required
              />
              <Field
                name="after"
                label="After buffer in minutes"
                type="number"
                min={policy.data.minimum_after_buffer_minutes ?? 0}
                required
              />
              <Select
                name="category"
                label="Eligible service category"
                options={[
                  "VISIBLE_LEAK",
                  "LOW_PRESSURE",
                  "SERVICE_INTERRUPTION",
                ].map((c) => ({ value: c, label: label(c) }))}
              />
              <Field
                name="areas"
                label="Reviewed eligible service-area codes, separated by commas"
                required
              />
              <TextArea
                name="reason"
                label="Publication review reason"
                required
                minLength={5}
              />
            </ActionForm>
          </>
        ) : (
          <Notice>
            Scheduling is disabled or unconfigured. An administrator must supply
            authorized policy; no availability is generated.
          </Notice>
        )}
      </ResourceState>
    </details>
  );
}

export function DispatchBoard({
  org,
  membershipId,
  staff,
}: {
  org: string;
  membershipId: string;
  staff: boolean;
}) {
  const [range, setRange] = useState<{ from: string; to: string }>();
  const [selected, setSelected] = useState("");
  const roster = usePage<Model<"M07DispatchTechnician">>(
    staff ? orgPath(org, "/dispatch/technicians") : null,
  );
  const workload = useResource<Model<"M07WorkloadSnapshot">>(
    staff && range ? orgPath(org, "/dispatch/workload") + query(range) : null,
  );
  const windows = usePage<Model<"M07StaffWindow">>(
    staff
      ? orgPath(org, "/dispatch/appointment-windows?state=PUBLISHED")
      : null,
  );
  const profile = roster.data?.items.find((p) => p.membership_id === selected);
  const refresh = () => {
    roster.refresh();
    workload.refresh();
    windows.refresh();
  };
  return (
    <section className="panel">
      <p className="eyebrow">Utility operations · Asia/Kolkata</p>
      <h2>{staff ? "Dispatch and workload" : "My visit agenda"}</h2>
      <button className="button secondary" onClick={refresh}>
        Refresh dispatch data
      </button>
      <Notice>
        Visits are manual operational records. Scheduling requires explicit
        policy, current enrollment, shifts, eligibility and non-overlapping
        allocations.
      </Notice>
      <RangeFilter setRange={setRange} />
      {staff && (
        <ResourceState {...roster}>
          <Field name="technician_calendar" label="Technician calendar">
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
            >
              <option value="">Choose an enrolled technician…</option>
              {roster.data?.items
                .filter((p) => p.profile_version)
                .map((p) => (
                  <option key={p.membership_id} value={p.membership_id}>
                    {p.display_name} · {label(p.scheduling_health)}
                  </option>
                ))}
            </select>
          </Field>
          <Pager {...roster} />
          {profile && (
            <StaffTools org={org} profile={profile} refresh={refresh} />
          )}
        </ResourceState>
      )}
      {range && (staff ? selected : membershipId) && (
        <Calendar
          key={`${staff ? selected : membershipId}:${profile?.calendar_version ?? 0}`}
          org={org}
          member={staff ? selected : membershipId}
          range={range}
          staff={staff}
        />
      )}
      {staff && range && (
        <ResourceState {...workload}>
          <h3>Workload for the selected range</h3>
          <div
            className="table-scroll"
            role="region"
            aria-label="Technician workload"
            tabIndex={0}
          >
            <table>
              <thead>
                <tr>
                  <th>Technician</th>
                  <th>Visits</th>
                  <th>Planned minutes</th>
                  <th>Unplanned work</th>
                  <th>Health</th>
                </tr>
              </thead>
              <tbody>
                {workload.data?.items.map((w) => (
                  <tr key={w.technician_membership_id}>
                    <td>
                      {roster.data?.items.find(
                        (p) => p.membership_id === w.technician_membership_id,
                      )?.display_name ?? "Authorized technician"}
                    </td>
                    <td>{w.confirmed_appointments}</td>
                    <td>{w.planned_occupied_minutes}</td>
                    <td>{w.unplanned_work_count}</td>
                    <td>{label(w.scheduling_health)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {workload.data?.next_cursor && (
            <Notice>Narrow the range to review the complete workload.</Notice>
          )}
        </ResourceState>
      )}
      {staff && (
        <ResourceState {...windows}>
          <h3>Published windows</h3>
          {windows.data?.items.map((w) => (
            <details key={w.id} className="disclosure">
              <summary>
                {date(w.arrival_start)} – {date(w.arrival_end)}
              </summary>
              <p>
                {label(w.state)} · {w.expected_service_minutes} estimated
                service minutes
              </p>
              <ActionForm
                path={orgPath(
                  org,
                  `/dispatch/appointment-windows/${w.id}/withdrawals`,
                )}
                version={w.version}
                submit="Withdraw publication"
                onDone={refresh}
                build={(f) =>
                  ({
                    expected_calendar_version: w.calendar_version,
                    reason: value(f, "reason"),
                  }) satisfies Model<"M07WindowWithdraw">
                }
              >
                <TextArea
                  name="reason"
                  label="Window withdrawal reason"
                  required
                  minLength={5}
                />
              </ActionForm>
            </details>
          ))}
          <Pager {...windows} />
          <Link href={`/app/${org}/service-requests`}>
            Review service and appointment requests
          </Link>
        </ResourceState>
      )}
    </section>
  );
}
