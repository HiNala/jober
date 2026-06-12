import { test, expect } from "@playwright/test";

import { E2E_API_URL } from "./helpers/api";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { requireFullStack } from "./helpers/fullstack";

test.describe("auth lifecycle", () => {
  test.beforeEach(() => {
    requireFullStack();
    test.skip(
      process.env.E2E_AUTH_NATIVE !== "1",
      "Set E2E_AUTH_NATIVE=1 with API AUTH_MODE=native and DEV_AUTH_BYPASS=false",
    );
  });

  test("signup → verify → login → logout", async ({ page, request }) => {
    const email = `e2e-${Date.now()}@example.com`;
    const password = "Str0ng!Passw0rd";

    const register = await request.post(`${E2E_API_URL}/api/auth/register`, {
      data: {
        email,
        password,
        display_name: "E2E User",
      },
    });
    expect(register.ok()).toBeTruthy();
    const verifyToken = register.headers()["x-jober-verify-token"];
    expect(verifyToken).toBeTruthy();

    const verify = await request.post(`${E2E_API_URL}/api/auth/verify-email`, {
      data: { token: verifyToken },
    });
    expect(verify.ok()).toBeTruthy();

    await page.goto("/login");
    await dismissAnalyticsConsent(page);
    await page.locator("#email").fill(email);
    await page.locator("#password").fill(password);
    await page.getByRole("button", { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 20_000 });
    await expect(page.getByRole("button", { name: "Workspace menu" })).toBeVisible();

    await page.goto("/settings");
    await page.getByRole("button", { name: "Sign out on this device" }).click();
    await expect(page).toHaveURL(/\/login/);
  });
});
