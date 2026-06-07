import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { ApiError } from "@/lib/api/client";
import { fetchFailureReportForJob } from "@/lib/api/recovery";

describe("recovery api helpers", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns null when job has no failure report", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("not found", { status: 404, statusText: "Not Found" }),
    );

    await expect(fetchFailureReportForJob("job-1")).resolves.toBeNull();
  });

  it("rethrows non-404 API errors", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("server error", { status: 500, statusText: "Error" }),
    );

    await expect(fetchFailureReportForJob("job-1")).rejects.toBeInstanceOf(ApiError);
  });
});
