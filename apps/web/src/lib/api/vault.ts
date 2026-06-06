import { apiFetch, getApiBaseUrl } from "@/lib/api/client";

export interface FieldConsent {
  consent: boolean;
  never_autofill: boolean;
  consented_at?: string | null;
}

export interface VaultField {
  key: string;
  label: string;
  tier: "public" | "preference" | "sensitive";
  value?: string | boolean | Record<string, unknown> | null;
  has_value?: boolean;
  consent: FieldConsent;
}

export interface ChecklistItem {
  key: string;
  label: string;
  tier: string;
  filled: boolean;
  required: boolean;
}

export interface ResumeAssetRead {
  id: string;
  original_filename: string;
  is_active: boolean;
  skills: string[];
  extracted_text_preview: string;
  has_text: boolean;
}

export interface ProfileVaultRead {
  id: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  current_title?: string | null;
  notice_period?: string | null;
  links?: Record<string, string> | null;
  relocation_pref?: boolean | null;
  onsite_pref?: boolean | null;
  hybrid_pref?: boolean | null;
  salary_prefs?: Record<string, unknown> | null;
  profile_completeness_score?: number | null;
  checklist: ChecklistItem[];
  fields: VaultField[];
  active_resume?: ResumeAssetRead | null;
}

export interface CommonAnswer {
  id: string;
  answer_key: string;
  label: string;
  body: string;
}

export async function fetchProfile(): Promise<ProfileVaultRead> {
  return apiFetch<ProfileVaultRead>("/api/profile");
}

export async function patchProfile(
  patch: Record<string, unknown>,
): Promise<ProfileVaultRead> {
  return apiFetch<ProfileVaultRead>("/api/profile", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
}

export async function patchVault(
  patch: Record<string, unknown>,
): Promise<ProfileVaultRead> {
  return apiFetch<ProfileVaultRead>("/api/profile/vault", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
}

export async function fetchCommonAnswers(): Promise<CommonAnswer[]> {
  const data = await apiFetch<{ items: CommonAnswer[] }>("/api/profile/common-answers");
  return data.items;
}

export async function saveCommonAnswer(
  answerKey: string,
  body: string,
  label?: string,
): Promise<CommonAnswer> {
  return apiFetch<CommonAnswer>(`/api/profile/common-answers/${answerKey}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body, label }),
  });
}

export async function uploadResume(file: File): Promise<ResumeAssetRead> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${getApiBaseUrl()}/api/resumes`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Upload failed (${res.status})`);
  }
  return res.json() as Promise<ResumeAssetRead>;
}
