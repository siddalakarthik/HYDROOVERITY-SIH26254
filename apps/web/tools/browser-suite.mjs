// Keep the real login-IP throttle intact across the two private acceptance suites.
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const cli = require.resolve("@playwright/test/cli");
for (const [index, file] of [
  "browser/workflow.spec.ts",
  "browser/service-foundation.spec.ts",
  "browser/science.spec.ts",
].entries()) {
  if (index) {
    console.log(
      "Waiting one login-rate window before the separate M07-A browser suite.",
    );
    await new Promise((resolve) => setTimeout(resolve, 61000));
  }
  const result = spawnSync(process.execPath, [cli, "test", file], {
    stdio: "inherit",
    env: process.env,
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
