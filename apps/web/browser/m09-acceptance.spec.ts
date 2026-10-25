import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const fixture = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as { org: string; password: string };
const output = process.env.HYDRO_M04_SCREENSHOTS!;

test("M09 public reflow, reduced motion, keyboard semantics and real navigation measurements", async ({
  page,
  browser,
}) => {
  mkdirSync(output, { recursive: true });
  await page.emulateMedia({ reducedMotion: "reduce" });
  const observations: object[] = [];
  for (const width of [1440, 768, 640, 320]) {
    await page.setViewportSize({ width, height: 960 });
    for (const route of ["/", "/login", "/register", "/how-it-works"]) {
      const response = await page.goto(route);
      expect(response?.status()).toBe(200);
      await expect(page.locator("main h1")).toBeVisible();
      await expect(page.locator(".loading:visible")).toHaveCount(0);
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth),
      ).toBeLessThanOrEqual(width);
      const result = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze();
      expect(
        result.violations.map((v) => ({
          id: v.id,
          targets: v.nodes.map((n) => n.target),
        })),
      ).toEqual([]);
      observations.push(
        await page.evaluate(() => {
          const n = performance.getEntriesByType(
            "navigation",
          )[0] as PerformanceNavigationTiming;
          return {
            path: location.pathname,
            width: innerWidth,
            ttfb_ms: n.responseStart - n.requestStart,
            dom_content_loaded_ms: n.domContentLoadedEventEnd,
            encoded_document_bytes: n.encodedBodySize,
            reduced_motion: matchMedia("(prefers-reduced-motion: reduce)")
              .matches,
          };
        }),
      );
    }
    await page.screenshot({
      path: join(output, `M09-public-${width}.png`),
      fullPage: true,
    });
  }
  await page.goto("/login");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  expect(
    await page.evaluate(
      () => getComputedStyle(document.activeElement!).outlineStyle,
    ),
  ).not.toBe("none");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#main$/);
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Email address")).toBeFocused();
  const missing = await page.goto("/m09-nonexistent-route");
  expect(missing?.status()).toBe(404);
  await expect(page.locator("main")).toBeVisible();
  writeFileSync(
    join(output, "M09-browser-measurements.json"),
    JSON.stringify(
      {
        environment: "PRIVATE_LOOPBACK_PRODUCTION_BUILD",
        browser_version: browser.version(),
        node_version: process.version,
        samples: observations,
        limitations:
          "16 sequential navigations, no production SLA; 640/320 CSS-pixel reflow approximates 200/400% on 1280px. Native browser zoom and full assistive-technology certification were not performed.",
      },
      null,
      2,
    ),
  );
});

test("M09 resident hostile text remains inert across submission, reload and mobile timeline", async ({
  page,
}) => {
  await page.goto("/login");
  await page
    .getByLabel("Email address")
    .fill("service-citizen@example.invalid");
  await page.getByLabel("Password", { exact: true }).fill(fixture.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Choose your workspace" }),
  ).toBeVisible();
  let dialogs = 0;
  page.on("dialog", async (dialog) => {
    dialogs++;
    await dialog.dismiss();
  });
  const marker =
    "SYNTHETIC M09 <img src=x onerror=alert('M09')> <script>alert('M09')</script>";
  await page.goto(`/citizen/${fixture.org}/service-requests/new`);
  await page
    .getByLabel("Service category", { exact: true })
    .selectOption("VISIBLE_LEAK");
  await page.getByLabel("What needs attention?", { exact: true }).fill(marker);
  await page
    .getByLabel("Rough area or public landmark", { exact: true })
    .fill("SYNTHETIC M09 public landmark");
  await page
    .getByLabel(
      "I understand this submits my description and rough area to the utility for review.",
    )
    .check();
  await page.getByRole("button", { name: "Submit service request" }).click();
  await expect(page).toHaveURL(/\/service-requests\/[0-9a-f-]{36}$/);
  await expect(page.getByText(marker, { exact: true })).toBeVisible();
  await page.reload();
  await page.setViewportSize({ width: 320, height: 854 });
  await expect(page.getByText(marker, { exact: true })).toBeVisible();
  expect(await page.locator("main img[src='x'], main script").count()).toBe(0);
  expect(dialogs).toBe(0);
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(320);
  const result = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(result.violations.map((v) => v.id)).toEqual([]);
  await page.screenshot({
    path: join(output, "M09-resident-inert-text-mobile.png"),
    fullPage: true,
  });
});
