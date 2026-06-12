import { readFileSync } from "node:fs";
import { join } from "node:path";

import type { APIRequestContext } from "@playwright/test";

import { E2E_DEV_TENANT_ID, E2E_DEV_USER_ID } from "./app-auth";

/** Playwright runs with cwd `apps/web` (see package.json / CI working-directory). */
const E2E_WORKBOOK_PATH = join(process.cwd(), "e2e", "fixtures", "jobs.xlsx");

export const E2E_API_URL = process.env.E2E_API_URL ?? process.env.API_URL ?? "http://localhost:8000";

export const FIXTURE_ATS_BASE = (
  process.env.FIXTURE_ATS_BASE ?? "http://127.0.0.1:8765"
).replace(/\/$/, "");

export function devAuthHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    "X-Jober-Tenant-Id": E2E_DEV_TENANT_ID,
    "X-Jober-User-Id": E2E_DEV_USER_ID,
    ...extra,
  };
}

export async function apiJson<T>(
  request: APIRequestContext,
  method: "GET" | "POST" | "PATCH" | "PUT",
  path: string,
  options?: { data?: unknown; multipart?: Parameters<APIRequestContext["fetch"]>[1] },
): Promise<{ status: number; body: T; headers: Record<string, string> }> {
  const response = await request.fetch(`${E2E_API_URL}${path}`, {
    method,
    headers: devAuthHeaders(
      options?.data !== undefined ? { "Content-Type": "application/json" } : undefined,
    ),
    data: options?.data,
    multipart: options?.multipart as never,
  });
  const text = await response.text();
  const body = text ? (JSON.parse(text) as T) : (undefined as T);
  const headers: Record<string, string> = {};
  for (const [key, value] of Object.entries(response.headers())) {
    headers[key.toLowerCase()] = value;
  }
  return { status: response.status(), body, headers };
}

export async function fetchFixtureHtml(
  request: APIRequestContext,
  slug: string,
): Promise<string> {
  const response = await request.get(`${FIXTURE_ATS_BASE}/${slug}`);
  if (!response.ok()) {
    throw new Error(`Fixture fetch failed ${slug}: ${response.status()}`);
  }
  return response.text();
}

export async function importE2eWorkbook(request: APIRequestContext): Promise<void> {
  const buffer = readFileSync(E2E_WORKBOOK_PATH);
  const response = await request.post(`${E2E_API_URL}/api/imports/jobs-xlsx`, {
    headers: devAuthHeaders(),
    multipart: {
      file: {
        name: "jobs.xlsx",
        mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        buffer,
      },
    },
  });
  if (!response.ok()) {
    throw new Error(`import failed: ${response.status()} ${await response.text()}`);
  }
}

/** Golden-path API setup: discover → fill → verify-ready → review checkpoint. */
export async function seedReviewCheckpointRun(request: APIRequestContext): Promise<string> {
  let jobs = await apiJson<{ items: { id: string; company: string }[] }>(
    request,
    "GET",
    "/api/job-targets?priority=A&limit=5",
  );
  if (!jobs.body.items.length) {
    await importE2eWorkbook(request);
    jobs = await apiJson(request, "GET", "/api/job-targets?priority=A&limit=5");
  }
  const jobId = jobs.body.items[1]?.id ?? jobs.body.items[0]?.id;
  if (!jobId) {
    throw new Error("No job targets after import");
  }

  const atsHtml = await fetchFixtureHtml(request, "behaviors/single-step");
  const submitHtml = await fetchFixtureHtml(request, "behaviors/submit-success");

  const discover = await apiJson(request, "POST", `/api/job-targets/${jobId}/discover-form`, {
    data: { fixture_html: atsHtml, platform: "greenhouse" },
  });
  if (discover.status >= 400) {
    throw new Error(`discover-form failed: ${discover.status} ${JSON.stringify(discover.body)}`);
  }

  const fill = await apiJson<{ run_id: string }>(
    request,
    "POST",
    `/api/job-targets/${jobId}/fill-form`,
    { data: { fixture_html: atsHtml } },
  );
  if (fill.status >= 400) {
    throw new Error(`fill-form failed: ${fill.status} ${JSON.stringify(fill.body)}`);
  }

  const verify = await apiJson<{ run_id: string; status: string }>(
    request,
    "POST",
    `/api/job-targets/${jobId}/verify-ready`,
    { data: { fixture_html: submitHtml } },
  );
  if (verify.status >= 400) {
    throw new Error(`verify-ready failed: ${verify.status}`);
  }
  return verify.body.run_id;
}

export async function waitForRunStatus(
  request: APIRequestContext,
  runId: string,
  statuses: string[],
  timeoutMs = 120_000,
): Promise<string> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const console = await apiJson<{ status: string }>(
      request,
      "GET",
      `/api/application-runs/${runId}/console`,
    );
    if (console.status === 200 && statuses.includes(console.body.status)) {
      return console.body.status;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Run ${runId} did not reach ${statuses.join("|")} within ${timeoutMs}ms`);
}
