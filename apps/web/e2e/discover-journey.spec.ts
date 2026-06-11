import { test, expect } from "@playwright/test";

import { dismissAnalyticsConsent } from "./helpers/consent";
import { waitForAppShell } from "./helpers/app-auth";

test("discover vs search: distinct page purposes", async ({ page }) => {
  await page.goto("/discover");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);
  await expect(page.getByRole("heading", { name: /discover & build lists/i })).toBeVisible();
  await expect(
    page.locator("header").getByRole("link", { name: /search library/i }),
  ).toBeVisible();

  await page.goto("/search");
  await waitForAppShell(page);
  await expect(page.getByRole("heading", { name: /search library/i })).toBeVisible();
  await expect(page.locator("header").getByRole("link", { name: /^discover$/i })).toBeVisible();
});

test("discover: board search tab and list panel visible", async ({ page }) => {
  await page.goto("/discover");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);
  await expect(page.getByRole("tab", { name: /search for jobs/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: /target list/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /preview batch from list/i })).toBeVisible();
});
