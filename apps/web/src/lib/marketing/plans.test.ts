import { describe, expect, it } from "vitest";

import { MARKETING_PLANS } from "@/lib/marketing/plans";

/** Mirrors apps/api/src/jober_api/services/billing/entitlements.py */
const API_PLAN_LIMITS = {
  free: { maxMonthlyRuns: 20, maxBatchItems: 5, maxLlmBudgetUsd: 5 },
  pro: { maxMonthlyRuns: 500, maxBatchItems: 100, maxLlmBudgetUsd: 50 },
} as const;

describe("MARKETING_PLANS", () => {
  it("mirrors API entitlements source of truth", () => {
    for (const plan of MARKETING_PLANS) {
      const api = API_PLAN_LIMITS[plan.id];
      expect(plan.entitlements.maxMonthlyRuns).toBe(api.maxMonthlyRuns);
      expect(plan.entitlements.maxBatchItems).toBe(api.maxBatchItems);
      expect(plan.entitlements.maxLlmBudgetUsd).toBe(api.maxLlmBudgetUsd);
    }
  });

  it("has free and pro tiers", () => {
    expect(MARKETING_PLANS.map((p) => p.id)).toEqual(["free", "pro"]);
  });
});
