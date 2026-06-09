/**
 * Marketing plan copy — mirrors `PLAN_ENTITLEMENTS` in
 * `apps/api/src/jober_api/services/billing/entitlements.py`.
 */
export type MarketingPlanId = "free" | "pro";

export type MarketingPlan = {
  id: MarketingPlanId;
  name: string;
  priceLabel: string;
  priceNote?: string;
  description: string;
  entitlements: {
    maxBatchItems: number;
    maxMonthlyRuns: number;
    maxLlmBudgetUsd: number;
  };
  highlights: string[];
};

export const MARKETING_PLANS: MarketingPlan[] = [
  {
    id: "free",
    name: "Free",
    priceLabel: "$0",
    priceNote: "per month",
    description: "Everything you need to run assisted applications with review-before-submit.",
    entitlements: {
      maxBatchItems: 5,
      maxMonthlyRuns: 20,
      maxLlmBudgetUsd: 5,
    },
    highlights: [
      "Job queue, profile vault, and document studio",
      "Live run console with human checkpoints",
      "Review and approve every submit",
      "First-party analytics in your workspace",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    priceLabel: "Coming soon",
    priceNote: "paid monthly via Stripe",
    description: "Higher limits for active pipelines and batch scheduling at scale.",
    entitlements: {
      maxBatchItems: 100,
      maxMonthlyRuns: 500,
      maxLlmBudgetUsd: 50,
    },
    highlights: [
      "Everything in Free",
      "Larger batches and monthly run allowance",
      "Higher managed LLM budget for letters and fills",
      "Priority support as we roll out billing",
    ],
  },
];

export function planById(id: MarketingPlanId): MarketingPlan {
  const plan = MARKETING_PLANS.find((p) => p.id === id);
  if (!plan) throw new Error(`Unknown plan: ${id}`);
  return plan;
}
