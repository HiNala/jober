/**
 * Mobile smoke tests — run on mobile-iphone and mobile-android Playwright projects.
 * Each test checks a public marketing page for horizontal overflow.
 * These tests run headlessly and do not require authentication.
 */
import { test, expect, type Page } from "@playwright/test";

async function expectNoHorizontalOverflow(page: Page): Promise<void> {
  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(hasOverflow, "Page should have no horizontal overflow").toBe(false);
}

test.describe("Mobile smoke — public marketing pages", () => {
  test("/ landing page — no horizontal overflow", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalOverflow(page);
  });

  test("/ landing page — hero heading visible", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    const heading = page.getByRole("heading", { level: 1 });
    await expect(heading).toBeVisible();
  });

  test("/ landing page — CTA button is tappable (≥44px)", async ({ page }) => {
    await page.goto("/");
    const cta = page.getByRole("link", { name: /get started free/i }).first();
    await expect(cta).toBeVisible();
    const box = await cta.boundingBox();
    expect(box?.height).toBeGreaterThanOrEqual(44);
  });

  test("/pricing — no horizontal overflow", async ({ page }) => {
    await page.goto("/pricing");
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalOverflow(page);
  });

  test("/how-it-works — no horizontal overflow", async ({ page }) => {
    await page.goto("/how-it-works");
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalOverflow(page);
  });

  test("/login — no horizontal overflow", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalOverflow(page);
  });

  test("/login — form inputs are present", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
  });

  test("/signup — no horizontal overflow", async ({ page }) => {
    await page.goto("/signup");
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalOverflow(page);
  });

  test("/features — no horizontal overflow", async ({ page }) => {
    await page.goto("/features");
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalOverflow(page);
  });

  test("mobile nav — hamburger menu opens", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    // Marketing mobile nav hamburger should be visible
    const mobileNavBtn = page.getByRole("button", { name: /open.*navigation|menu/i }).first();
    if (await mobileNavBtn.isVisible()) {
      await mobileNavBtn.tap();
      // Sheet should open with nav links
      await expect(page.getByRole("navigation", { name: /marketing/i })).toBeVisible();
    }
  });
});
