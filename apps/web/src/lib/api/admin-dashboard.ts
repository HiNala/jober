import { apiFetch } from "@/lib/api/client";
import type { CostDashboard, FunnelDashboard, TrafficDashboard } from "@/lib/api/analytics-dashboard";

export type AdminAttention = { level: string; message: string };

export type AdminOverview = {
  as_of: string;
  active_users: { dau: number; wau: number; mau: number; day: string | null };
  signups: { today: number; last_7d: number; last_30d: number };
  runs: {
    total: number;
    succeeded: number;
    failed: number;
    needs_human: number;
    by_status: Record<string, number>;
  };
  submits_30d: number;
  cost: {
    last_30d_usd: number;
    forecast_monthly_usd: number;
    reconciled: boolean;
  };
  health: {
    status: string;
    checks: Record<string, { ok: boolean; detail: string }>;
    queue: {
      globally_paused: boolean;
      max_concurrency: number;
      active_runs: number;
    };
  };
  attention: AdminAttention[];
};

export type AdminRunsSummary = {
  range: { start: string; end: string };
  totals: {
    runs: number;
    succeeded: number;
    failed: number;
    retryable: number;
    needs_human_backlog: number;
    recovery_rate: number;
  };
  by_status: Record<string, number>;
  failures_by_platform: Array<{
    platform: string;
    failure_class: string;
    count: number;
  }>;
  attention: AdminAttention[];
};

export type AdminAcquisition = {
  range: { start: string; end: string };
  signups: number;
  funnel_signups: number;
  funnel: FunnelDashboard;
  traffic: TrafficDashboard;
  utm_sources: Array<{ utm_source: string; utm_medium: string | null; sessions: number }>;
  geo: Array<{ country: string; sessions: number }>;
};

export type ProductConfigEntry = {
  key: string;
  value: Record<string, unknown>;
  updated_at: string | null;
};

export type AdminUserOperational = {
  user: Record<string, unknown>;
  tenant: Record<string, unknown>;
  usage_30d: Record<string, unknown>;
  data_requests: Array<Record<string, unknown>>;
  privacy_note: string;
};

export function fetchAdminOverview(): Promise<AdminOverview> {
  return apiFetch("/api/admin/overview");
}

export function fetchAdminRuns(): Promise<AdminRunsSummary> {
  return apiFetch("/api/admin/runs");
}

export function fetchAdminAcquisition(): Promise<AdminAcquisition> {
  return apiFetch("/api/admin/acquisition");
}

export function fetchAdminCostDashboard(): Promise<CostDashboard> {
  return apiFetch("/api/admin/cost");
}

export function fetchAdminSystem(): Promise<{ health: AdminOverview["health"]; attention: AdminAttention[] }> {
  return apiFetch("/api/admin/system");
}

export function fetchProductConfig(): Promise<{ items: ProductConfigEntry[] }> {
  return apiFetch("/api/admin/config/");
}

export function updateProductConfig(
  key: string,
  value: Record<string, unknown>,
): Promise<ProductConfigEntry> {
  return apiFetch(`/api/admin/config/${key}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
}

export function fetchAdminDataRequests(): Promise<{
  items: Array<{
    id: string;
    tenant_id: string;
    user_id: string | null;
    action: string;
    message: string;
    ts: string;
  }>;
}> {
  return apiFetch("/api/admin/data-requests");
}

export function fetchUserOperational(userId: string): Promise<AdminUserOperational> {
  return apiFetch(`/api/admin/users/${userId}/operational`);
}
