import { test, expect } from "@playwright/test";

import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { requireFullStack } from "./helpers/fullstack";

/**
 * Admin surface smoke under dev-auth bypass (role may be "user" in bypass —
 * then we still assert non-admin guard). When seeded admin cookies exist,
 * overview should load.
 */
test.describe("admin surface", () => {
  test.beforeEach(() => {
    requireFullStack();
  });

  test("admin route either shows ops shell or access denied", async ({ page }) => {
    await page.goto("/admin");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    const denied = page.getByText(/admin access required/i);
    const overview = page.getByRole("heading", { name: /overview|admin|ops/i }).first();

    await expect(denied.or(overview)).toBeVisible({ timeout: 20_000 });
  });

  test("settings page loads plan and vault sections", async ({ page }) => {
    await page.goto("/settings");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    await expect(page.getByRole("heading", { name: /settings/i })).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.getByText(/plan & billing|profile & vault|appearance/i).first()).toBeVisible({
      timeout: 15_000,
    });
  });
});
