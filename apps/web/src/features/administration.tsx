"use client";
import { useState } from "react";
import { date, label, orgPath, query, uuid, type Model } from "@/lib/api";
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
  value,
} from "@/components/ui";
import { usePage, Pager } from "@/components/pagination";

const staffRoles = ["ENGINEER", "SUPERVISOR", "TECHNICIAN", "ADMIN"];
export function Administration({ org }: { org: string }) {
  const list = usePage<Model<"MembershipView">>(orgPath(org, "/memberships"));
  return (
    <>
      <Heading eyebrow="Tenant administration" title="Members and invitations">
        Govern current utility access. Administrator access does not grant
        engineering or evaluation privileges.
      </Heading>
      <Notice>
        Governance changes require sign-in within the last 10 minutes. Changing
        roles or status revokes the affected user’s sessions. The backend
        protects the last active administrator.
      </Notice>
      <ResourceState {...list}>
        <section className="panel">
          <h2>Current membership directory</h2>
          {list.data?.items.length ? (
            <ul className="record-list">
              {list.data.items.map((m) => (
                <li key={`${m.id}-${m.version}`}>
                  <div className="record-top">
                    <h3>{m.roles.join(" · ") || "No roles"}</h3>
                    <Badge>{label(m.status)}</Badge>
                  </div>
                  <p className="meta mono">Membership ID: {m.id}</p>
                  <p className="meta">
                    {m.organization_name} · Version{" "}
                    {m.version ?? "Not supplied"}
                  </p>
                  {m.version !== undefined && (
                    <>
                      <details className="disclosure">
                        <summary>Review role changes</summary>
                        {m.roles.includes("EVALUATOR") ? (
                          <Notice>
                            Evaluation grants require a separately reviewed
                            owner procedure. This ordinary editor does not
                            modify that membership’s role set.
                          </Notice>
                        ) : (
                          <ActionForm
                            path={orgPath(
                              org,
                              `/memberships/${uuid(m.id)}/roles`,
                            )}
                            method="PUT"
                            version={m.version}
                            submit="Apply reviewed roles"
                            build={(f) =>
                              ({
                                roles: f.getAll(
                                  "roles",
                                ) as Model<"RoleWrite">["roles"],
                                reason: value(f, "role_reason"),
                              }) satisfies Model<"RoleWrite">
                            }
                            onDone={list.refresh}
                            description={`Changes affect membership ${m.id} and revoke its user sessions.`}
                          >
                            {[...staffRoles, "CITIZEN"].map((role) => (
                              <div className="checkbox-row" key={role}>
                                <input
                                  type="checkbox"
                                  id={`role-${m.id}-${role}`}
                                  name="roles"
                                  value={role}
                                  defaultChecked={m.roles.includes(role)}
                                />
                                <label htmlFor={`role-${m.id}-${role}`}>
                                  {role}
                                </label>
                              </div>
                            ))}
                            <TextArea
                              name="role_reason"
                              label="Reason for role changes"
                              minLength={10}
                              maxLength={1000}
                            />
                            <div className="checkbox-row">
                              <input
                                type="checkbox"
                                id={`confirm-roles-${m.id}`}
                                required
                              />
                              <label htmlFor={`confirm-roles-${m.id}`}>
                                I reviewed the access consequences and session
                                revocation.
                              </label>
                            </div>
                          </ActionForm>
                        )}
                      </details>
                      <details className="disclosure">
                        <summary>Review membership status</summary>
                        <ActionForm
                          path={orgPath(
                            org,
                            `/memberships/${uuid(m.id)}/status`,
                          )}
                          version={m.version}
                          submit="Apply reviewed status"
                          build={(f) =>
                            ({
                              status: value(
                                f,
                                "member_status",
                              ) as Model<"MemberStatusWrite">["status"],
                              reason: value(f, "status_reason"),
                            }) satisfies Model<"MemberStatusWrite">
                          }
                          onDone={list.refresh}
                        >
                          <Select
                            name="member_status"
                            label="Membership status"
                            options={[
                              { value: "ACTIVE", label: "Active" },
                              { value: "SUSPENDED", label: "Suspended" },
                            ]}
                            defaultValue={m.status}
                          />
                          <TextArea
                            name="status_reason"
                            label="Reason for membership status"
                            minLength={10}
                            maxLength={1000}
                          />
                          <div className="checkbox-row">
                            <input
                              type="checkbox"
                              id={`confirm-status-${m.id}`}
                              required
                            />
                            <label htmlFor={`confirm-status-${m.id}`}>
                              I reviewed this membership and the session
                              revocation.
                            </label>
                          </div>
                        </ActionForm>
                      </details>
                    </>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <Empty title="No permitted memberships" />
          )}
          <Pager {...list} />
        </section>
      </ResourceState>
      <section className="panel">
        <h2>Invite a staff member</h2>
        <ActionForm
          path={orgPath(org, "/invitations")}
          submit="Create invitation"
          build={(f) =>
            ({
              email: value(f, "invite_email"),
              role: value(f, "invite_role") as Model<"InviteWrite">["role"],
            }) satisfies Model<"InviteWrite">
          }
          description="Creates a 30-minute invitation in private development delivery. It does not send external email or grant access before verified acceptance."
          onDone={list.refresh}
        >
          <Field
            name="invite_email"
            label="Invited email address"
            type="email"
            maxLength={254}
            required
          />
          <Select
            name="invite_role"
            label="Exact invited role"
            options={staffRoles.map((value) => ({
              value,
              label: label(value),
            }))}
          />
        </ActionForm>
      </section>
    </>
  );
}
export function Audit({ org }: { org: string }) {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [filterError, setFilterError] = useState("");
  const list = usePage<Model<"AuditEvent">>(
    orgPath(org, "/audit-logs") + query(filters),
  );
  return (
    <>
      <Heading eyebrow="Tenant administration" title="Audit history">
        Safe action and resource identifiers. No secret payloads or raw personal
        records.
      </Heading>
      <form
        className="filter-bar"
        onSubmit={(e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          const from = value(f, "from"),
            to = value(f, "to");
          if (Boolean(from) !== Boolean(to)) {
            setFilterError("Supply both UTC date boundaries.");
            return;
          }
          if (from && to) {
            const a = Date.parse(from + "Z"),
              b = Date.parse(to + "Z");
            if (
              !Number.isFinite(a) ||
              !Number.isFinite(b) ||
              b <= a ||
              b - a > 31 * 86400000
            ) {
              setFilterError(
                "Choose ordered UTC boundaries no more than 31 days apart.",
              );
              return;
            }
          }
          setFilterError("");
          setFilters({
            ...(value(f, "action") ? { action: value(f, "action") } : {}),
            ...(from && to
              ? {
                  from_time: new Date(from + "Z").toISOString(),
                  to_time: new Date(to + "Z").toISOString(),
                }
              : {}),
          });
        }}
      >
        <Field name="action" label="Action code (optional)" maxLength={100} />
        <Field
          name="from"
          label="From (UTC, optional pair)"
          type="datetime-local"
        />
        <Field
          name="to"
          label="To (UTC, optional pair)"
          type="datetime-local"
        />
        <button className="button secondary">Apply filters</button>
      </form>
      {filterError && (
        <div role="alert" className="error-panel">
          {filterError}
        </div>
      )}
      <Notice>
        For time filtering, supply both ordered UTC boundaries within 31 days.
        The backend validates the range.
      </Notice>
      <ResourceState {...list}>
        <section className="panel">
          {list.data?.items.length ? (
            <div
              className="table-scroll"
              tabIndex={0}
              role="region"
              aria-label="Audit records"
            >
              <table>
                <caption className="help">
                  Authorized audit records on the current page
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Action</th>
                    <th scope="col">Resource</th>
                    <th scope="col">Timestamp (IST)</th>
                    <th scope="col">Request ID</th>
                  </tr>
                </thead>
                <tbody>
                  {list.data.items.map((a) => (
                    <tr key={a.id}>
                      <td>{a.action}</td>
                      <td>
                        {a.resource_type}
                        <br />
                        <span className="mono">
                          {a.resource_id ?? "Not recorded"}
                        </span>
                      </td>
                      <td>{date(a.occurred_at)}</td>
                      <td className="mono">{a.request_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Empty title="No audit records in this view" />
          )}
          <Pager {...list} />
        </section>
      </ResourceState>
    </>
  );
}
