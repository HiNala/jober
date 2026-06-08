import { apiFetch, getApiBaseUrl } from "@/lib/api/client";
import type { ResumeAssetRead } from "@/lib/api/vault";

export type CoverLetterItem = {
  id: string;
  job_target_id: string;
  company: string;
  role: string;
  ats_score: number | null;
  generated_at: string | null;
  preview: string;
  is_template: boolean;
};

export type LibraryRunItem = {
  id: string;
  job_target_id: string;
  company: string;
  role: string;
  status: string;
  policy: string;
  updated_at: string;
  created_at: string;
};

export type JobListItem = {
  id: string;
  name: string;
  description: string | null;
  archived: boolean;
  items: {
    id: string;
    job_target_id: string;
    sort_order: number;
    company: string | null;
    role: string | null;
    status: string | null;
  }[];
};

export type LibrarySearchResults = {
  jobs: { id: string; company: string; role: string; status: string }[];
  cover_letters: CoverLetterItem[];
  runs: LibraryRunItem[];
  lists: { id: string; name: string }[];
};

export function fetchLibraryResumes() {
  return apiFetch<{ items: ResumeAssetRead[] }>("/api/library/resumes");
}

export function fetchLibraryCoverLetters(q?: string) {
  const params = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiFetch<{ items: CoverLetterItem[] }>(`/api/library/cover-letters${params}`);
}

export function fetchLibraryRuns() {
  return apiFetch<{ items: LibraryRunItem[] }>("/api/library/runs");
}

export function fetchJobLists(includeArchived = false) {
  const params = includeArchived ? "?include_archived=true" : "";
  return apiFetch<{ items: JobListItem[] }>(`/api/job-lists${params}`);
}

export function createJobList(name: string, description?: string) {
  return apiFetch<JobListItem>("/api/job-lists", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });
}

export function updateJobList(
  listId: string,
  patch: { name?: string; description?: string; archived?: boolean },
) {
  return apiFetch<JobListItem>(`/api/job-lists/${listId}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function reorderJobList(listId: string, itemIds: string[]) {
  return apiFetch<JobListItem>(`/api/job-lists/${listId}/reorder`, {
    method: "POST",
    body: JSON.stringify({ item_ids: itemIds }),
  });
}

export function searchLibrary(q: string) {
  return apiFetch<LibrarySearchResults>(
    `/api/library/search?q=${encodeURIComponent(q)}`,
  );
}

export function activateResume(resumeId: string) {
  return apiFetch<ResumeAssetRead>(`/api/resumes/${resumeId}/activate`, { method: "POST" });
}

export function lockCoverLetterTemplate(documentId: string, locked: boolean) {
  return apiFetch<{ id: string; locked_template: boolean }>(`/api/documents/${documentId}`, {
    method: "PATCH",
    body: JSON.stringify({ locked_template: locked }),
  });
}

export function coverLetterPdfUrl(documentId: string) {
  return `${getApiBaseUrl()}/api/documents/${documentId}/download/pdf`;
}

export async function uploadResumeFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${getApiBaseUrl()}/api/resumes`, {
    method: "POST",
    credentials: "include",
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<ResumeAssetRead>;
}
