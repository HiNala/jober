import { expect, type Page } from "@playwright/test";

/** Dismiss the one-time analytics consent sheet when present (fresh profile). */
export async function dismissAnalyticsConsent(page: Page): Promise<void> {
  const decline = page.getByRole("button", { name: "Decline" });
  try {
    await decline.waitFor({ state: "visible", timeout: 5000 });
  } catch {
    return;
  }
  await decline.click();
  await expect(page.getByRole("dialog", { name: /first-party analytics/i })).not.toBeVisible();
}
