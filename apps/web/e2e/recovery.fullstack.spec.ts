import { test, expect } from "@playwright/test";

import { apiJson, fetchFixtureHtml, importE2eWorkbook } from "./helpers/api";
import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { requireFullStack } from "./helpers/fullstack";

test.describe("recovery (login gate)", () => {
  test.beforeEach(() => {
    requireFullStack();
  });

  test("login-wall fixture surfaces failure report in job drawer", async ({ page, request }) => {
    await importE2eWorkbook(request);
    const jobs = await apiJson<{ items: { id: string; company: string }[] }>(
      request,
      "GET",
      "/api/job-targets?priority=A&limit=50",
    );
    const job = jobs.body.items.at(-1);
    if (!job) throw new Error("missing job after import");

    const loginHtml = await fetchFixtureHtml(request, "gates/login");
    const extract = await apiJson<{ detail?: { gate?: string; run_id?: string } }>(
      request,
      "POST",
      `/api/job-targets/${job.id}/extract`,
      {
        data: {
          fixture_html: loginHtml,
          fixture_url: "https://example.com/login",
          force: true,
        },
      },
    );
    expect(extract.status).toBe(409);
    expect(extract.body.detail?.gate).toBe("login");

    await expect
      .poll(async () => {
        const report = await apiJson(request, "GET", `/api/job-targets/${job.id}/failure-report`);
        return report.status;
      })
      .toBe(200);

    await page.goto("/queue");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    const jobRow = page.locator(`[data-job-id="${job.id}"]`);
    await expect(jobRow).toBeVisible({ timeout: 15_000 });
    const failureReportResponse = page.waitForResponse(
      (response) =>
        response.url().includes(`/api/job-targets/${job.id}/failure-report`) &&
        response.status() === 200,
    );
    await jobRow.click();
    await failureReportResponse;
    await expect(page.getByTestId("failure-report-panel")).toBeVisible({ timeout: 15_000 });
  });
});
