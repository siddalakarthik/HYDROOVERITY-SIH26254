import { test, expect, type BrowserContext, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
const fixture = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as {
  password: string;
  other_complaint: string;
  org: string;
  other_org: string;
  zone: string;
  tech_membership: string;
  other_tech_membership: string;
  work_order: string;
  incident: string;
  pipe: string;
  junctions: string[];
};
const output = process.env.HYDRO_M04_SCREENSHOTS;
if (!output)
  throw new Error("Set a dedicated synthetic screenshot output directory.");
mkdirSync(output, { recursive: true });
async function capture(page: Page, name: string) {
  await page.screenshot({ path: join(output!, `${name}.png`), fullPage: true });
}
async function a11y(page: Page) {
  const result = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(
    result.violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.map((n) => n.target),
    })),
  ).toEqual([]);
}
async function login(page: Page, email: string) {
  await page.goto("/login");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(fixture.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Choose your workspace" }),
  ).toBeVisible();
  await expect(
    page.getByText("SYNTHETIC integration utility A", { exact: true }),
  ).toBeVisible();
}
async function raw(
  page: Page,
  path: string,
  method = "GET",
  body?: unknown,
  extra: Record<string, string> = {},
) {
  return page.evaluate(
    async ({ path, method, body, extra }) => {
      const h: Record<string, string> = { ...extra };
      if (body !== undefined) h["Content-Type"] = "application/json";
      if (method !== "GET" && !Object.hasOwn(extra, "X-CSRF-Token")) {
        const c = await fetch("/api/v1/auth/csrf", { cache: "no-store" });
        h["X-CSRF-Token"] = (await c.json()).csrf_token;
      }
      const r = await fetch("/api/v1" + path, {
        method,
        headers: h,
        body: body === undefined ? undefined : JSON.stringify(body),
        cache: "no-store",
      });
      return {
        status: r.status,
        headers: Object.fromEntries(r.headers.entries()),
        data: await r.json(),
      };
    },
    { path, method, body, extra },
  );
}
test("real resident-to-independent-review workflow, denial cases, mobile and accessible layouts", async ({
  browser,
}) => {
  const consoleErrors: string[] = [];
  const expectedHttpDenials: string[] = [];
  function observe(page: Page) {
    page.on("pageerror", (error) => consoleErrors.push(error.message));
    page.on("console", (message) => {
      if (message.type() !== "error") return;
      const text = message.text();
      if (
        /^Failed to load resource: the server responded with a status of (400|401|403|404|409|412|422|428|429)\b/.test(
          text,
        )
      )
        expectedHttpDenials.push(text);
      else consoleErrors.push(text);
    });
  }
  const contexts: BrowserContext[] = [];
  async function actor(email: string) {
    const c = await browser.newContext({
      baseURL: "https://localhost:8443",
      viewport: { width: 1440, height: 1000 },
      ignoreHTTPSErrors: false,
    });
    contexts.push(c);
    const p = await c.newPage();
    observe(p);
    await login(p, email);
    return p;
  }
  const publicContext = await browser.newContext({
    baseURL: "https://localhost:8443",
    viewport: { width: 1374, height: 1145 },
  });
  contexts.push(publicContext);
  const publicPage = await publicContext.newPage();
  observe(publicPage);
  await publicPage.goto("/");
  await expect(
    publicPage.getByRole("heading", {
      name: "Evidence before conclusions",
      exact: true,
    }),
  ).toBeVisible();
  await capture(publicPage, "home-desktop");
  await a11y(publicPage);
  await publicPage.goto("/how-it-works");
  await capture(publicPage, "how-it-works-desktop");
  await a11y(publicPage);
  await publicPage.goto("/login");
  await capture(publicPage, "login-desktop");
  await a11y(publicPage);
  for (const width of [360, 390, 640, 768, 1024, 1280, 1440, 1920]) {
    await publicPage.setViewportSize({ width, height: 900 });
    await publicPage.goto("/");
    expect(
      await publicPage.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    if (width === 390) {
      await publicPage.getByRole("button", { name: "Open navigation" }).click();
      await expect(
        publicPage.getByRole("navigation", { name: "Main navigation" }),
      ).toBeVisible();
      await capture(publicPage, "home-mobile-menu");
      await a11y(publicPage);
    }
  }
  const citizen = await actor("citizen@example.invalid");
  await citizen.goto(`/citizen/${fixture.org}/reports/new`);
  await citizen.getByLabel("Issue category").selectOption("VISIBLE_LEAK");
  await citizen
    .getByLabel("Describe the issue")
    .fill(
      "SYNTHETIC browser report: wetness observed for integration testing only.",
    );
  await citizen.getByLabel("Rough area or landmark").fill("SYNTHETIC locality");
  await capture(citizen, "citizen-report-form-desktop");
  await a11y(citizen);
  await citizen.getByRole("button", { name: "Submit report" }).click();
  await expect(
    citizen.getByRole("heading", { name: "Your report", exact: true }),
  ).toBeVisible();
  const complaintId = new URL(citizen.url()).pathname.split("/").at(-1)!;
  const tracking = await citizen.locator(".record-top h2").innerText();
  await citizen
    .getByLabel("What has changed?")
    .fill("SYNTHETIC follow-up retained in public-safe history.");
  await citizen.getByRole("button", { name: "Send follow-up" }).click();
  await expect(
    citizen
      .getByText("SYNTHETIC follow-up retained in public-safe history.", {
        exact: true,
      })
      .first(),
  ).toBeVisible();
  await citizen.goto(`/citizen/${fixture.org}/reports`);
  await capture(citizen, "citizen-reports-desktop");
  await expect(citizen.getByRole("link", { name: tracking })).toBeVisible();
  expect((await raw(citizen, `/orgs/${fixture.org}/pipes`)).status).toBe(403);
  expect(
    (await raw(citizen, `/orgs/${fixture.other_org}/complaints`)).status,
  ).toBe(404);
  await citizen.setViewportSize({ width: 390, height: 844 });
  await capture(citizen, "citizen-reports-mobile");
  await a11y(citizen);
  expect(
    (
      await raw(
        citizen,
        `/orgs/${fixture.org}/complaints/${fixture.other_complaint}`,
      )
    ).status,
  ).toBe(404);
  const supervisor = await actor("supervisor@example.invalid");
  await supervisor.goto(`/app/${fixture.org}/overview`);
  await expect(
    supervisor.getByRole("heading", { name: "Operations overview" }),
  ).toBeVisible();
  await capture(supervisor, "supervisor-overview-desktop");
  await a11y(supervisor);
  await supervisor.goto(`/app/${fixture.org}/incidents`);
  await supervisor.getByText("Create an incident", { exact: true }).click();
  await supervisor.getByLabel("Authorized zone").selectOption(fixture.zone);
  await supervisor
    .getByLabel("Incident title")
    .fill("SYNTHETIC browser investigation concern");
  await supervisor
    .locator("form")
    .filter({
      has: supervisor.getByRole("button", {
        name: "Create incident",
        exact: true,
      }),
    })
    .getByLabel("Severity", { exact: true })
    .selectOption("MEDIUM");
  await supervisor
    .getByRole("button", { name: "Create incident", exact: true })
    .click();
  await expect(
    supervisor.getByRole("heading", {
      name: "SYNTHETIC browser investigation concern",
      exact: true,
    }),
  ).toBeVisible();
  const incidentId = new URL(supervisor.url()).pathname.split("/").at(-1)!;
  for (const target of ["UNDER_REVIEW", "ACCEPTED"]) {
    await supervisor.getByLabel("Next lifecycle state").selectOption(target);
    await supervisor
      .getByLabel("Reason for this transition")
      .fill("SYNTHETIC supervisor review for browser integration testing.");
    await supervisor
      .getByRole("button", { name: "Record transition", exact: true })
      .click();
    await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
      target === "UNDER_REVIEW" ? "Under review" : "Accepted",
    );
  }
  await capture(supervisor, "incident-detail-desktop");
  await a11y(supervisor);
  await supervisor.goto(`/app/${fixture.org}/complaints`);
  await supervisor.getByRole("button", { name: tracking, exact: true }).click();
  await supervisor.getByLabel("Public status").selectOption("INVESTIGATING");
  await supervisor
    .getByLabel("Message visible to the resident")
    .fill("SYNTHETIC investigation planned; no confirmed leak claim.");
  await supervisor.getByLabel("Incident ID (optional)").fill(incidentId);
  await supervisor
    .getByLabel("Private review reason")
    .fill(
      "SYNTHETIC private reason that must never appear in citizen projections.",
    );
  await supervisor.getByRole("button", { name: "Publish safe update" }).click();
  await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
    "Investigating",
  );
  const safe = await raw(
    citizen,
    `/orgs/${fixture.org}/complaints/${complaintId}`,
  );
  expect(safe.status).toBe(200);
  expect(JSON.stringify(safe.data)).not.toContain("private reason");
  expect(JSON.stringify(safe.data)).not.toContain(incidentId);
  await supervisor.goto(`/app/${fixture.org}/work-orders`);
  await supervisor.getByText("Create a work order", { exact: true }).click();
  await supervisor.getByLabel("Reviewed incident").selectOption(incidentId);
  await supervisor
    .getByLabel("Priority", { exact: true })
    .selectOption("MEDIUM");
  await supervisor
    .getByLabel("Visit instructions")
    .fill(
      "SYNTHETIC browser task: document observations; no physical work is authorized.",
    );
  await supervisor
    .getByRole("button", { name: "Create work order", exact: true })
    .click();
  await expect(
    supervisor.getByRole("heading", {
      name: "Investigation and repair record",
    }),
  ).toBeVisible();
  const workId = new URL(supervisor.url()).pathname.split("/").at(-1)!;
  await supervisor
    .getByText("Assign or reassign technician", { exact: true })
    .click();
  await supervisor
    .getByLabel("Technician membership ID")
    .fill(fixture.tech_membership);
  await supervisor
    .getByLabel("Assignment reason", { exact: true })
    .fill("SYNTHETIC authorized browser assignment.");
  await supervisor
    .getByRole("button", { name: "Record assignment", exact: true })
    .click();
  await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
    "Assigned",
  );
  await capture(supervisor, "work-order-supervisor-desktop");
  await supervisor.goto(`/app/${fixture.org}/incidents/${incidentId}`);
  await supervisor
    .getByLabel("Next lifecycle state")
    .selectOption("IN_PROGRESS");
  await supervisor
    .getByLabel("Reason for this transition")
    .fill("SYNTHETIC assigned work begins after reviewed triage.");
  await supervisor
    .getByRole("button", { name: "Record transition", exact: true })
    .click();
  await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
    "In progress",
  );
  const technician = await actor("technician@example.invalid");
  await technician.setViewportSize({ width: 390, height: 844 });
  await technician.goto(`/app/${fixture.org}/work-orders/${workId}`);
  await expect(
    technician.getByRole("heading", { name: "Assigned-task brief" }),
  ).toBeVisible();
  for (const target of ["ACCEPTED", "IN_PROGRESS"]) {
    await technician.getByLabel("Next work state").selectOption(target);
    await technician
      .getByLabel("Reason for work transition")
      .fill("SYNTHETIC technician browser step.");
    await technician
      .getByRole("button", { name: "Record work transition" })
      .click();
    await expect(technician.locator(".record-top .badge").first()).toHaveText(
      target === "ACCEPTED" ? "Accepted" : "In progress",
    );
  }
  await capture(technician, "technician-task-mobile");
  await a11y(technician);
  expect((await raw(technician, `/orgs/${fixture.org}/pipes`)).status).toBe(
    403,
  );
  await technician
    .getByLabel("Inspection note", { exact: true })
    .fill(
      "SYNTHETIC inspection note; no sensor measurement or physical experiment.",
    );
  await technician
    .getByRole("button", { name: "Save inspection note" })
    .click();
  await expect(
    technician.getByRole("heading", { name: "Record a repair receipt" }),
  ).toBeVisible();
  await technician
    .getByLabel("Work performed and limitations")
    .fill(
      "SYNTHETIC repair receipt for persistent UI workflow testing only, not physical work.",
    );
  await technician.getByRole("button", { name: "Save repair receipt" }).click();
  await expect(
    technician.getByRole("link", { name: "Review verification history" }),
  ).toBeVisible();
  const repairHref = await technician
    .getByRole("link", { name: "Review verification history" })
    .getAttribute("href");
  await technician
    .getByLabel("Next work state")
    .selectOption("SUBMITTED_FOR_REVIEW");
  await technician
    .getByLabel("Reason for work transition")
    .fill("SYNTHETIC submission for independent review.");
  await technician
    .getByRole("button", { name: "Record work transition" })
    .click();
  await expect(technician.locator(".record-top .badge").first()).toHaveText(
    "Submitted for review",
  );
  await supervisor.goto(`/app/${fixture.org}/work-orders/${workId}`);
  await supervisor.getByLabel("Next work state").selectOption("COMPLETED");
  await supervisor
    .getByLabel("Reason for work transition")
    .fill(
      "SYNTHETIC supervisor accepts submitted work, not scientific verification.",
    );
  await supervisor
    .getByRole("button", { name: "Record work transition" })
    .click();
  await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
    "Completed",
  );
  await supervisor.goto(`/app/${fixture.org}/incidents/${incidentId}`);
  await supervisor
    .getByLabel("Next lifecycle state")
    .selectOption("VERIFICATION_PENDING");
  await supervisor
    .getByLabel("Reason for this transition")
    .fill("SYNTHETIC submitted repair awaits independent evidence review.");
  await supervisor
    .getByRole("button", { name: "Record transition", exact: true })
    .click();
  await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
    "Verification pending",
  );
  await supervisor.goto(repairHref!);
  await supervisor
    .getByLabel("Missing comparability and evidence")
    .fill(
      "No comparable measured pressure, supply, calibration or before/after windows exist in this synthetic workflow.",
    );
  await supervisor
    .getByLabel("Independent reviewer reason")
    .fill("SYNTHETIC independent review cannot establish repair performance.");
  await supervisor
    .getByRole("button", { name: "Record NOT_VERIFIABLE" })
    .click();
  await expect(
    supervisor.getByRole("heading", { name: "Not verifiable", exact: true }),
  ).toBeVisible();
  await capture(supervisor, "verification-desktop");
  await a11y(supervisor);
  await supervisor.goto(`/app/${fixture.org}/incidents/${incidentId}`);
  await supervisor
    .getByLabel("Next lifecycle state")
    .selectOption("NOT_VERIFIABLE");
  await supervisor
    .getByLabel("Reason for this transition")
    .fill("SYNTHETIC evidence remains insufficient despite work completion.");
  await supervisor
    .getByRole("button", { name: "Record transition", exact: true })
    .click();
  await expect(supervisor.locator(".record-top .badge").first()).toHaveText(
    "Not verifiable",
  );
  await technician.goto(repairHref!);
  await expect(
    technician.getByRole("button", { name: "Record NOT_VERIFIABLE" }),
  ).toHaveCount(0);
  const engineer = await actor("engineer@example.invalid");
  await engineer.goto(`/app/${fixture.org}/network`);
  await expect(
    engineer.getByRole("heading", { name: "Network explorer" }),
  ).toBeVisible();
  await expect(engineer.locator(".map-canvas canvas")).toBeVisible();
  await capture(engineer, "network-desktop");
  await a11y(engineer);
  await engineer.setViewportSize({ width: 390, height: 844 });
  await capture(engineer, "network-mobile");
  expect(
    await engineer.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await a11y(engineer);
  expect((await raw(engineer, `/orgs/${fixture.other_org}/pipes`)).status).toBe(
    404,
  );
  const admin = await actor("admin-a@example.invalid");
  await admin.goto(`/app/${fixture.org}/admin/users`);
  await capture(admin, "administration-desktop");
  await a11y(admin);
  await admin.goto(`/app/${fixture.org}/admin/audit`);
  await expect(admin.getByRole("table")).toBeVisible();
  await capture(admin, "audit-desktop");
  await a11y(admin);
  const cookie = (await admin.context().cookies()).find(
    (c) => c.name === "__Host-hydro_session",
  );
  expect(cookie).toMatchObject({
    secure: true,
    httpOnly: true,
    sameSite: "Lax",
    path: "/",
  });
  const base = `/orgs/${fixture.org}`;
  const current = (await raw(supervisor, `${base}/incidents/${incidentId}`))
    .data;
  const badCsrf = await raw(
    supervisor,
    `${base}/incidents/${incidentId}/transitions`,
    "POST",
    { target: "UNDER_REVIEW", reason: "SYNTHETIC missing CSRF rejection." },
    {
      "X-CSRF-Token": "",
      "Idempotency-Key": crypto.randomUUID(),
      "If-Match": `"${current.version}"`,
    },
  );
  expect(badCsrf.status).toBe(403);
  const missingKey = await raw(
    supervisor,
    `${base}/incidents/${incidentId}/transitions`,
    "POST",
    {
      target: "UNDER_REVIEW",
      reason: "SYNTHETIC missing idempotency rejection.",
    },
    { "If-Match": `"${current.version}"` },
  );
  expect(missingKey.status).toBe(400);
  const stale = await raw(
    supervisor,
    `${base}/incidents/${incidentId}/transitions`,
    "POST",
    { target: "UNDER_REVIEW", reason: "SYNTHETIC stale version rejection." },
    { "Idempotency-Key": crypto.randomUUID(), "If-Match": '"0"' },
  );
  expect(stale.status).toBe(412);
  const noMatch = await raw(
    supervisor,
    `${base}/incidents/${incidentId}/transitions`,
    "POST",
    {
      target: "UNDER_REVIEW",
      reason: "SYNTHETIC missing precondition rejection.",
    },
    { "Idempotency-Key": crypto.randomUUID() },
  );
  expect(noMatch.status).toBe(428);
  const key = crypto.randomUUID(),
    body = {
      title: "SYNTHETIC idempotency check",
      zone_id: fixture.zone,
      severity: "LOW",
      assessment_ids: [],
      workspace_mode: "OPERATIONAL",
      simulation_run_id: null,
    };
  const first = await raw(supervisor, `${base}/incidents`, "POST", body, {
    "Idempotency-Key": key,
  });
  expect(first.status).toBe(201);
  const repeated = await raw(supervisor, `${base}/incidents`, "POST", body, {
    "Idempotency-Key": key,
  });
  expect(repeated.data.id).toBe(first.data.id);
  const changed = await raw(
    supervisor,
    `${base}/incidents`,
    "POST",
    { ...body, title: "SYNTHETIC changed body" },
    { "Idempotency-Key": key },
  );
  expect(changed.status).toBe(409);
  const invalid = await raw(
    supervisor,
    `${base}/incidents`,
    "POST",
    { ...body, title: "x" },
    { "Idempotency-Key": crypto.randomUUID() },
  );
  expect(invalid.status).toBe(422);
  expect(
    await citizen.evaluate(() => localStorage.length + sessionStorage.length),
  ).toBe(0);
  expect(
    (await raw(citizen, "/public/project-status")).headers["cache-control"],
  ).toBe("no-store");
  // A forged Origin reaches the same real API through browser interception.
  await supervisor.route("**/api/v1/me", async (route) =>
    route.continue({
      headers: { ...route.request().headers(), origin: "https://evil.invalid" },
    }),
  );
  expect(
    (
      await raw(
        supervisor,
        "/me",
        "PATCH",
        { display_name: "SYNTHETIC rejected origin" },
        { "If-Match": '"1"' },
      )
    ).status,
  ).toBe(403);
  await supervisor.unroute("**/api/v1/me");
  const seededWork = (
    await raw(supervisor, `${base}/work-orders/${fixture.work_order}`)
  ).data;
  expect(
    (
      await raw(
        supervisor,
        `${base}/work-orders/${fixture.work_order}/assignment`,
        "POST",
        {
          assignee_membership_id: fixture.other_tech_membership,
          due_at: null,
          reason:
            "SYNTHETIC reassignment invalidates the former technician's task access.",
        },
        {
          "Idempotency-Key": crypto.randomUUID(),
          "If-Match": `"${seededWork.version}"`,
        },
      )
    ).status,
  ).toBe(201);
  expect(
    (await raw(technician, `${base}/work-orders/${fixture.work_order}/brief`))
      .status,
  ).toBe(404);
  const directory = (await raw(admin, `${base}/memberships`)).data.items as {
    id: string;
    roles: string[];
    version: number;
  }[];
  const finalAdmin = directory.find((member) =>
    member.roles.includes("ADMIN"),
  )!;
  expect(
    (
      await raw(
        admin,
        `${base}/memberships/${finalAdmin.id}/roles`,
        "PUT",
        {
          roles: ["CITIZEN"],
          reason:
            "SYNTHETIC last-administrator protection must reject this change.",
        },
        {
          "Idempotency-Key": crypto.randomUUID(),
          "If-Match": `"${finalAdmin.version}"`,
        },
      )
    ).status,
  ).toBe(409);
  const affected = directory.find(
    (member) => member.id === fixture.tech_membership,
  )!;
  expect(
    (
      await raw(
        admin,
        `${base}/memberships/${affected.id}/status`,
        "POST",
        {
          status: "SUSPENDED",
          reason: "SYNTHETIC immediate session revocation boundary test.",
        },
        {
          "Idempotency-Key": crypto.randomUUID(),
          "If-Match": `"${affected.version}"`,
        },
      )
    ).status,
  ).toBe(200);
  expect((await raw(technician, "/me")).status).toBe(401);
  await technician.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(
    technician.getByRole("heading", { name: "Assigned-task brief" }),
  ).toHaveCount(0);
  await admin.getByLabel("Utility workspace").selectOption(fixture.other_org);
  await expect(admin.getByLabel("Utility workspace")).toHaveValue(
    fixture.other_org,
  );
  await expect(
    admin.getByRole("heading", { name: "Members and invitations" }),
  ).toBeVisible();
  expect(admin.url()).toContain(fixture.other_org);
  await capture(admin, "administration-other-tenant");
  await citizen.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(
    citizen.getByRole("heading", { name: "Sign in to your workspace" }),
  ).toBeVisible();
  await citizen.goBack();
  await expect(citizen.getByText(tracking, { exact: true })).toHaveCount(0);
  expect(consoleErrors).toEqual([]);
  writeFileSync(
    join(output!, "browser-safe-summary.json"),
    JSON.stringify(
      {
        result: "PASS",
        provenance: "SYNTHETIC_BROWSER_INTEGRATION_ONLY",
        physical_trials: 0,
        field_trials: 0,
        verification: "NOT_VERIFIABLE",
        viewport_widths: [360, 390, 640, 768, 1024, 1280, 1440, 1920],
        unexpected_console_or_page_errors: consoleErrors.length,
        expected_http_denial_console_messages: expectedHttpDenials.length,
      },
      null,
      2,
    ),
  );
  for (const context of contexts) await context.close();
});
