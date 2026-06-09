import { apiFetch } from "@/lib/api/client";

export type DateRange = { start: string; end: string };

export type UserAnalytics = {
  range: DateRange;
  summary: {
    applications_sent: number;
    responses_tracked: number;
    letters_generated: number;
    llm_cost_usd: number;
    llm_budget_usd: number;
    budget_used_ratio: number;
  };
  activity: Array<{ day: string; runs: number }>;
  cost_series: Array<{ day: string; cost_usd: number }>;
  attention: Array<{ level: string; message: string }>;
  previous?: UserAnalytics["summary"];
};

export type FunnelStep = {
  step: string;
  event_name: string;
  event_count: number;
  unique_sessions: number;
  drop_off_sessions: number;
  drop_off_rate: number;
};

export type FunnelDashboard = {
  range: DateRange;
  steps: FunnelStep[];
  previous_steps?: FunnelStep[];
};

export type TrafficDashboard = {
  range: DateRange;
  pages: Array<{
    page: string;
    page_views: number;
    unique_sessions: number;
    avg_time_on_page_sec: number;
    bounce_rate: number;
  }>;
  active_users: Array<{ day: string; dau: number; wau: number; mau: number }>;
  totals: { page_views: number; sessions: number };
};

export type CostDashboard = {
  range: DateRange;
  rollup_total_usd: number;
  llm_call_total_usd: number;
  reconciled: boolean;
  by_day: Array<{ day: string; cost_usd: number }>;
  by_model: Array<{ model: string; cost_usd: number }>;
  by_agent: Array<{ agent_role: string; cost_usd: number }>;
  anomalies: Array<{ day: string; cost_usd: number }>;
  attention: Array<{ level: string; message: string }>;
};

export type AnalyticsRangePreset = "7d" | "30d" | "90d";

export function rangeFromPreset(preset: AnalyticsRangePreset): { start: string; end: string } {
  const end = new Date();
  const start = new Date(end);
  const days = preset === "7d" ? 6 : preset === "30d" ? 29 : 89;
  start.setDate(end.getDate() - days);
  return { start: start.toISOString().slice(0, 10), end: end.toISOString().slice(0, 10) };
}

function rangeQuery(
  range: { start: string; end: string },
  comparePrevious?: boolean,
): string {
  const params = new URLSearchParams({ start: range.start, end: range.end });
  if (comparePrevious) params.set("compare_previous", "true");
  return params.toString();
}

export function fetchUserAnalytics(
  range: { start: string; end: string },
  comparePrevious = false,
): Promise<UserAnalytics> {
  return apiFetch(`/api/analytics/me?${rangeQuery(range, comparePrevious)}`);
}

export function fetchAdminFunnel(
  range: { start: string; end: string },
  comparePrevious = false,
): Promise<FunnelDashboard> {
  return apiFetch(`/api/analytics/admin/funnel?${rangeQuery(range, comparePrevious)}`);
}

export function fetchAdminTraffic(range: { start: string; end: string }): Promise<TrafficDashboard> {
  return apiFetch(`/api/analytics/admin/traffic?${rangeQuery(range)}`);
}

export function fetchAdminCost(range: { start: string; end: string }): Promise<CostDashboard> {
  return apiFetch(`/api/analytics/admin/cost?${rangeQuery(range)}`);
}

export function exportCsvUrl(path: string, range: { start: string; end: string }): string {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return `${base}${path}?${rangeQuery(range)}`;
}
