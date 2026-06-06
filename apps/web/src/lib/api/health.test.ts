import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchReadiness } from "@/lib/api/health";

describe("fetchReadiness", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns ready when /readyz succeeds", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({}),
      }),
    );

    await expect(fetchReadiness()).resolves.toEqual({ status: "ready" });
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
