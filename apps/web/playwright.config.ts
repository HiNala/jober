import { defineConfig, devices } from "@playwright/test";

const PORT = process.env.PORT ?? "3000";
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? "github" : "list",
  use: {
    ...devices["Desktop Chrome"],
    baseURL,
    trace: "retain-on-failure",
  },
  webServer: process.env.PLAYWRIGHT_SKIP_WEB_SERVER
    ? undefined
    : {
        command: "pnpm start",
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
        env: {
          ...process.env,
          NEXT_PUBLIC_DEV_AUTH_BYPASS: "true",
          NEXT_PUBLIC_JOBER_TENANT_ID:
            process.env.NEXT_PUBLIC_JOBER_TENANT_ID ?? "00000000-0000-4000-8000-000000000001",
          NEXT_PUBLIC_JOBER_USER_ID:
            process.env.NEXT_PUBLIC_JOBER_USER_ID ?? "00000000-0000-4000-8000-000000000002",
        },
      },
});
