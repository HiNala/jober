import { test, expect } from "@playwright/test";

import {
  E2E_API_URL,
  importE2eWorkbook,
  seedReviewCheckpointRun,
  waitForRunStatus,
} from "./helpers/api";
import { waitForAppShell } from "./helpers/app-auth";
import { dismissAnalyticsConsent } from "./helpers/consent";
import { requireFullStack } from "./helpers/fullstack";

test.describe("core journey (fixture-backed)", () => {
  test.beforeEach(() => {
    requireFullStack();
  });

  test("import workbook → queue rows → dry-run batch enqueues", async ({ page, request }) => {
    await importE2eWorkbook(request);

    await page.goto("/queue");
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    await expect(page.getByRole("cell", { name: "Company 1" })).toBeVisible();
    await expect(page.getByTestId("job-queue-row")).toHaveCount(2, { timeout: 15_000 });

    await page.goto("/dashboard");
    await waitForAppShell(page);
    await page.getByRole("button", { name: "Preview dry-run" }).click();
    await expect(page.getByTestId("batch-preview-dialog")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Included" })).toBeVisible();
    await page.getByTestId("batch-enqueue").click();

    await expect
      .poll(
        async () => {
          const runs = await request.get(`${E2E_API_URL}/api/library/runs?limit=5`, {
            headers: {
              "X-Jober-Tenant-Id": "00000000-0000-4000-8000-000000000001",
              "X-Jober-User-Id": "00000000-0000-4000-8000-000000000002",
            },
          });
          if (!runs.ok()) return 0;
          const body = (await runs.json()) as { items?: unknown[] };
          return body.items?.length ?? 0;
        },
        { timeout: 120_000 },
      )
      .toBeGreaterThan(0);
  });

  test("run console resolves review checkpoint and survives reconnect", async ({
    page,
    request,
  }) => {
    const runId = await seedReviewCheckpointRun(request);

    await page.goto(`/runs/${runId}`);
    await dismissAnalyticsConsent(page);
    await waitForAppShell(page);

    const checkpoint = page.getByTestId("checkpoint-card");
    await expect(checkpoint).toBeVisible({ timeout: 30_000 });
    await expect(page.getByTestId("run-event-stream")).toBeVisible();

    await page.getByTestId("checkpoint-skip").click();
    await expect(checkpoint).toBeHidden({ timeout: 15_000 });

    await waitForRunStatus(request, runId, ["skipped", "succeeded", "failed_final"]);

    await page.reload();
    await waitForAppShell(page);
    await expect(page.getByTestId("run-event-stream")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Event stream" })).toBeVisible();
  });
});

test.use({
  storageState: undefined,
});
