import { apiFetch, getApiBaseUrl } from "@/lib/api/client";
import { fetchJobTargets } from "@/lib/api/jobs";

export interface ParagraphGrounding {
  paragraph_index: number;
  resume_facts: string[];
  job_keywords: string[];
}

export interface KeywordCoverage {
  present: string[];
  missing: string[];
  density: number;
  stuffing_penalty: number;
  resume_variant?: string;
  asserted_facts?: string[];
  paragraph_grounding?: ParagraphGrounding[];
  explain?: ParagraphGrounding[];
}

export interface GeneratedDocumentRead {
  id: string;
  job_target_id: string;
  document_type: string;
  text: string;
  keyword_coverage: KeywordCoverage;
  ats_score: number;
  generated_at: string | null;
  cached: boolean;
  pdf_download_path: string;
  docx_download_path: string | null;
}

export async function fetchJobsForStudio() {
  return fetchJobTargets();
}

export async function generateCoverLetter(
  jobTargetId: string,
  options: { force?: boolean; includeDocx?: boolean } = {},
): Promise<GeneratedDocumentRead> {
  return apiFetch<GeneratedDocumentRead>("/api/documents/generate-cover-letter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_target_id: jobTargetId,
      force: options.force ?? false,
      include_docx: options.includeDocx ?? true,
    }),
  });
}

export function documentDownloadUrl(path: string): string {
  return `${getApiBaseUrl()}${path}`;
}
