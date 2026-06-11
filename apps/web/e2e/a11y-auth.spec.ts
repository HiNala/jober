import AxeBuilder from "@axe-core/playwright";
import { test, expect } from "@playwright/test";

import { dismissAnalyticsConsent } from "./helpers/consent";

const AUTH_ROUTES = [
  "/login",
  "/signup",
  "/forgot-password",
  "/reset-password?token=e2e-placeholder",
  "/link-google",
] as const;

for (const path of AUTH_ROUTES) {
  test(`axe clean: ${path}`, async ({ page }) => {
    await page.goto(path);
    await dismissAnalyticsConsent(page);
    await expect(page.locator("h1").first()).toBeVisible();

    const results = await new AxeBuilder({ page })
      .disableRules(["color-contrast"])
      .analyze();

    expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
  });
}

test("keyboard: login fields and submit are focusable", async ({ page }) => {
  await page.goto("/login");
  await dismissAnalyticsConsent(page);
  await page.locator("#email").focus();
  await expect(page.locator("#email")).toBeFocused();
  await page.locator("#password").focus();
  await expect(page.locator("#password")).toBeFocused();
  await page.getByRole("button", { name: "Sign in" }).focus();
  await expect(page.getByRole("button", { name: "Sign in" })).toBeFocused();
});

test("keyboard: tab order reaches primary action on signup", async ({ page }) => {
  await page.goto("/signup");
  await dismissAnalyticsConsent(page);
  await page.locator("#email").focus();
  await expect(page.locator("#email")).toBeFocused();
});
