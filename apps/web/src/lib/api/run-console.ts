import { apiFetch } from "@/lib/api/client";

export interface RunStreamEvent {
  id: string;
  seq: number;
  ts: string;
  level: string;
  event_type: string;
  message: string;
  payload?: Record<string, unknown>;
  screenshot_key?: string | null;
  screenshot_url?: string | null;
  attempt_index?: number | null;
}

export interface RunConsoleSnapshot {
  run_id: string;
  job_target_id: string;
  company: string;
  role: string;
  status: string;
  current_step: string | null;
  attempt_count: number;
  latest_screenshot_url: string | null;
  latest_screenshot_key: string | null;
  open_checkpoint: {
    id: string;
    checkpoint_type: string;
    prompt: string;
    options?: Record<string, unknown>;
  } | null;
  timeline: Array<{
    seq: number;
    ts: string;
    status?: string;
    step?: string;
    screenshot_key?: string | null;
    screenshot_url?: string | null;
  }>;
  artifacts: Array<{
    attempt_index: number;
    trace_url?: string | null;
    video_url?: string | null;
    screenshot_url?: string | null;
    dom_url?: string | null;
  }>;
  last_event_seq: number;
  events: RunStreamEvent[];
}

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export function runEventsStreamUrl(runId: string, afterSeq = 0): string {
  const base = getApiBaseUrl();
  const suffix = afterSeq > 0 ? `?after_seq=${afterSeq}` : "";
  return `${base}/api/application-runs/${runId}/events${suffix}`;
}

export async function fetchRunConsoleSnapshot(runId: string): Promise<RunConsoleSnapshot> {
  return apiFetch<RunConsoleSnapshot>(`/api/application-runs/${runId}/console`);
}

export async function resolveRunCheckpoint(
  runId: string,
  checkpointId: string,
  action: "approve" | "deny" | "edit" | "skip",
  value?: string,
): Promise<{ checkpoint_id: string; status: string; run_status: string; action: string }> {
  return apiFetch(`/api/application-runs/${runId}/checkpoints/${checkpointId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, value }),
  });
}
