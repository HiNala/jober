import { test, expect } from "@playwright/test";

import { importE2eWorkbook } from "./helpers/api";
import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { requireFullStack } from "./helpers/fullstack";

test.describe("document studio cycle", () => {
  test.beforeEach(() => {
    requireFullStack();
  });

  test("generate → lock → regen → download PDF", async ({ page, request }) => {
    await importE2eWorkbook(request);

    await page.goto("/library?tab=letters&view=studio");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    await page.getByRole("combobox", { name: "Select job" }).click();
    await page.getByRole("option").first().click();

    await page.getByTestId("studio-generate").click();
    await expect(page.getByTestId("letter-preview")).toBeVisible({ timeout: 30_000 });

    await page.getByTestId("paragraph-lock-0").click();
    const beforeLock = await page.locator('[data-testid="letter-preview"]').inputValue();

    await page.getByTestId("paragraph-regen-1").click();
    await expect(page.getByTestId("letter-preview")).not.toHaveValue(beforeLock, {
      timeout: 30_000,
    });

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByTestId("studio-download-pdf").click(),
    ]);
    const name = download.suggestedFilename();
    expect(name.toLowerCase()).toContain(".pdf");
  });
});
