import { expect, type Page } from "@playwright/test";

/** Skip the consent sheet by pre-setting the decline cookie (stable under overlays). */
export async function seedAnalyticsDeclinedCookie(page: Page): Promise<void> {
  const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";
  await page.context().addCookies([
    { name: "jober_analytics_consent", value: "0", url: baseURL },
  ]);
}

/** Dismiss the one-time analytics consent sheet when present (fresh profile). */
export async function dismissAnalyticsConsent(page: Page): Promise<void> {
  await seedAnalyticsDeclinedCookie(page);

  const decline = page.getByRole("button", { name: "Decline" });
  const dialog = page.getByRole("dialog", { name: /first-party analytics/i });
  try {
    await decline.waitFor({ state: "visible", timeout: 5000 });
  } catch {
    return;
  }

  await decline.click({ timeout: 5000, noWaitAfter: true }).catch(async () => {
    await page.keyboard.press("Escape");
  });
  await expect(dialog).not.toBeVisible({ timeout: 5000 });
}
