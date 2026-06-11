import AxeBuilder from "@axe-core/playwright";
import { test, expect } from "@playwright/test";

import { dismissAnalyticsConsent } from "./helpers/consent";
import { MARKETING_A11Y_ROUTES } from "./marketing-routes";

for (const path of MARKETING_A11Y_ROUTES) {
  test(`axe clean: ${path}`, async ({ page }) => {
    await page.goto(path);
    await dismissAnalyticsConsent(page);
    await expect(page.locator("h1").first()).toBeVisible();

    const results = await new AxeBuilder({ page })
      .disableRules(["color-contrast"])
      .analyze();

    expect(
      results.violations,
      JSON.stringify(results.violations, null, 2),
    ).toEqual([]);
  });
}

test("keyboard: skip link focuses main content", async ({ page }) => {
  await page.goto("/");
  await dismissAnalyticsConsent(page);
  await page.keyboard.press("Tab");
  const skip = page.getByRole("link", { name: /skip to main content/i });
  await expect(skip).toBeFocused();
  await skip.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
});

test("reduced motion: hero renders without animation errors", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await dismissAnalyticsConsent(page);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});
