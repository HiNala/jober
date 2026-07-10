import { apiFetch } from "@/lib/api/client";

export type UsageDashboard = {
  plan: string;
  limits: {
    max_batch_items: number;
    max_monthly_runs: number;
    max_llm_budget_usd: number;
  };
  usage: {
    monthly_runs: number;
    documents_generated: number;
    llm_cost_usd: number;
  };
  remaining: {
    monthly_runs: number;
    llm_budget_usd: number;
  };
};

export type BillingStatus = {
  stripe_enabled: boolean;
  plan: string;
  has_stripe_customer: boolean;
  subscription_ends_at: string | null;
};

export async function fetchUsageDashboard(): Promise<UsageDashboard> {
  return apiFetch<UsageDashboard>("/api/billing/usage");
}

/** Prefer runtime API status; falls back to NEXT_PUBLIC_STRIPE_ENABLED. */
export function isStripeEnabledClient(): boolean {
  return process.env.NEXT_PUBLIC_STRIPE_ENABLED === "true";
}

export async function fetchBillingStatus(): Promise<BillingStatus> {
  return apiFetch<BillingStatus>("/api/billing/status");
}

export async function createCheckoutSession(input: {
  successUrl: string;
  cancelUrl: string;
}): Promise<{ url: string }> {
  return apiFetch<{ url: string }>("/api/billing/checkout-session", {
    method: "POST",
    body: JSON.stringify({
      success_url: input.successUrl,
      cancel_url: input.cancelUrl,
    }),
  });
}

export async function createPortalSession(input: {
  returnUrl: string;
}): Promise<{ url: string }> {
  return apiFetch<{ url: string }>("/api/billing/portal-session", {
    method: "POST",
    body: JSON.stringify({
      return_url: input.returnUrl,
    }),
  });
}
