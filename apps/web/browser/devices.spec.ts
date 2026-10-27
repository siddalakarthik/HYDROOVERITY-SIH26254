import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const fixture = JSON.parse(
  readFileSync(process.env.HYDRO_M04_BROWSER_FIXTURE!, "utf8"),
) as { org: string; password: string };

test("proposed device identity persists while actual hardware credential issuance stays gated", async ({
  page,
}) => {
  await page.goto("/login");
  await page.getByLabel("Email address").fill("admin-a@example.invalid");
  await page.getByLabel("Password", { exact: true }).fill(fixture.password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Choose your workspace" }),
  ).toBeVisible();
  await page.goto(`/app/${fixture.org}/devices`);
  await page
    .getByLabel("Proposed serial or reference")
    .fill("SYNTHETIC proposed WATCH identity — no hardware");
  await page.getByLabel("Proposed device type").selectOption("WATCH");
  await page
    .getByLabel("Declared acquisition context")
    .selectOption("LABORATORY");
  const receipt = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      new URL(response.url()).pathname ===
        `/api/v1/orgs/${fixture.org}/devices`,
  );
  await page
    .getByRole("button", { name: "Register proposed identity", exact: true })
    .click();
  const response = await receipt;
  expect(response.status()).toBe(201);
  const device = await response.json();
  expect(device.health).toBe("UNKNOWN");
  expect(Object.keys(device).sort()).toEqual([
    "device_kind",
    "environment",
    "health",
    "id",
    "serial_ref",
    "version",
  ]);
  await page
    .getByRole("link", {
      name: "SYNTHETIC proposed WATCH identity — no hardware",
      exact: true,
    })
    .click();
  await expect(
    page.getByRole("heading", { name: "Device identity", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "Issue hardware credential",
      exact: true,
    }),
  ).toBeDisabled();
  const denied = await page.evaluate(
    async ({ org, id }) => {
      const csrf = await (await fetch("/api/v1/auth/csrf")).json();
      const response = await fetch(
        `/api/v1/orgs/${org}/devices/${id}/credentials`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrf.csrf_token,
            "Idempotency-Key": crypto.randomUUID(),
          },
          body: JSON.stringify({
            environment: "LABORATORY",
            expires_at: new Date(Date.now() + 3600000).toISOString(),
          }),
        },
      );
      const result = await response.json();
      return {
        status: response.status,
        code: result.error?.code,
        hasSecret: Object.hasOwn(result, "one_time_secret"),
      };
    },
    { org: fixture.org, id: device.id },
  );
  expect(denied).toEqual({
    status: 503,
    code: "PHYSICAL_PROVISIONING_NOT_APPROVED",
    hasSecret: false,
  });
  await page.setViewportSize({ width: 320, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  const directory = process.env.HYDRO_M04_SCREENSHOTS!;
  mkdirSync(directory, { recursive: true });
  await page.screenshot({
    path: join(directory, "PREM10-DEVICES-proposed-metadata-mobile.png"),
    fullPage: true,
  });
});
