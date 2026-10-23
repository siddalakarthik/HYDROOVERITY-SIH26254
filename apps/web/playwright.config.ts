import { defineConfig, devices } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
const file = process.env.HYDRO_M04_BROWSER_FIXTURE;
if (!file)
  throw new Error(
    "Set HYDRO_M04_BROWSER_FIXTURE to the private synthetic fixture outside Git.",
  );
const fixture = JSON.parse(readFileSync(resolve(file), "utf8")) as {
  provenance: string;
  certificate_spki: string;
};
const channel = process.env.HYDRO_M04_BROWSER_CHANNEL;
if (channel && channel !== "chrome")
  throw new Error("Only the installed official Chrome fallback is supported.");
if (
  fixture.provenance !== "SYNTHETIC_BROWSER_INTEGRATION_ONLY" ||
  !fixture.certificate_spki
)
  throw new Error("Unrecognized private browser fixture");
export default defineConfig({
  testDir: "./browser",
  timeout: 300000,
  expect: { timeout: 12000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    channel: channel as "chrome" | undefined,
    baseURL:
      process.env.HYDRO_BROWSER_PORT === "9443"
        ? "https://localhost:9443"
        : "https://localhost:8443",
    ignoreHTTPSErrors: false,
    trace: "off",
    video: "off",
    screenshot: "off",
    launchOptions: {
      args: [
        `--ignore-certificate-errors-spki-list=${fixture.certificate_spki}`,
      ],
    },
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 1000 },
      },
    },
  ],
});
