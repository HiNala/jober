import { test, expect } from "@playwright/test";

import { dismissAnalyticsConsent } from "./helpers/consent";

test("signup keeps input and shows inline password error", async ({ page }) => {
  await page.goto("/signup");
  await dismissAnalyticsConsent(page);

  await page.locator("#email").fill("keeper@example.com");
  await page.locator("#password").fill("short");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.getByText(/at least 10 characters/i)).toBeVisible();
  await expect(page.locator("#email")).toHaveValue("keeper@example.com");
  await expect(page.locator("#password")).toHaveValue("short");
});

test("signup rejects invalid email before submit", async ({ page }) => {
  await page.goto("/signup");
  await dismissAnalyticsConsent(page);

  await page.locator("#email").fill("not-an-email");
  await page.locator("#password").fill("ValidPass123!");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.getByText(/valid email/i)).toBeVisible();
  await expect(page.locator("#email")).toHaveValue("not-an-email");
});
