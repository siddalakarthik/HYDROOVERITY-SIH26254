import { test, expect, type Page, type Browser } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const fixture = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as {
  password: string;
  org: string;
  zone: string;
  work_order: string;
  incident: string;
};
const output = process.env.HYDRO_M04_SCREENSHOTS!;
const baseURL =
  process.env.HYDRO_BROWSER_PORT === "9443"
    ? "https://localhost:9443"
    : "https://localhost:8443";
test.describe.configure({ mode: "serial" });

async function actor(browser: Browser, email: string, mobile = false) {
  const context = await browser.newContext({
    baseURL,
    viewport: mobile
      ? { width: 390, height: 844 }
      : { width: 1440, height: 1000 },
  });
  const page = await context.newPage();
  await page.goto("/login");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(fixture.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Choose your workspace" }),
  ).toBeVisible();
  return { page, context };
}

async function capture(page: Page, name: string) {
  await expect(page.locator(".loading:visible")).toHaveCount(0);
  mkdirSync(output, { recursive: true });
  await page.screenshot({ path: join(output, name + ".png"), fullPage: true });
}

async function accessible(page: Page) {
  const result = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(
    result.violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      targets: v.nodes.map((n) => n.target),
    })),
  ).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
}

async function raw(
  page: Page,
  path: string,
  method = "GET",
  body?: unknown,
  version?: number,
) {
  return page.evaluate(
    async ({ path, method, body, version }) => {
      const headers: Record<string, string> = {};
      if (method !== "GET") {
        headers["Content-Type"] = "application/json";
        const token = await (await fetch("/api/v1/auth/csrf")).json();
        headers["X-CSRF-Token"] = token.csrf_token;
        headers["Idempotency-Key"] = crypto.randomUUID();
        if (version) headers["If-Match"] = `"${version}"`;
      }
      const result = await fetch("/api/v1" + path, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        cache: "no-store",
      });
      return { status: result.status, data: await result.json() };
    },
    { path, method, body, version },
  );
}

let caseId = "";
let tracking = "";
test("M07-A real resident intake, supervisor triage, follow-up and authorized investigation findings", async ({
  browser,
}) => {
  const resident = await actor(browser, "service-citizen@example.invalid");
  const supervisor = await actor(browser, "service-supervisor@example.invalid");
  const technician = await actor(browser, "service-tech@example.invalid");
  const errors: string[] = [];
  [resident.page, supervisor.page, technician.page].forEach((page) =>
    page.on("pageerror", (e) => errors.push(e.message)),
  );
  let releaseResources = () => {};
  try {
    const r = resident.page,
      s = supervisor.page,
      t = technician.page;
    const root = `/citizen/${fixture.org}/service-requests`;
    await r.goto(root);
    // Delay real optional-resource requests until the resident has entered data.
    // No response or appointment/service data is fabricated by this regression.
    const resourcePaths = new Set([
      `/api/v1/orgs/${fixture.org}/complaints`,
      `/api/v1/orgs/${fixture.org}/service-requests`,
    ]);
    const resourceUrl = (url: URL) => resourcePaths.has(url.pathname);
    const heldPaths = new Set<string>();
    const resourcesReady = new Promise<void>((resolve) => {
      releaseResources = resolve;
    });
    await r.route(resourceUrl, async (route) => {
      if (
        route.request().method() === "GET" &&
        r.url().endsWith("/service-requests/new")
      ) {
        heldPaths.add(new URL(route.request().url()).pathname);
        await resourcesReady;
      }
      await route.continue();
    });
    await r
      .getByRole("link", { name: "Request utility service", exact: true })
      .click();
    await expect(r).toHaveURL(new RegExp(`/service-requests/new$`));
    await expect(
      r.getByRole("heading", { name: "Request utility service", exact: true }),
    ).toBeVisible();
    await expect.poll(() => heldPaths.size).toBe(2);
    const selectedCategory = await r
      .getByLabel("Service category", { exact: true })
      .elementHandle();
    await r
      .getByLabel("Service category", { exact: true })
      .selectOption("VISIBLE_LEAK");
    await r
      .getByLabel("What needs attention?")
      .fill(
        "SYNTHETIC M07-A browser request: visible water near a public landmark.",
      );
    await r
      .getByLabel("Rough area or public landmark")
      .fill("SYNTHETIC public landmark only");
    await r.getByLabel("I understand this submits").check();
    await expect(r.getByLabel("Service category", { exact: true })).toHaveValue(
      "VISIBLE_LEAK",
    );
    releaseResources();
    await r
      .getByText("Connect an existing report or closed request (optional)", {
        exact: true,
      })
      .click();
    await expect(r.getByLabel("Existing report (optional)")).toBeVisible();
    await expect(
      r.getByLabel("Closed request for a recurring concern (optional)"),
    ).toBeVisible();
    expect(await selectedCategory!.evaluate((el) => el.isConnected)).toBe(true);
    await expect(r.getByLabel("Service category", { exact: true })).toHaveValue(
      "VISIBLE_LEAK",
    );
    await expect(r.getByLabel("What needs attention?")).toHaveValue(
      "SYNTHETIC M07-A browser request: visible water near a public landmark.",
    );
    await expect(r.getByLabel("Rough area or public landmark")).toHaveValue(
      "SYNTHETIC public landmark only",
    );
    await expect(r.getByLabel("I understand this submits")).toBeChecked();
    await r.unroute(resourceUrl);
    await accessible(r);
    await expect(r.getByLabel("Service category", { exact: true })).toHaveValue(
      "VISIBLE_LEAK",
    );
    await capture(r, "M07-A-01-resident-intake-desktop");
    await r.getByRole("button", { name: "Submit service request" }).click();
    await expect(r).toHaveURL(new RegExp(`/service-requests/[0-9a-f-]{36}$`));
    caseId = r.url().split("/").pop()!;
    await expect(r.locator(".tracking-reference")).toBeVisible();
    tracking = (await r.locator(".tracking-reference").textContent())!;
    await expect(
      r.getByText("Submitted", { exact: true }).first(),
    ).toBeVisible();
    const staffPath = `/app/${fixture.org}/service-requests/${caseId}`;
    await s.goto(staffPath);
    for (const target of ["UNDER_REVIEW", "AWAITING_RESIDENT"]) {
      await s.getByLabel("Review decision").selectOption(target);
      await s
        .getByLabel("Message visible to the resident", { exact: true })
        .fill("SYNTHETIC utility request for more information.");
      await s
        .getByLabel("Private triage reason")
        .fill("SYNTHETIC PRIVATE TRIAGE MARKER - internal only.");
      await s.getByRole("button", { name: "Record triage decision" }).click();
      await expect(
        s.locator(".badge").filter({
          hasText:
            target === "UNDER_REVIEW" ? "Under review" : "Awaiting resident",
        }),
      ).toBeVisible();
    }
    await capture(s, "M07-A-02-supervisor-triage-desktop");
    await accessible(s);
    await r.reload();
    await r
      .getByLabel("Additional information for this request")
      .fill("SYNTHETIC follow-up answering the utility's question.");
    await r.getByRole("button", { name: "Send service follow-up" }).click();
    await expect(
      r.locator(".badge").filter({ hasText: "Under review" }),
    ).toBeVisible();
    await expect(
      r.getByText("SYNTHETIC PRIVATE TRIAGE MARKER", { exact: false }),
    ).toHaveCount(0);
    await capture(r, "M07-A-03-safe-resident-timeline");
    await s.reload();
    await s.getByLabel("Review decision").selectOption("ACCEPTED");
    await s
      .getByLabel("Message visible to the resident", { exact: true })
      .fill(
        "SYNTHETIC service accepted for investigation; no visit is booked.",
      );
    await s
      .getByLabel("Private triage reason")
      .fill("SYNTHETIC supervisor acceptance after independent review.");
    await s.getByRole("button", { name: "Record triage decision" }).click();
    await expect(
      s.locator(".badge").filter({ hasText: "Accepted" }),
    ).toBeVisible();
    // The work is created through the actual UI from an already triaged incident.
    const base = `/orgs/${fixture.org}`;
    const concern = await raw(s, base + "/incidents", "POST", {
      zone_id: fixture.zone,
      title: "SYNTHETIC independent service investigation",
      severity: "MEDIUM",
      assessment_ids: [],
      workspace_mode: "OPERATIONAL",
      simulation_run_id: null,
    });
    expect(concern.status).toBe(201);
    let reviewed = concern.data;
    for (const target of ["UNDER_REVIEW", "INVESTIGATION_REQUIRED"]) {
      const decision = await raw(
        s,
        base + `/incidents/${reviewed.id}/transitions`,
        "POST",
        {
          target,
          reason:
            "SYNTHETIC explicit utility triage, independent of resident submission",
        },
        reviewed.version,
      );
      expect(decision.status).toBe(200);
      reviewed = decision.data;
    }
    await s.goto(`/app/${fixture.org}/work-orders`);
    await s.getByText("Create a work order", { exact: true }).click();
    await s.getByLabel("Reviewed incident").selectOption(reviewed.id);
    await s.getByLabel("Priority", { exact: true }).selectOption("MEDIUM");
    await s.getByLabel("Work purpose").selectOption("INVESTIGATION");
    await s
      .getByLabel("Visit instructions")
      .fill(
        "SYNTHETIC investigation only; no repair or visit confirmation is claimed.",
      );
    await s
      .getByRole("button", { name: "Create work order", exact: true })
      .click();
    await expect(s).toHaveURL(new RegExp(`/work-orders/[0-9a-f-]{36}$`));
    const workId = s.url().split("/").pop()!;
    // Assign via existing backend contract; scheduling remains disabled.
    const w = await raw(s, base + `/work-orders/${workId}`);
    const fixtureFull = JSON.parse(
      readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
    );
    expect(
      (
        await raw(
          s,
          base + `/work-orders/${workId}/assignment`,
          "POST",
          {
            assignee_membership_id: fixtureFull.service_tech_membership,
            due_at: null,
            reason: "SYNTHETIC assignment without appointment",
          },
          w.data.version,
        )
      ).status,
    ).toBe(201);
    await s.goto(staffPath);
    await s.getByText("Link authorized work", { exact: true }).click();
    await s.getByLabel("Authorized work order").selectOption(workId);
    await s.getByLabel("Existing work purpose").selectOption("INVESTIGATION");
    await s
      .getByLabel("Private linkage reason")
      .fill("SYNTHETIC authorized operational work linkage.");
    await s
      .getByRole("button", { name: "Link work order", exact: true })
      .click();
    await expect(
      s.getByRole("heading", { name: "Authorized work links" }),
    ).toBeVisible();
    await expect(
      s
        .locator(".record-list")
        .getByRole("link", { name: workId, exact: true }),
    ).toBeVisible();
    await t.goto(`/app/${fixture.org}/work-orders/${workId}`);
    for (const target of ["ACCEPTED", "IN_PROGRESS"]) {
      await t.getByLabel("Next work state").selectOption(target);
      await t
        .getByLabel("Reason for work transition")
        .fill("SYNTHETIC technician progression.");
      await t.getByRole("button", { name: "Record work transition" }).click();
      await expect(
        t.locator(".badge").filter({
          hasText: target === "ACCEPTED" ? "Accepted" : "In progress",
        }),
      ).toBeVisible();
    }
    await t
      .getByLabel("Investigation findings", { exact: true })
      .fill(
        "SYNTHETIC inspection found no sufficient basis to report a completed repair.",
      );
    await t
      .getByLabel("Why no repair was performed")
      .fill("SYNTHETIC investigation only; no physical repair performed.");
    await t
      .getByRole("button", { name: "Record investigation findings" })
      .click();
    await expect(
      t
        .getByText("SYNTHETIC inspection found no sufficient basis", {
          exact: false,
        })
        .first(),
    ).toBeVisible();
    await capture(t, "M07-A-04-technician-findings-desktop");
    await accessible(t);
    const counts = await raw(s, base + `/work-orders/${workId}/repairs`);
    expect(counts.status).toBe(200);
    expect(counts.data.items).toEqual([]);
    await r.goto(`${root}/${caseId}`);
    await expect(r.getByText(workId, { exact: false })).toHaveCount(0);
    await expect(
      r.getByText("SYNTHETIC PRIVATE TRIAGE MARKER", { exact: false }),
    ).toHaveCount(0);
    expect(errors).toEqual([]);
  } finally {
    releaseResources();
    await Promise.all([
      resident.context.close(),
      supervisor.context.close(),
      technician.context.close(),
    ]);
  }
});

test("M07-A mobile tracking, ownership denial, stale versions and offline error recovery", async ({
  browser,
}) => {
  expect(caseId).not.toBe("");
  const resident = await actor(
    browser,
    "service-citizen@example.invalid",
    true,
  );
  const stranger = await actor(
    browser,
    "service-stranger@example.invalid",
    true,
  );
  try {
    const r = resident.page;
    const root = `/citizen/${fixture.org}/service-requests`;
    await r.goto(root);
    await r.getByLabel("Tracking reference", { exact: true }).fill(tracking);
    await r.getByRole("button", { name: "Find request", exact: true }).click();
    await expect(r).toHaveURL(new RegExp(caseId));
    await accessible(r);
    await capture(r, "M07-A-05-resident-mobile");
    const base = `/orgs/${fixture.org}/service-requests/${caseId}`;
    expect((await raw(stranger.page, base)).status).toBe(404);
    expect((await raw(r, base + "/timeline?audience=INTERNAL")).status).toBe(
      403,
    );
    expect((await raw(r, base + "/visit-access")).status).toBe(503);
    expect(
      (
        await raw(
          r,
          base + "/follow-ups",
          "POST",
          {
            operation_id: crypto.randomUUID(),
            message: "SYNTHETIC stale attempt",
          },
          1,
        )
      ).status,
    ).toBe(412);
    await resident.context.setOffline(true);
    await r
      .getByRole("button", { name: "Refresh request and history" })
      .click();
    await expect(
      r.getByText("Connection unavailable.", { exact: false }).first(),
    ).toBeVisible();
    await capture(r, "M07-A-06-mobile-offline-error");
    await resident.context.setOffline(false);
    await r.reload();
    await expect(r.locator(".tracking-reference")).toHaveText(tracking);
    await r
      .getByLabel("Reason for this request")
      .fill("SYNTHETIC resident requests cancellation for utility review.");
    await r
      .getByRole("button", { name: "Request cancellation", exact: true })
      .click();
    await expect(
      r.getByText("Cancellation is pending utility review.", { exact: false }),
    ).toBeVisible();
    await accessible(r);
    await capture(r, "M07-A-07-mobile-cancellation-pending");
  } finally {
    await resident.context.close();
    await stranger.context.close();
  }
});
