"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Menu,
  X,
  LayoutDashboard,
  Network,
  ClipboardList,
  HardHat,
  MessageSquare,
  Users,
  ScrollText,
  Settings,
  User,
} from "lucide-react";
import {
  api,
  ApiError,
  clearPrivateState,
  orgPath,
  type Model,
  type Page,
} from "@/lib/api";
import { Wordmark } from "@/components/shells";
import {
  Badge,
  ErrorPanel,
  Field,
  Heading,
  Notice,
  ResourceState,
  useResource,
} from "@/components/ui";
import { Logout, membershipHome } from "./auth";
import { CitizenReports, SupervisorComplaints } from "./complaints";
import { Overview, Incidents, IncidentDetail } from "./incidents";
import { WorkOrders, WorkDetail, VerificationPage } from "./work";
import { NetworkPage } from "./network";
import { Administration, Audit } from "./administration";
import routes from "../lib/route-capabilities.json";

function useMemberships() {
  const [state, setState] = useState<{
    data?: Model<"MembershipView">[];
    error?: unknown;
    loading: boolean;
  }>({ loading: true });
  useEffect(() => {
    const controller = new AbortController();
    let signature = "";
    const load = async () => {
      try {
        const items: Model<"MembershipView">[] = [];
        let cursor: string | null = null;
        do {
          const result: {
            data: Page<Model<"MembershipView">>;
            etag: string | null;
          } = await api<Page<Model<"MembershipView">>>(
            `/me/memberships?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
            { signal: controller.signal },
          );
          items.push(...result.data.items);
          cursor = result.data.next_cursor;
        } while (cursor);
        signature = JSON.stringify(items);
        if (!controller.signal.aborted)
          setState({ data: items, loading: false });
      } catch (error) {
        if (!controller.signal.aborted) setState({ error, loading: false });
      }
    };
    void load();
    const clear = () => {
      controller.abort();
      setState({
        loading: false,
        error: new ApiError(
          401,
          "SESSION_CHANGED",
          "Session or membership changed. Sign in to reload current access.",
        ),
      });
    };
    const check = async () => {
      try {
        await api("/me");
        const items: Model<"MembershipView">[] = [];
        let cursor: string | null = null;
        do {
          const response: {
            data: Page<Model<"MembershipView">>;
            etag: string | null;
          } = await api<Page<Model<"MembershipView">>>(
            `/me/memberships?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
          );
          items.push(...response.data.items);
          cursor = response.data.next_cursor;
        } while (cursor);
        if (signature && JSON.stringify(items) !== signature)
          clearPrivateState();
      } catch {
        clear();
      }
    };
    window.addEventListener("hydro:scope-cleared", clear);
    window.addEventListener("focus", check);
    const timer = setInterval(check, 30000);
    const onPageShow = (e: PageTransitionEvent) => {
      if (e.persisted) window.location.reload();
    };
    window.addEventListener("pageshow", onPageShow);
    return () => {
      controller.abort();
      clearInterval(timer);
      window.removeEventListener("hydro:scope-cleared", clear);
      window.removeEventListener("focus", check);
      window.removeEventListener("pageshow", onPageShow);
    };
  }, []);
  return state;
}
const navItems = [
  {
    suffix: "overview",
    label: "Overview",
    roles: ["ENGINEER", "SUPERVISOR"],
    icon: LayoutDashboard,
  },
  {
    suffix: "network",
    label: "Network",
    roles: ["ENGINEER", "SUPERVISOR"],
    icon: Network,
  },
  {
    suffix: "incidents",
    label: "Incidents",
    roles: ["ENGINEER", "SUPERVISOR"],
    icon: ClipboardList,
  },
  {
    suffix: "work-orders",
    label: "Work orders",
    roles: ["ENGINEER", "SUPERVISOR", "TECHNICIAN"],
    icon: HardHat,
  },
  {
    suffix: "complaints",
    label: "Citizen reports",
    roles: ["SUPERVISOR"],
    icon: MessageSquare,
  },
  {
    suffix: "admin/users",
    label: "Members & invitations",
    roles: ["ADMIN"],
    icon: Users,
  },
  {
    suffix: "admin/settings",
    label: "Organization information",
    roles: ["ADMIN"],
    icon: Settings,
  },
  {
    suffix: "admin/audit",
    label: "Audit history",
    roles: ["ADMIN"],
    icon: ScrollText,
  },
];
export function Workspace({ segments }: { segments: string[] }) {
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    if (mobile) document.querySelector<HTMLElement>(".sidebar nav a")?.focus();
  }, [mobile]);
  const [scope, org, ...tail] = segments;
  const memberships = useMemberships();
  const suffix = tail.join("/");
  const validOrg =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      org ?? "",
    );
  const organization = useResource<Model<"OrganizationView">>(
    validOrg ? orgPath(org) : null,
  );
  const route = routes.pages.find((p) =>
    new RegExp(
      "^" +
        p.route.replaceAll("{org}", "[^/]+").replaceAll("{id}", "[^/]+") +
        "$",
    ).test("/" + segments.join("/")),
  );
  const member = memberships.data?.find(
    (m) => m.organization_id === org && m.status === "ACTIVE",
  );
  if (!validOrg || !route)
    return (
      <main id="main" className="public-main">
        <h1>Page unavailable</h1>
        <Link href="/account">My account</Link>
      </main>
    );
  if (memberships.loading)
    return (
      <main id="main" className="public-main" role="status">
        Checking current membership…
      </main>
    );
  if (memberships.error)
    return (
      <main id="main" className="public-main">
        <ErrorPanel error={memberships.error} />
      </main>
    );
  if (
    !member ||
    !route.roles.split(",").some((r) => member.roles.includes(r) || r === "ALL")
  )
    return (
      <main id="main" className="public-main">
        <h1>Workspace unavailable</h1>
        <p>A current permitted utility membership is required.</p>
        <Link href="/account">Choose an authorized workspace</Link>
      </main>
    );
  const root = `/app/${org}`;
  const common = { org, roles: member.roles };
  const content = () => {
    if (route.status === "DEFERRED")
      return (
        <>
          <Heading eyebrow="Not enabled" title={route.title}>
            This capability depends on deferred backend operations.
          </Heading>
          <Notice>
            Hardware connection, monitoring, scientific integration and offline
            synchronization are pending. No records or successful actions are
            fabricated here.
          </Notice>
        </>
      );
    if (scope === "citizen")
      return <CitizenReports org={org} rest={tail.slice(1)} />;
    if (suffix === "overview") return <Overview {...common} />;
    if (suffix === "network") return <NetworkPage {...common} />;
    if (tail[0] === "incidents")
      return tail[1] ? (
        <IncidentDetail {...common} id={tail[1]} />
      ) : (
        <Incidents {...common} />
      );
    if (tail[0] === "work-orders")
      return tail[1] ? (
        <WorkDetail {...common} membershipId={member.id} id={tail[1]} />
      ) : (
        <WorkOrders {...common} />
      );
    if (tail[0] === "repairs" && tail[2] === "verification")
      return <VerificationPage {...common} id={tail[1]} />;
    if (suffix === "complaints") return <SupervisorComplaints org={org} />;
    if (suffix === "admin/users") return <Administration org={org} />;
    if (suffix === "admin/audit") return <Audit org={org} />;
    return (
      <>
        <Heading eyebrow="Read only" title="Organization information" />
        <dl className="details-grid">
          <div>
            <dt>Name</dt>
            <dd>{organization.data?.name}</dd>
          </div>
          <div>
            <dt>Public utility code</dt>
            <dd>{organization.data?.public_slug}</dd>
          </div>
        </dl>
        <Notice>
          Organization settings edits and integrations are not enabled. Account
          profile edits are available from My account.
        </Notice>
      </>
    );
  };
  return (
    <div className="workspace">
      <aside
        className={`sidebar${mobile ? " open" : ""}`}
        onKeyDown={(e) => {
          if (e.key === "Escape") {
            setMobile(false);
            document
              .querySelector<HTMLButtonElement>(
                ".workspace-header .menu-toggle",
              )
              ?.focus();
          }
        }}
      >
        <Wordmark />
        <nav aria-label="Workspace navigation">
          {scope === "citizen" ? (
            <>
              <Link
                href={`/citizen/${org}/reports`}
                aria-current={suffix === "reports" ? "page" : undefined}
              >
                <MessageSquare size={18} aria-hidden="true" />
                My reports
              </Link>
              <Link
                href={`/citizen/${org}/reports/new`}
                aria-current={suffix === "reports/new" ? "page" : undefined}
              >
                New report
              </Link>
            </>
          ) : (
            navItems
              .filter((n) => n.roles.some((r) => member.roles.includes(r)))
              .map((n) => (
                <Link
                  key={n.suffix}
                  href={`${root}/${n.suffix}`}
                  aria-current={
                    suffix === n.suffix || suffix.startsWith(n.suffix + "/")
                      ? "page"
                      : undefined
                  }
                >
                  <n.icon size={18} aria-hidden="true" />
                  {n.label}
                </Link>
              ))
          )}
          {scope !== "citizen" && member.roles.includes("CITIZEN") && (
            <Link href={`/citizen/${org}/reports`}>My resident reports</Link>
          )}
          {scope === "citizen" &&
            member.roles.some((r) =>
              ["ENGINEER", "SUPERVISOR", "TECHNICIAN", "ADMIN"].includes(r),
            ) && <Link href={membershipHome(member)}>Team workspace</Link>}
          <Link href="/account">
            <User size={18} aria-hidden="true" />
            My account
          </Link>
        </nav>
        <div className="sidebar-bottom">
          <p className="meta">Team TARK · SIH26254</p>
          <p className="help">Hardware connection pending</p>
          <Link href="/">Public website</Link>
        </div>
      </aside>
      <div className="workspace-body">
        <header className="workspace-header">
          <button
            type="button"
            className="icon-button menu-toggle"
            aria-label={
              mobile
                ? "Close workspace navigation"
                : "Open workspace navigation"
            }
            aria-expanded={mobile}
            onClick={() => setMobile(!mobile)}
          >
            {mobile ? <X /> : <Menu />}
          </button>
          <Field name="organization" label="Utility workspace">
            <select
              id="organization"
              value={org}
              onChange={(e) => {
                const next = memberships.data?.find(
                  (m) => m.organization_id === e.target.value,
                );
                if (next) {
                  clearPrivateState();
                  window.location.assign(membershipHome(next));
                }
              }}
            >
              {memberships.data
                ?.filter((m) => m.status === "ACTIVE")
                .map((m) => (
                  <option value={m.organization_id} key={m.id}>
                    {m.organization_name}
                  </option>
                ))}
            </select>
          </Field>
          <Badge>{member.roles.join(" · ")}</Badge>
          <Logout />
        </header>
        <main id="main" className="workspace-content">
          <p className="breadcrumbs">
            <Link href="/account">Account</Link> /{" "}
            {organization.data?.name ?? "Utility"} / {route.title}
          </p>
          <ResourceState {...organization}>
            <Notice>
              Operational record workspace · Manual reports and work receipts.
              No live sensor measurements are connected.
            </Notice>
            <div key={`${org}-${suffix}`}>{content()}</div>
          </ResourceState>
        </main>
      </div>
    </div>
  );
}
