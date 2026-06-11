import { test, expect } from "@playwright/test";

import { E2E_FIXTURE_RUN_ID, waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { assertNoHorizontalOverflow, VIEWPORTS } from "./helpers/responsive";

const MARKETING_ROUTES = ["/", "/pricing", "/signup", "/login"] as const;

const APP_ROUTES = ["/dashboard", "/queue", "/settings"] as const;

for (const [label, viewport] of Object.entries(VIEWPORTS) as [
  keyof typeof VIEWPORTS,
  (typeof VIEWPORTS)[keyof typeof VIEWPORTS],
][]) {
  test.describe(`viewport ${label} (${viewport.width}px)`, () => {
    test.use({ viewport });

    for (const path of MARKETING_ROUTES) {
      test(`no overflow: ${path}`, async ({ page }) => {
        await page.goto(path);
        await dismissAnalyticsConsent(page);
        await assertNoHorizontalOverflow(page);
      });
    }

    test("marketing home: primary CTA visible", async ({ page }) => {
      await page.goto("/");
      await dismissAnalyticsConsent(page);
      await expect(page.getByRole("link", { name: /get started|start free/i }).first()).toBeVisible();
    });

    for (const path of APP_ROUTES) {
      test(`no overflow (app): ${path}`, async ({ page }) => {
        await page.goto(path);
        await dismissAnalyticsConsent(page);
        await waitForAppShell(page);
        await assertNoHorizontalOverflow(page);
      });
    }

    test("app: mobile nav trigger visible", async ({ page }) => {
      await page.goto("/dashboard");
      await dismissAnalyticsConsent(page);
      await waitForAppShell(page);
      await expect(page.getByRole("button", { name: "Open navigation menu" })).toBeVisible();
    });

    test("app: touch command palette trigger visible", async ({ page }) => {
      await page.goto("/dashboard");
      await dismissAnalyticsConsent(page);
      await waitForAppShell(page);
      await expect(page.getByRole("button", { name: "Open command palette" }).first()).toBeVisible();
    });

    test("marketing: mobile menu trigger visible", async ({ page }) => {
      await page.goto("/");
      await dismissAnalyticsConsent(page);
      await expect(page.getByRole("button", { name: "Open marketing menu" })).toBeVisible();
    });

    test("run console: Work and Canvas tabs", async ({ page }) => {
      await page.goto(`/runs/${E2E_FIXTURE_RUN_ID}`);
      await dismissAnalyticsConsent(page);
      await waitForAppShell(page);
      await expect(page.getByRole("tab", { name: "Work" })).toBeVisible();
      await expect(page.getByRole("tab", { name: "Canvas" })).toBeVisible();
      await assertNoHorizontalOverflow(page);
    });

    test("run console: header canvas button switches tab", async ({ page }) => {
      await page.goto(`/runs/${E2E_FIXTURE_RUN_ID}`);
      await dismissAnalyticsConsent(page);
      await waitForAppShell(page);
      await page.getByRole("button", { name: "Show canvas" }).click();
      await expect(page.getByRole("tab", { name: "Canvas" })).toHaveAttribute("aria-selected", "true");
    });

    test("run console: work surface mounts (stream or API error)", async ({ page }) => {
      await page.goto(`/runs/${E2E_FIXTURE_RUN_ID}`);
      await dismissAnalyticsConsent(page);
      await waitForAppShell(page);
      const eventStream = page.getByRole("heading", { name: "Event stream" });
      const unavailable = page.getByRole("heading", { name: "Run console unavailable" });
      await expect(eventStream.or(unavailable)).toBeVisible({ timeout: 15_000 });
    });
  });
}
