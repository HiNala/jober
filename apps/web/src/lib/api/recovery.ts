import { ApiError, apiFetch } from "@/lib/api/client";

export interface FailureReport {
  job_target_id: string;
  company: string;
  role: string;
  apply_url?: string | null;
  failed_step: string;
  failure_class: string;
  inferred_reason: string;
  recommended_manual_action: string;
  safe_to_retry: boolean;
  attempt_count: number;
  screenshot_object_key?: string | null;
  self_assessments?: Array<{
    attempt_index: number;
    strategy_name: string;
    tried: string;
    happened: string;
    next_change: string;
  }>;
}

export interface FailureAnalytics {
  buckets: Array<{
    platform: string;
    failure_class: string;
    count: number;
    circuit_tripped: boolean;
  }>;
  alerts: Array<Record<string, unknown>>;
}

export async function fetchFailureReportForJob(
  jobTargetId: string,
): Promise<FailureReport | null> {
  try {
    return await apiFetch<FailureReport>(`/api/job-targets/${jobTargetId}/failure-report`);
  } catch (err: unknown) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

export async function fetchFailureAnalytics(): Promise<FailureAnalytics> {
  return apiFetch<FailureAnalytics>("/api/recovery/failure-analytics");
}
