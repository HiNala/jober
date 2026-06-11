import { test, expect } from "@playwright/test";

import { dismissAnalyticsConsent } from "./helpers/consent";

/**
 * Hermetic marketing funnel smoke — no live network or external ATS.
 * Full fixture pipeline is covered by `test_golden_path_integration.py` (API).
 */
test("marketing funnel: landing → signup CTA → signup page", async ({ page }) => {
  await page.goto("/");
  await dismissAnalyticsConsent(page);
  await page.getByRole("link", { name: /start free/i }).first().click();
  await expect(page).toHaveURL(/\/signup/);
  await expect(page.getByRole("heading", { name: /create account/i })).toBeVisible();
});

test("marketing funnel: pricing CTA reachable by keyboard", async ({ page }) => {
  await page.goto("/pricing");
  await dismissAnalyticsConsent(page);
  await expect(page.getByRole("heading", { level: 1 })).toContainText(/plans that match/i);
  const signup = page.getByRole("link", { name: /start free/i }).first();
  await signup.focus();
  await expect(signup).toBeFocused();
});
