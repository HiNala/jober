import { test, expect, devices } from "@playwright/test";

import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";

/**
 * Mobile More sheet — destinations beyond the four primary tabs.
 * Uses iPhone viewport; works with or without full-stack if shell chrome renders.
 */
test.use({ ...devices["iPhone 13"] });

test("mobile More sheet lists Library, Vault, Analytics, Settings", async ({ page }) => {
  await page.goto("/dashboard");
  await dismissAnalyticsConsent(page);

  // Shell may require auth; if login redirect, skip remaining asserts gracefully.
  if (page.url().includes("/login")) {
    test.skip(true, "Auth required — run with DEV_AUTH_BYPASS or session for full stack");
  }

  await waitForAppShell(page).catch(() => undefined);

  const more = page.getByRole("button", { name: /more destinations/i });
  await expect(more).toBeVisible({ timeout: 15_000 });
  await more.click();

  await expect(page.getByRole("navigation", { name: /more destinations/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /library/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /vault/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /analytics/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /^settings/i })).toBeVisible();
});
