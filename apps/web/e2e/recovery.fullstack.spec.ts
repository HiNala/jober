import { test, expect } from "@playwright/test";

import { apiJson, fetchFixtureHtml, importE2eWorkbook } from "./helpers/api";
import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent, seedAnalyticsDeclinedCookie } from "./helpers/consent";
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
    const company2Jobs = jobs.body.items.filter((row) => row.company === "Company 2");
    const job = company2Jobs.at(-1);
    if (!job) throw new Error("missing Company 2 job after import");

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

    const reportRes = await apiJson<{ inferred_reason: string }>(
      request,
      "GET",
      `/api/job-targets/${job.id}/failure-report`,
    );
    expect(reportRes.status).toBe(200);
    expect(reportRes.body.inferred_reason).toBeTruthy();

    await seedAnalyticsDeclinedCookie(page);
    const jobsLoaded = page.waitForResponse(
      (response) => response.url().includes("/api/job-targets") && response.ok(),
    );
    await page.goto(`/queue?job=${job.id}`);
    await waitForAppShell(page);
    await dismissAnalyticsConsent(page);
    await jobsLoaded;
    await expect(page.locator(`[data-job-id="${job.id}"]`)).toBeVisible({ timeout: 15_000 });

    await expect(
      page.getByRole("heading", { name: new RegExp(`${job.company} —`) }),
    ).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("failure-report-panel")).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText(reportRes.body.inferred_reason)).toBeVisible();
  });
});
