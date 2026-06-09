import { ApiError, apiFetch } from "@/lib/api/client";

export interface ReadinessCheck {
  check_id: string;
  passed: boolean;
  reason: string;
  evidence?: Record<string, unknown> | null;
}

export interface ReadinessReport {
  passed: boolean;
  checks: ReadinessCheck[];
}

export interface FillDiffItem {
  field_key: string;
  label: string | null;
  proposed_redacted?: string | null;
  actual_redacted?: string | null;
  matched?: boolean | null;
  locator_strategy?: string | null;
}

export interface ReviewPackage {
  run_id: string;
  job_target_id: string;
  company: string;
  role: string;
  status: string;
  human_summary: string;
  readiness: ReadinessReport;
  fill_diffs: FillDiffItem[];
  screenshot_object_key?: string | null;
  resume_filename?: string | null;
  cover_letter_preview?: string | null;
  cover_letter?: {
    id: string;
    text: string;
    ats_score: number | null;
    keyword_coverage?: {
      present?: string[];
      missing?: string[];
      template_style?: string;
      voice_preset?: string;
    };
    template_style?: string;
    voice_preset?: string;
    locked_paragraphs?: number[];
    pdf_download_path?: string;
  } | null;
  checkpoint_id?: string | null;
  policy: string;
}

export interface SubmitResult {
  run_id: string;
  outcome: string;
  confirmation_text?: string | null;
  final_url?: string | null;
  note?: string | null;
  job_target_status?: string | null;
}

export async function fetchReviewPackage(jobTargetId: string): Promise<ReviewPackage | null> {
  try {
    return await apiFetch<ReviewPackage>(`/api/job-targets/${jobTargetId}/review`);
  } catch (err: unknown) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

export async function fetchReviewPackageByRun(runId: string): Promise<ReviewPackage | null> {
  try {
    return await apiFetch<ReviewPackage>(`/api/application-runs/${runId}/review`);
  } catch (err: unknown) {
    if (err instanceof ApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

export async function submitApplicationRun(
  runId: string,
  fixtureHtml?: string,
): Promise<SubmitResult> {
  return apiFetch<SubmitResult>(`/api/application-runs/${runId}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fixtureHtml ? { fixture_html: fixtureHtml } : {}),
  });
}

export async function skipApplicationSubmit(runId: string): Promise<{ run_id: string; status: string }> {
  return apiFetch(`/api/application-runs/${runId}/skip-submit`, { method: "POST" });
}
