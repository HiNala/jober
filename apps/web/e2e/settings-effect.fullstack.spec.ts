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

    await apiJson(request, "PUT", "/api/settings/policy", {
      data: {
        default_run_policy: "review_before_submit",
        auto_submit_opt_in: false,
      },
    });

    await page.goto("/dashboard");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);
    await page.getByTestId("preview-batch-tenant-default").click();

    await expect(page.getByTestId("batch-preview-dialog")).toBeVisible();
    await expect(page.locator('input[name="batch-policy"][value="review_before_submit"]')).toBeChecked();
  });
});
