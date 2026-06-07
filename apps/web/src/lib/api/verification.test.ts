import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { ApiError } from "@/lib/api/client";
import { fetchReviewPackage } from "@/lib/api/verification";

describe("verification api helpers", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns null when no run awaits review", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("not found", { status: 404, statusText: "Not Found" }),
    );

    await expect(fetchReviewPackage("job-1")).resolves.toBeNull();
  });

  it("rethrows non-404 API errors", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("server error", { status: 500, statusText: "Error" }),
    );

    await expect(fetchReviewPackage("job-1")).rejects.toBeInstanceOf(ApiError);
  });
});
