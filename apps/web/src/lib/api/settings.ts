import { apiFetch } from "@/lib/api/client";

export type TenantPolicy = {
  plan: string;
  policy: {
    default_run_policy: string;
    auto_submit_opt_in: boolean;
    retention_days: number | null;
  };
  usage_guidance: Record<string, string>;
};

export async function fetchTenantPolicy(): Promise<TenantPolicy> {
  return apiFetch<TenantPolicy>("/api/settings/policy");
}
