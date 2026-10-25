import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const f = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as {
  org: string;
  other_org: string;
  password: string;
  comms_case: string;
  comms_work: string;
};

test("M07-C real inbox, versioned preferences, service feedback, supervisor review and technician links", async ({
  page,
  context,
}) => {
  test.setTimeout(180000);
  page.setDefaultTimeout(15000);
  const output = process.env.HYDRO_M04_SCREENSHOTS!;
  mkdirSync(output, { recursive: true });
  async function login(email: string) {
    await context.clearCookies();
    await page.goto("/login");
    await page.getByLabel("Email address").fill(email);
    await page.getByLabel("Password", { exact: true }).fill(f.password);
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "Choose your workspace" }),
    ).toBeVisible();
  }
  async function accessible() {
    const result = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
      .analyze();
    expect(
      result.violations.map((v) => ({
        id: v.id,
        targets: v.nodes.map((n) => n.target),
      })),
    ).toEqual([]);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(await page.evaluate(() => window.innerWidth));
  }
  const inbox = `/app/${f.org}/notifications`;
  await login("comms-citizen@example.invalid");
  await page.goto(inbox);
  await expect(
    page.getByRole("heading", { name: "Notifications", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Mark as read", exact: true }),
  ).toBeVisible();
  await expect(page.locator("main")).not.toContainText("PRIVATE_SYNTHETIC");
  await accessible();
  await page.screenshot({
    path: join(output, "M07C-resident-inbox-desktop.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Mark as read", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Mark as read", exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("link", { name: "Open current authorized record", exact: true })
    .click();
  await expect(page).toHaveURL(new RegExp(f.comms_case));
  await page.goto(inbox);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByLabel("Enable optional in-app notifications").uncheck();
  const saveDisabled = page.waitForResponse(
    (r) =>
      r.url().endsWith("/notification-preferences") &&
      r.request().method() === "PUT",
  );
  await page
    .getByRole("button", { name: "Save notification preferences" })
    .click();
  expect((await saveDisabled).status()).toBe(200);
  await expect(
    page.getByLabel("Enable optional in-app notifications"),
  ).not.toBeChecked();
  await page.reload();
  await expect(
    page.getByLabel("Enable optional in-app notifications"),
  ).not.toBeChecked();
  await accessible();
  await page.screenshot({
    path: join(output, "M07C-resident-preferences-mobile.png"),
    fullPage: true,
  });
  await page.getByLabel("Enable optional in-app notifications").check();
  const saveEnabled = page.waitForResponse(
    (r) =>
      r.url().endsWith("/notification-preferences") &&
      r.request().method() === "PUT",
  );
  await page
    .getByRole("button", { name: "Save notification preferences" })
    .click();
  expect((await saveEnabled).status()).toBe(200);
  await page.goto(`/citizen/${f.org}/service-requests/${f.comms_case}`);
  await page
    .getByLabel("Feedback summary", { exact: true })
    .fill("SYNTHETIC service experience feedback");
  await page
    .getByLabel("Your experience", { exact: true })
    .fill(
      "SYNTHETIC resident experience only. No physical sensor or repair validation is claimed.",
    );
  await page
    .getByLabel("Service experience rating (optional)")
    .selectOption("4");
  await page
    .getByRole("button", { name: "Submit feedback", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "SYNTHETIC service experience feedback",
      exact: true,
    }),
  ).toBeVisible();
  await accessible();
  await page.screenshot({
    path: join(output, "M07C-resident-feedback-mobile.png"),
    fullPage: true,
  });
  await page.goto(`/app/${f.org}/feedback`);
  await expect(
    page.getByRole("heading", {
      name: "SYNTHETIC service experience feedback",
      exact: true,
    }),
  ).toBeVisible();
  await login("comms-supervisor@example.invalid");
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(`/app/${f.org}/service-requests/${f.comms_case}`);
  await expect(
    page.getByRole("heading", { name: "In-app delivery audit" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Service delivery audit" }),
  ).toContainText("DELIVERED");
  await accessible();
  await page.screenshot({
    path: join(output, "M07C-supervisor-delivery-audit-desktop.png"),
    fullPage: true,
  });
  await page.getByText("Review feedback", { exact: true }).click();
  await page
    .getByLabel("Review status", { exact: true })
    .selectOption("RESOLVED");
  await page
    .getByLabel("Private review severity")
    .fill("PRIVATE_REVIEW_SYNTHETIC");
  await page
    .getByLabel("Public response to the resident")
    .fill(
      "SYNTHETIC reviewed public response, separate from scientific verification.",
    );
  await page.getByRole("button", { name: "Record feedback review" }).click();
  await expect(
    page.getByText(
      "SYNTHETIC reviewed public response, separate from scientific verification.",
      { exact: true },
    ),
  ).toBeVisible();
  await login("comms-technician@example.invalid");
  await page.goto(inbox);
  await expect(
    page.getByText(
      "Your assigned work has an update. Check your current task and agenda before taking action.",
    ),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Open current authorized record", exact: true })
    .click();
  await expect(page).toHaveURL(new RegExp(`/app/${f.org}/work-orders`));
  await login("comms-citizen@example.invalid");
  await page.goto(`/app/${f.org}/feedback`);
  await expect(
    page.getByText(
      "SYNTHETIC reviewed public response, separate from scientific verification.",
      { exact: true },
    ),
  ).toBeVisible();
  await expect(page.locator("main")).not.toContainText(
    "PRIVATE_REVIEW_SYNTHETIC",
  );
  const denied = await page.evaluate(
    async (other) =>
      (await fetch(`/api/v1/orgs/${other}/notifications`)).status,
    f.other_org,
  );
  expect(denied).toBe(404);
  // Deterministic network outage; persistence and normal workflow above use the real API.
  const outage = /\/api\/v1\/orgs\/[^/]+\/notifications\?/;
  await page.goto(inbox);
  await expect(
    page.getByRole("heading", { name: "Notifications", exact: true }),
  ).toBeVisible();
  await page.route(outage, (route) => route.abort("failed"));
  await page
    .getByRole("button", { name: "Refresh notifications", exact: true })
    .click();
  const connectionError = page
    .getByRole("alert")
    .filter({ hasText: "Connection unavailable" });
  await expect(connectionError).toBeVisible();
  await page.unroute(outage);
  await connectionError
    .getByRole("button", { name: "Refresh current data", exact: true })
    .click();
  await expect(connectionError).toHaveCount(0);
  await context.clearCookies();
  await page.reload();
  await expect(
    page.getByRole("link", { name: "Sign in", exact: true }).first(),
  ).toBeVisible();
});
