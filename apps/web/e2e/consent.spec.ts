import { test, expect } from "@playwright/test";

test.describe("analytics consent sheet", () => {
  test.beforeEach(async ({ context }) => {
    await context.clearCookies();
    await context.addInitScript(() => {
      localStorage.removeItem("jober_analytics_consent_prompted");
    });
  });

  test("shows once until the user declines", async ({ page }) => {
    await page.goto("/");
    const sheet = page.getByRole("dialog", { name: /first-party analytics/i });
    await expect(sheet).toBeVisible();
    await page.getByRole("button", { name: "Decline" }).click();
    await expect(sheet).not.toBeVisible();

    await page.reload();
    await expect(sheet).not.toBeVisible();
  });

  test("accept enables analytics cookie", async ({ page, context }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Accept" }).click();
    const cookies = await context.cookies();
    const consent = cookies.find((c) => c.name === "jober_analytics_consent");
    expect(consent?.value).toBe("1");
  });
});
