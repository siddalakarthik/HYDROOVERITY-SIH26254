import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const fixture = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as { org: string; password: string };
test("M06 real import, qualified evidence, replay, export, mobile and access denial", async ({
  page,
}) => {
  await page.goto("/login");
  await page
    .getByLabel("Email address")
    .fill("science-engineer@example.invalid");
  await page.getByLabel("Password", { exact: true }).fill(fixture.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Choose your workspace" }),
  ).toBeVisible();
  const root = `/app/${fixture.org}/simulations`;
  const output = process.env.HYDRO_M04_SCREENSHOTS!;
  mkdirSync(output, { recursive: true });
  async function scenario(code: string) {
    await page.goto(root);
    await expect(
      page.getByRole("heading", { name: "Scientific scenario lab" }),
    ).toBeVisible();
    await page
      .getByLabel("Scientific scenario", { exact: true })
      .selectOption(code);
    await page
      .getByRole("button", { name: "Import scenario", exact: true })
      .click();
    await expect(page).toHaveURL(new RegExp(`/simulations/[a-f0-9-]+$`));
    await expect(
      page.getByRole("heading", { name: "Evidence waterfall" }),
    ).toBeVisible();
    await expect(page.locator(".science-provenance")).toContainText(
      "SIMULATION MODE",
    );
  }
  async function accessible() {
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
          .analyze()
      ).violations.map((v) => ({
        id: v.id,
        targets: v.nodes.map((n) => n.target),
      })),
    ).toEqual([]);
    const overflow = await page.evaluate(() => ({
      width: window.innerWidth,
      actual: document.documentElement.scrollWidth,
      elements: [...document.querySelectorAll("main *")]
        .filter((e) => e.getBoundingClientRect().right > window.innerWidth + 1)
        .slice(0, 12)
        .map((e) => ({
          tag: e.tagName,
          class: e.className,
          width: e.getBoundingClientRect().width,
        })),
    }));
    expect(overflow.actual, JSON.stringify(overflow)).toBeLessThanOrEqual(
      overflow.width,
    );
  }
  await scenario("H11");
  await expect(
    page.getByRole("heading", {
      name: "Independent fault / urgent observations",
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Play replay", exact: true }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "samples" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Pause replay", exact: true }).click();
  await page
    .getByRole("button", { name: "Restart replay", exact: true })
    .click();
  const run = page.url().split("/").at(-1)!;
  const read = (path: string) =>
    page.evaluate(async (url) => {
      const response = await fetch(url, { credentials: "same-origin" });
      return { status: response.status, text: await response.text() };
    }, path);
  const stream = await read(
    `/api/v1/orgs/${fixture.org}/scientific-replays/${run}/events?offset=0&limit=2`,
  );
  expect(stream.status).toBe(200);
  expect(stream.text).toContain("event: observation");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export observations" }).click();
  const download = await downloadPromise;
  const contents = JSON.parse(readFileSync((await download.path())!, "utf8"));
  expect(contents.source_category).toBe("SIMULATION");
  expect(JSON.stringify(contents)).not.toMatch(
    /"(?:truth|seed|position_m|hidden_label|artifact_path)"/,
  );
  await accessible();
  await page.screenshot({
    path: join(output, "M06-WATCH-desktop.png"),
    fullPage: true,
  });
  await scenario("G06-nominal");
  await expect(page.locator(".science-channels article")).toHaveCount(5);
  await expect(page.locator(".science-channels")).toContainText("UNKNOWN");
  await page.setViewportSize({ width: 390, height: 844 });
  await accessible();
  await page.screenshot({
    path: join(output, "M06-GUARD5-mobile.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await scenario("A01");
  await accessible();
  await page.screenshot({
    path: join(output, "M06-EAR-desktop.png"),
    fullPage: true,
  });
  await scenario("A09");
  await expect(
    page.getByText("No qualified localization interval"),
  ).toBeVisible();
  for (const [code, outcome] of [
    ["comparable_repair", "PASSED"],
    ["incomplete_repair", "FAILED"],
    ["missing_post_evidence", "NOT_VERIFIABLE"],
  ]) {
    await scenario("V-" + code);
    await expect(
      page
        .locator(".panel")
        .filter({
          has: page.getByRole("heading", {
            name: "HYDRO-VERIFY · modeled outcome",
            exact: true,
          }),
        })
        .locator(".science-interval"),
    ).toHaveText(outcome);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await accessible();
  await page.screenshot({
    path: join(output, "M06-VERIFY-mobile.png"),
    fullPage: true,
  });
  const foreign = await read(
    `/api/v1/orgs/00000000-0000-4000-8000-000000000001/scientific-replays/${run}`,
  );
  expect(foreign.status).toBe(404);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
  expect(
    (await read(`/api/v1/orgs/${fixture.org}/scientific-replays/${run}`))
      .status,
  ).toBe(401);
});
