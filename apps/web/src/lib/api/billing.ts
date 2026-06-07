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

export async function fetchUsageDashboard(): Promise<UsageDashboard> {
  return apiFetch<UsageDashboard>("/api/billing/usage");
}
