import { describe, expect, it } from "vitest";

import { MARKETING_PLANS, planById } from "@/lib/marketing/plans";

describe("MARKETING_PLANS", () => {
  it("mirrors API entitlement limits for Free and Pro", () => {
    const free = planById("free");
    const pro = planById("pro");
    expect(free.entitlements).toEqual({
      maxBatchItems: 5,
      maxMonthlyRuns: 20,
      maxLlmBudgetUsd: 5,
    });
    expect(pro.entitlements).toEqual({
      maxBatchItems: 100,
      maxMonthlyRuns: 500,
      maxLlmBudgetUsd: 50,
    });
  });

  it("defines exactly two tiers", () => {
    expect(MARKETING_PLANS.map((p) => p.id)).toEqual(["free", "pro"]);
  });
});
