import { test, expect } from "@playwright/test";

import { APP_A11Y_ROUTES, waitForAppShell } from "./helpers/app-auth";
import { createAxeBuilder } from "./helpers/axe";
import { dismissAnalyticsConsent } from "./helpers/consent";

for (const path of APP_A11Y_ROUTES) {
  test(`axe clean (app): ${path}`, async ({ page }) => {
    await page.goto(path);
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    const results = await createAxeBuilder(page).analyze();

    expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
  });
}

test("axe clean: command palette when open", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/dashboard");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);

  await page.getByRole("button", { name: "Workspace menu" }).focus();
  await page.keyboard.press("Control+K");
  await expect(page.getByRole("dialog", { name: /command palette/i })).toBeVisible({
    timeout: 10_000,
  });

  const results = await createAxeBuilder(page).analyze();
  expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);

  await page.keyboard.press("Escape");
});

test("keyboard: command palette opens and closes with Escape", async ({ page }) => {
  await page.goto("/dashboard");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);

  // Focus app chrome so Chromium does not steal Ctrl+K for the omnibox.
  await page.getByRole("button", { name: "Workspace menu" }).focus();
  await page.keyboard.press("Control+K");

  const dialog = page.getByRole("dialog", { name: /command palette/i });
  await expect(dialog).toBeVisible({ timeout: 10_000 });
  await expect(page.getByPlaceholder("Search commands…")).toBeFocused();

  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
});

test("keyboard: analytics tabs are focusable", async ({ page }) => {
  await page.goto("/analytics");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);

  const mineTab = page.getByRole("tab", { name: /your workspace/i });
  if (await mineTab.isVisible()) {
    await mineTab.focus();
    await expect(mineTab).toBeFocused();
  }
});

test("axe clean (app): library cover letters studio", async ({ page }) => {
  await page.goto("/library?tab=letters&view=studio");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);

  const results = await createAxeBuilder(page).analyze();
  expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
});

test("consent sheet is axe-clean when shown", async ({ page }) => {
  await page.goto("/dashboard");
  await page.evaluate(() => localStorage.removeItem("jober-analytics-consent"));
  await page.reload();
  const dialog = page.getByRole("dialog", { name: /first-party analytics/i });
  await expect(dialog).toBeVisible();

  const results = await createAxeBuilder(page).analyze();
  expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
});
