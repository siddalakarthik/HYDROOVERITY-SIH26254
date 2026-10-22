"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { PublicShell } from "@/components/shells";
import {
  ActionForm,
  Badge,
  Empty,
  Field,
  Heading,
  Notice,
  ResourceState,
  useResource,
  value,
} from "@/components/ui";
import {
  api,
  clearPrivateState,
  date,
  uuid,
  type Model,
  type Page,
} from "@/lib/api";

const headings: Record<string, [string, string]> = {
  login: [
    "Sign in to your workspace",
    "Use your verified account. Your utility and roles are checked by the backend.",
  ],
  register: [
    "Create a citizen account",
    "Register with an enabled utility. Staff access is by invitation only.",
  ],
  "forgot-password": [
    "Recover your account",
    "The response is deliberately the same whether an eligible account exists or not.",
  ],
  "reset-password": [
    "Set a new password",
    "Paste the private recovery token. Resetting revokes existing authenticated sessions.",
  ],
  "verify-account": [
    "Verify your account",
    "Paste the private verification token, then sign in separately.",
  ],
  "accept-invitation": [
    "Accept your invitation",
    "Sign in as the verified invited email. The invitation binds the utility and role.",
  ],
};
export function AuthPage({
  mode,
  utility = "",
  logoutUnconfirmed = false,
}: {
  mode: string;
  utility?: string;
  logoutUnconfirmed?: boolean;
}) {
  const [done, setDone] = useState(false);
  const slug = utility;
  const uncertain = logoutUnconfirmed;
  const [title, lead] = headings[mode];
  const endpoint =
    (
      {
        "forgot-password": "recovery",
        "reset-password": "reset",
        "verify-account": "verify",
        "accept-invitation": "invitation-accept",
      } as Record<string, string>
    )[mode] ?? mode;
  return (
    <PublicShell>
      <div className="auth-grid">
        <section className="auth-story">
          <p className="eyebrow">Private development · Secure access</p>
          <h1>{title}</h1>
          <p>{lead}</p>
          <Notice>
            Verification, recovery and invitation messages currently use private
            local development files. External email delivery is not enabled.
          </Notice>
          <p className="help">
            Tokens must be pasted here, never placed in an address, screenshot
            or support message.
          </p>
        </section>
        <section aria-label={title}>
          {uncertain && (
            <Notice tone="warning">
              The local view was cleared, but server logout was not confirmed.
              Reconnect and revoke the session from your account.
            </Notice>
          )}
          {done ? (
            <>
              <h2>Request acknowledged</h2>
              <p>
                Check the private development delivery or your current account
                state. A replayed or expired token cannot be reused.
              </p>
              <div className="actions">
                <Link className="button" href="/login">
                  Sign in
                </Link>
                <Link href="/account">Check account</Link>
              </div>
            </>
          ) : (
            <ActionForm
              key={`${mode}-${slug}`}
              auth
              path={`/auth/${endpoint}`}
              submit={
                mode === "login"
                  ? "Sign in"
                  : mode === "register"
                    ? "Create citizen account"
                    : "Submit identity request"
              }
              build={(f) => {
                if (mode === "login")
                  return {
                    email: value(f, "email"),
                    password: String(f.get("password")),
                  } satisfies Model<"Login">;
                if (mode === "register")
                  return {
                    email: value(f, "email"),
                    password: String(f.get("password")),
                    display_name: value(f, "display_name"),
                    utility_slug: value(f, "utility_slug"),
                  } satisfies Model<"Register">;
                if (mode === "forgot-password")
                  return {
                    email: value(f, "email"),
                  } satisfies Model<"Recovery">;
                if (mode === "reset-password")
                  return {
                    token: value(f, "token"),
                    new_password: String(f.get("password")),
                  } satisfies Model<"Reset">;
                return {
                  token: value(f, "token"),
                } satisfies Model<"TokenAction">;
              }}
              onDone={() => {
                if (mode === "login") {
                  clearPrivateState();
                  window.location.replace("/account");
                } else {
                  if (mode === "reset-password" || mode === "accept-invitation")
                    clearPrivateState();
                  setDone(true);
                }
              }}
            >
              {mode === "register" && (
                <>
                  <Field
                    label="Utility code"
                    name="utility_slug"
                    defaultValue={slug}
                    required
                    maxLength={80}
                    pattern="[a-z0-9-]+"
                  />
                  <Field
                    label="Display name"
                    name="display_name"
                    autoComplete="name"
                    required
                    maxLength={120}
                  />
                </>
              )}
              {["login", "register", "forgot-password"].includes(mode) && (
                <Field
                  label="Email address"
                  name="email"
                  type="email"
                  autoComplete="username"
                  maxLength={254}
                  required
                />
              )}
              {[
                "reset-password",
                "verify-account",
                "accept-invitation",
              ].includes(mode) && (
                <Field
                  label="Private token"
                  name="token"
                  type="password"
                  autoComplete="off"
                  minLength={32}
                  maxLength={200}
                  required
                />
              )}
              {["login", "register", "reset-password"].includes(mode) && (
                <Field
                  label={mode === "login" ? "Password" : "New password"}
                  name="password"
                  type="password"
                  autoComplete={
                    mode === "login" ? "current-password" : "new-password"
                  }
                  minLength={mode === "login" ? 1 : 15}
                  maxLength={128}
                  required
                  help={
                    mode === "login"
                      ? "Password managers and pasting are supported."
                      : "15–128 characters. Passwords are never silently truncated."
                  }
                />
              )}
            </ActionForm>
          )}
          <nav className="auth-links" aria-label="Account help">
            <Link href="/login">Sign in</Link>
            <Link href="/register">Citizen registration</Link>
            <Link href="/forgot-password">Forgot password</Link>
            <Link href="/verify-account">Verify account</Link>
            <Link href="/accept-invitation">Accept invitation</Link>
          </nav>
        </section>
      </div>
    </PublicShell>
  );
}
export function membershipHome(m: Model<"MembershipView">) {
  const root = `/app/${uuid(m.organization_id)}`;
  if (m.roles.includes("SUPERVISOR") || m.roles.includes("ENGINEER"))
    return `${root}/overview`;
  if (m.roles.includes("TECHNICIAN")) return `${root}/work-orders`;
  if (m.roles.includes("ADMIN")) return `${root}/admin/users`;
  return `/citizen/${uuid(m.organization_id)}/reports`;
}
export function Logout() {
  const [pending, setPending] = useState(false);
  return (
    <button
      className="button secondary"
      disabled={pending}
      onClick={async () => {
        setPending(true);
        let confirmed = false;
        clearPrivateState();
        try {
          await api("/auth/logout", { method: "POST" });
          confirmed = true;
        } catch {
          /* Clear the local view without claiming server revocation. */
        } finally {
          clearPrivateState();
          window.location.replace(
            confirmed ? "/login" : "/login?logout=unconfirmed",
          );
        }
      }}
    >
      {" "}
      {pending ? "Signing out…" : "Sign out"}
    </button>
  );
}
export function AccountPage({ sessions = false }: { sessions?: boolean }) {
  const user = useResource<Model<"UserView">>("/me");
  const [cursor, setCursor] = useState<string>();
  const memberships = useResource<Page<Model<"MembershipView">>>(
    `/me/memberships?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
  );
  const sessionList = useResource<Page<Model<"SessionView">>>(
    sessions
      ? `/me/sessions?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`
      : null,
  );
  useEffect(() => {
    const onPageShow = (e: PageTransitionEvent) => {
      if (e.persisted) window.location.reload();
    };
    window.addEventListener("pageshow", onPageShow);
    return () => window.removeEventListener("pageshow", onPageShow);
  }, []);
  return (
    <PublicShell>
      <Heading
        eyebrow="Your account"
        title={sessions ? "Active sessions" : "Choose your workspace"}
        action={<Logout />}
      >
        Only current memberships and server-authorized records grant access.
      </Heading>
      <ResourceState {...user}>
        {user.data && (
          <>
            <p className="meta">
              Signed in as {user.data.display_name} · {user.data.email}
            </p>
            <div className="actions">
              <Link href="/account">Workspaces</Link>
              <Link href="/account/sessions">Manage sessions</Link>
            </div>
            {sessions ? (
              <ResourceState {...sessionList}>
                <section className="panel">
                  <h2>Your sessions</h2>
                  <ul className="record-list">
                    {sessionList.data?.items.map((s) => (
                      <li key={s.id}>
                        <div className="record-top">
                          <h3>
                            {s.current ? "This session" : "Other session"}
                          </h3>
                          <Badge>
                            {s.current ? "Current" : "Authenticated"}
                          </Badge>
                        </div>
                        <p className="meta">
                          Created {date(s.created_at)} · Idle expiry{" "}
                          {date(s.idle_expires_at)}
                        </p>
                        <ActionForm
                          path={`/me/sessions/${uuid(s.id)}`}
                          method="DELETE"
                          auth
                          build={() => undefined}
                          submit={
                            s.current ? "Revoke this session" : "Revoke session"
                          }
                          onDone={() => {
                            if (s.current) {
                              clearPrivateState();
                              window.location.replace("/login");
                            } else sessionList.refresh();
                          }}
                        />
                      </li>
                    ))}
                  </ul>
                  {sessionList.data?.next_cursor && (
                    <button
                      className="button secondary"
                      onClick={() => setCursor(sessionList.data!.next_cursor!)}
                    >
                      Next sessions
                    </button>
                  )}
                </section>
              </ResourceState>
            ) : (
              <>
                <ResourceState {...memberships}>
                  <section className="panel">
                    <h2>Utility memberships</h2>
                    {memberships.data?.items.length === 0 ? (
                      <Empty title="No active workspace yet">
                        Use an invitation or complete account verification.
                        Staff roles cannot be self-selected.
                      </Empty>
                    ) : (
                      <ul className="record-list">
                        {memberships.data?.items.map((m) => (
                          <li key={m.id}>
                            <div className="record-top">
                              <h3>{m.organization_name}</h3>
                              <Badge>{m.status}</Badge>
                            </div>
                            <p className="meta">{m.roles.join(" · ")}</p>
                            {m.status === "ACTIVE" && (
                              <Link
                                className="button secondary"
                                href={membershipHome(m)}
                                onClick={clearPrivateState}
                              >
                                Open workspace
                              </Link>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                    {memberships.data?.next_cursor && (
                      <button
                        className="button secondary"
                        onClick={() =>
                          setCursor(memberships.data!.next_cursor!)
                        }
                      >
                        Next memberships
                      </button>
                    )}
                  </section>
                </ResourceState>
                <section className="panel">
                  <h2>Profile</h2>
                  <ActionForm
                    path="/me"
                    method="PATCH"
                    auth
                    version={user.etag ?? undefined}
                    submit="Save display name"
                    build={(f) =>
                      ({
                        display_name: value(f, "display_name"),
                      }) satisfies Model<"ProfilePatch">
                    }
                    onDone={user.refresh}
                  >
                    <Field
                      label="Display name"
                      name="display_name"
                      defaultValue={user.data.display_name}
                      required
                      maxLength={120}
                    />
                  </ActionForm>
                </section>
              </>
            )}
          </>
        )}
      </ResourceState>
    </PublicShell>
  );
}
