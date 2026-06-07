import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { ApiError } from "@/lib/api/client";
import { fetchFieldObservations } from "@/lib/api/forms";

describe("forms api helpers", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns empty list when observations are missing", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("not found", { status: 404, statusText: "Not Found" }),
    );

    await expect(fetchFieldObservations("job-1")).resolves.toEqual([]);
  });

  it("rethrows non-404 API errors", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response("server error", { status: 500, statusText: "Error" }),
    );

    await expect(fetchFieldObservations("job-1")).rejects.toBeInstanceOf(ApiError);
  });
});
