import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
const f = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as {
  org: string;
  password: string;
  dispatch_case: string;
  dispatch_tech: string;
  dispatch_from: string;
  dispatch_to: string;
};
test("M07-B resident request, supervisor booking, technician visit and mobile accessibility", async ({
  page,
  context,
}) => {
  test.setTimeout(120000);
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
  const citizen = `/citizen/${f.org}/service-requests/${f.dispatch_case}`;
  const staff = `/app/${f.org}/service-requests/${f.dispatch_case}`;
  await login("dispatch-citizen@example.invalid");
  await page.goto(citizen);
  await expect(
    page.getByRole("heading", { name: "Appointments and requests" }),
  ).toBeVisible();
  await page
    .getByLabel("Eligible visit window", { exact: true })
    .selectOption({ index: 1 });
  await page
    .getByLabel("Optional visit request message", { exact: true })
    .fill("SYNTHETIC browser visit request.");
  await page
    .getByRole("button", { name: "Request a visit", exact: true })
    .click();
  await expect(page.locator(".appointment-panel")).toContainText("Pending");
  await expect(page.locator(".appointment-panel")).toContainText(
    "No confirmed visit",
  );
  await accessible();
  await page.screenshot({
    path: join(output, "M07B-resident-request-desktop.png"),
    fullPage: true,
  });
  await login("dispatch-supervisor@example.invalid");
  await page.goto(staff);
  await page.getByText("Review appointment request", { exact: true }).click();
  await page
    .getByLabel("Reason visible to the resident", { exact: true })
    .fill("Your requested visit is now confirmed.");
  await page
    .getByLabel("Private dispatch reason", { exact: true })
    .fill("SYNTHETIC capacity and work linkage reviewed.");
  await page
    .getByRole("button", { name: "Record appointment decision", exact: true })
    .click();
  await expect(page.locator(".appointment-panel")).toContainText("Confirmed");
  await page.goto(`/app/${f.org}/work-orders`);
  await page
    .getByLabel("Calendar from (your browser timezone)", { exact: true })
    .fill(f.dispatch_from.slice(0, 16));
  await page
    .getByLabel("Calendar to (your browser timezone)", { exact: true })
    .fill(f.dispatch_to.slice(0, 16));
  await page
    .getByRole("button", { name: "Load schedule range", exact: true })
    .click();
  await page
    .getByLabel("Technician calendar", { exact: true })
    .selectOption(f.dispatch_tech);
  await expect(
    page.getByRole("heading", { name: "Assigned visits", exact: true }),
  ).toBeVisible();
  await accessible();
  await page.screenshot({
    path: join(output, "M07B-supervisor-dispatch-desktop.png"),
    fullPage: true,
  });
  await login("dispatch-tech@example.invalid");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/app/${f.org}/work-orders`);
  await page
    .getByLabel("Calendar from (your browser timezone)", { exact: true })
    .fill(f.dispatch_from.slice(0, 16));
  await page
    .getByLabel("Calendar to (your browser timezone)", { exact: true })
    .fill(f.dispatch_to.slice(0, 16));
  await page
    .getByRole("button", { name: "Load schedule range", exact: true })
    .click();
  await page
    .getByLabel("Permitted visit event", { exact: true })
    .selectOption("CHECK_IN");
  await page
    .getByLabel("Visit event note", { exact: true })
    .fill("SYNTHETIC manual technician check-in.");
  await page
    .getByRole("button", { name: "Record visit event", exact: true })
    .click();
  await expect(
    page
      .getByLabel("Permitted visit event", { exact: true })
      .locator("option[value=VISIT_FINISHED]"),
  ).toHaveCount(1);
  await page
    .getByLabel("Permitted visit event", { exact: true })
    .selectOption("VISIT_FINISHED");
  await page
    .getByLabel("Visit event note", { exact: true })
    .fill(
      "SYNTHETIC inspection visit finished; no repair or scientific result claimed.",
    );
  await page
    .getByRole("button", { name: "Record visit event", exact: true })
    .click();
  await expect(
    page
      .getByRole("heading", { name: "Assigned visits", exact: true })
      .locator(".."),
  ).toBeVisible();
  await expect(page.getByText("Visit finished", { exact: true })).toBeVisible();
  await page
    .getByRole("heading", { name: "My visit agenda", exact: true })
    .click();
  await accessible();
  await page.screenshot({
    path: join(output, "M07B-technician-agenda-mobile.png"),
    fullPage: true,
  });
  await login("dispatch-citizen@example.invalid");
  await page.goto(citizen);
  await expect(page.locator(".appointment-panel")).toContainText(
    "Visit finished",
  );
  await expect(page.locator("main")).not.toContainText(
    "SYNTHETIC capacity and work linkage reviewed.",
  );
  await accessible();
  await page.screenshot({
    path: join(output, "M07B-resident-outcome-mobile.png"),
    fullPage: true,
  });
});
