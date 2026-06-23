import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchReadiness } from "@/lib/api/health";

describe("fetchReadiness", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns ready when /readyz reports ready", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: "ready", checks: {} }),
      }),
    );

    await expect(fetchReadiness()).resolves.toEqual({ status: "ready" });
  });

  it("returns degraded with check details when dependencies fail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        text: async () =>
          JSON.stringify({
            status: "not_ready",
            checks: { redis: { ok: false, detail: "connection refused" } },
          }),
      }),
    );

    await expect(fetchReadiness()).resolves.toEqual({
      status: "degraded",
      detail: "redis: connection refused",
    });
  });

  it("returns degraded with message when /readyz fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("Failed to fetch")),
    );

    const result = await fetchReadiness();
    expect(result.status).toBe("degraded");
    expect(result.detail).toContain("Failed to fetch");
  });
});
