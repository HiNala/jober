import { test, expect } from "@playwright/test";

import { apiJson, importE2eWorkbook } from "./helpers/api";
import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { requireFullStack } from "./helpers/fullstack";

test.describe("settings policy default", () => {
  test.beforeEach(() => {
    requireFullStack();
  });

  test("tenant default pre-selects batch policy", async ({ page, request }) => {
    await importE2eWorkbook(request);

    await page.goto("/settings");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    await page.locator("#run-policy").selectOption("dry_run");
    await expect.poll(async () => {
      const policy = await apiJson<{ policy: { default_run_policy: string } }>(
        request,
        "GET",
        "/api/settings/policy",
      );
      return policy.body.policy.default_run_policy;
    }).toBe("dry_run");

    await page.goto("/dashboard");
    await waitForAppShell(page);
    await page.getByTestId("preview-batch-tenant-default").click();

    await expect(page.getByTestId("batch-preview-dialog")).toBeVisible();
    await expect(page.locator('input[name="batch-policy"][value="dry_run"]')).toBeChecked();
  });
});
