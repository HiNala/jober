import type { ImportReportRead, JobTargetRead, JobTargetStatus } from "@jober/schemas";

import { apiFetch, uploadFetch, getApiBaseUrl } from "@/lib/api/client";

export interface JobTargetFilters {
  status?: JobTargetStatus;
  priority?: string;
  company?: string;
  role?: string;
  location?: string;
  ats_guess?: string;
}

export async function fetchJobTargets(
  filters: JobTargetFilters = {},
): Promise<JobTargetRead[]> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value);
  }
  const qs = params.toString();
  const data = await apiFetch<{ items: JobTargetRead[] }>(
    `/api/job-targets${qs ? `?${qs}` : ""}`,
  );
  return data.items;
}

export async function updateJobTarget(
  id: string,
  patch: Partial<
    Pick<JobTargetRead, "status" | "applied_date" | "follow_up_date" | "notes" | "priority">
  >,
): Promise<JobTargetRead> {
  return apiFetch<JobTargetRead>(`/api/job-targets/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
}

export async function previewJobsImport(file: File): Promise<ImportReportRead> {
  const form = new FormData();
  form.append("file", file);
  const res = await uploadFetch("/api/imports/jobs-xlsx?dry_run=true", form);
  if (!res.ok) {
    throw new Error(`Import preview failed (${res.status})`);
  }
  return res.json() as Promise<ImportReportRead>;
}

export async function commitJobsImport(file: File): Promise<ImportReportRead> {
  const form = new FormData();
  form.append("file", file);
  const res = await uploadFetch("/api/imports/jobs-xlsx", form);
  if (!res.ok) {
    throw new Error(`Import failed (${res.status})`);
  }
  return res.json() as Promise<ImportReportRead>;
}

export function exportJobsXlsxUrl(): string {
  return `${getApiBaseUrl()}/api/exports/jobs-xlsx`;
}
