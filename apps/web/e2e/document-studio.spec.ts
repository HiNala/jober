import { test, expect } from "@playwright/test";

import { dismissAnalyticsConsent } from "./helpers/consent";
import { waitForAppShell } from "./helpers/app-auth";

test("library cover letters: studio sub-nav and saved list", async ({ page }) => {
  await page.goto("/library?tab=letters");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);

  await expect(page.getByRole("navigation", { name: /cover letter views/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /document studio/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /saved letters/i })).toBeVisible();

  await page.getByRole("link", { name: /document studio/i }).click();
  await expect(page.getByRole("link", { name: /document studio/i })).toHaveAttribute(
    "aria-current",
    "page",
  );

  const studioRegion = page.getByRole("region", { name: /document studio/i });
  await expect(studioRegion).toBeVisible();

  const jobPicker = page.getByRole("combobox", { name: /select job/i });
  const noJobsEmpty = page.getByRole("heading", { name: /add jobs to generate letters/i });
  const jobsError = page.getByRole("heading", { name: /could not load jobs/i });
  await expect(jobPicker.or(noJobsEmpty).or(jobsError)).toBeVisible();
});

test("/documents redirects to document studio", async ({ page }) => {
  await page.goto("/documents");
  await dismissAnalyticsConsent(page);
  await waitForAppShell(page);
  await expect(page).toHaveURL(/\/library\?tab=letters&view=studio/);
  await expect(page.getByRole("link", { name: /document studio/i })).toHaveAttribute(
    "aria-current",
    "page",
  );
});
