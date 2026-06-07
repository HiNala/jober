import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchTenantPolicy } from "@/lib/api/settings";

describe("fetchTenantPolicy", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns policy and usage guidance from API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          plan: "pro",
          policy: {
            default_run_policy: "review_before_submit",
            auto_submit_opt_in: false,
            retention_days: null,
          },
          usage_guidance: {
            auto_submit_disclosure: "auto_submit is opt-in only.",
          },
        }),
      }),
    );

    const result = await fetchTenantPolicy();
    expect(result.plan).toBe("pro");
    expect(result.policy.auto_submit_opt_in).toBe(false);
    expect(result.usage_guidance.auto_submit_disclosure).toContain("opt-in");
  });
});
