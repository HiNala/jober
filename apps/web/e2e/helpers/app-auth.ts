import type { Page } from "@playwright/test";

/** Dev bypass tenant/user — matches `jober_api.auth.constants` seed IDs. */
export const E2E_DEV_TENANT_ID = "00000000-0000-4000-8000-000000000001";
export const E2E_DEV_USER_ID = "00000000-0000-4000-8000-000000000002";

/** Fixture run id for ops-desk axe (page may show error without API; still renders chrome). */
export const E2E_FIXTURE_RUN_ID = "00000000-0000-4000-8000-000000000099";

export const APP_A11Y_ROUTES = [
  "/dashboard",
  "/queue",
  "/discover",
  "/library",
  "/search",
  "/settings",
  "/analytics",
  `/runs/${E2E_FIXTURE_RUN_ID}`,
] as const;

/** Wait for hydrated workspace chrome (palette + shortcuts mount with the shell). */
export async function waitForAppShell(page: Page): Promise<void> {
  await page
    .getByRole("button", { name: "Workspace menu" })
    .waitFor({ state: "visible", timeout: 30_000 });
}
