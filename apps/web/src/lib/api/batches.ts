import { apiFetch } from "./client";

export type DashboardSummary = {
  queue_depth_priority_a: number;
  active_runs: number;
  needs_review: number;
  worker: {
    globally_paused: boolean;
    max_concurrency: number;
    active_runs: number;
    active_run_ids: string[];
  };
  batches: Array<{
    id: string;
    name: string;
    status: string;
    policy: string;
    counts: Record<string, number>;
  }>;
};

export type DailyPlan = {
  summary: string;
  proposed_filters: Record<string, unknown>;
  pacing_note: string;
};

export type BatchPolicy = "dry_run" | "review_before_submit";

export type BatchPreviewJob = {
  job_target_id: string;
  company: string;
  role: string;
  priority?: string;
  domain?: string;
  apply_url?: string | null;
  reason?: string;
};

export type BatchPreviewResult = {
  filters: Record<string, unknown>;
  included: BatchPreviewJob[];
  excluded: BatchPreviewJob[];
  domain_count: number;
  estimated_cost_usd: number;
};

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>("/api/dashboard/summary");
}

export async function fetchDailyPlan(): Promise<DailyPlan> {
  return apiFetch<DailyPlan>("/api/batches/daily-plan");
}

export async function pauseAllQueue(): Promise<void> {
  await apiFetch("/api/queue/pause-all", { method: "POST" });
}

export async function resumeAllQueue(): Promise<void> {
  await apiFetch("/api/queue/resume-all", { method: "POST" });
}

export async function previewBatch(filters: Record<string, unknown>): Promise<BatchPreviewResult> {
  return apiFetch<BatchPreviewResult>("/api/batches/preview", {
    method: "POST",
    body: JSON.stringify({ filters }),
  });
}

export async function createBatch(body: Record<string, unknown>) {
  return apiFetch("/api/batches", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function enqueueBatch(batchId: string) {
  return apiFetch(`/api/batches/${batchId}/enqueue`, { method: "POST", body: "{}" });
}
