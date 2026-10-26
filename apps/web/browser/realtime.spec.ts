import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const f = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as { org: string; password: string };

test("R02 real SSE, disconnect replay and background refresh preserve the resident draft", async ({
  page,
  context,
  browser,
}) => {
  await page.goto("/login");
  await page.getByLabel("Email address").fill("comms-citizen@example.invalid");
  await page.getByLabel("Password", { exact: true }).fill(f.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Choose your workspace" }),
  ).toBeVisible();
  await page.goto(`/citizen/${f.org}/service-requests/new`);
  await expect(
    page.getByRole("status").filter({ hasText: "Record updates connected" }),
  ).toBeVisible();
  await page
    .getByLabel("Service category", { exact: true })
    .selectOption("VISIBLE_LEAK");
  const draft = "SYNTHETIC resident draft retained across real record updates";
  await page.getByLabel("What needs attention?").fill(draft);
  await page
    .getByLabel("Rough area or public landmark")
    .fill("SYNTHETIC realtime acceptance landmark");
  await page
    .getByLabel(
      "I understand this submits my description and rough area to the utility for review.",
    )
    .check();
  const actor = await browser.newContext({
    baseURL: new URL(page.url()).origin,
  });
  await actor.addCookies(await context.cookies());
  const source = await actor.newPage();
  try {
    await source.goto("/");
    await context.setOffline(true);
    await expect(
      page
        .getByRole("status")
        .filter({ hasText: "Record updates disconnected" }),
    ).toBeVisible();
    const result = await source.evaluate(async (org) => {
      const csrf = await (await fetch("/api/v1/auth/csrf")).json();
      const response = await fetch(`/api/v1/orgs/${org}/complaints`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrf.csrf_token,
          "Idempotency-Key": crypto.randomUUID(),
        },
        body: JSON.stringify({
          category: "VISIBLE_LEAK",
          description: "SYNTHETIC record created during another tab disconnect",
          coarse_area: "SYNTHETIC replay landmark",
          photo_consent: false,
          attachment_ids: [],
        }),
      });
      return { status: response.status, id: (await response.json()).id };
    }, f.org);
    expect(result.status).toBe(201);
    const snapshot = page.waitForResponse(
      (r) =>
        r.request().method() === "GET" &&
        r.url().includes(`/orgs/${f.org}/complaints`) &&
        r.status() === 200,
    );
    await context.setOffline(false);
    const response = await snapshot;
    expect(
      (await response.json()).items.some(
        (item: { id: string }) => item.id === result.id,
      ),
    ).toBe(true);
    await expect(
      page.getByRole("status").filter({ hasText: "Record updates connected" }),
    ).toBeVisible();
    await expect(
      page.getByLabel("Service category", { exact: true }),
    ).toHaveValue("VISIBLE_LEAK");
    await expect(page.getByLabel("What needs attention?")).toHaveValue(draft);
    await expect(page.getByLabel("Rough area or public landmark")).toHaveValue(
      "SYNTHETIC realtime acceptance landmark",
    );
    await expect(
      page.getByLabel(
        "I understand this submits my description and rough area to the utility for review.",
      ),
    ).toBeChecked();
    await expect(
      page.getByText(
        "Record connectivity does not establish physical sensor freshness.",
        { exact: false },
      ),
    ).toBeVisible();
    await page.setViewportSize({ width: 320, height: 844 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    const output = process.env.HYDRO_M04_SCREENSHOTS!;
    mkdirSync(output, { recursive: true });
    await page.screenshot({
      path: join(output, "PREM10-REALTIME-resident-draft-mobile.png"),
      fullPage: true,
    });
    await page
      .getByRole("button", { name: "Submit service request", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Service request", exact: true }),
    ).toBeVisible();
    await expect(page.locator("main")).toContainText(draft);
  } finally {
    await context.setOffline(false);
    await actor.close();
  }
});
