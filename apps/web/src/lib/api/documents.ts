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
  template_style?: string;
  voice_preset?: string;
  locked_paragraphs?: number[];
  version?: number;
  ab_tracking?: Record<string, string | null>;
}

export interface GeneratedDocumentRead {
  id: string;
  job_target_id: string;
  run_id?: string | null;
  document_type: string;
  text: string;
  keyword_coverage: KeywordCoverage;
  ats_score: number;
  generated_at: string | null;
  cached: boolean;
  template_style?: string;
  voice_preset?: string;
  locked_paragraphs?: number[];
  version?: number;
  pdf_download_path: string;
  docx_download_path: string | null;
}

export interface LetterOptions {
  templates: string[];
  voice_presets: string[];
}

export async function fetchJobsForStudio() {
  return fetchJobTargets();
}

export async function fetchLetterOptions(): Promise<LetterOptions> {
  return apiFetch<LetterOptions>("/api/documents/letter-options");
}

export async function generateCoverLetter(
  jobTargetId: string,
  options: {
    force?: boolean;
    includeDocx?: boolean;
    templateStyle?: string;
    voicePreset?: string;
    runId?: string;
    lockedParagraphs?: number[];
    regenerateParagraphIndex?: number;
    seedText?: string;
    parentDocumentId?: string;
  } = {},
): Promise<GeneratedDocumentRead> {
  return apiFetch<GeneratedDocumentRead>("/api/documents/generate-cover-letter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_target_id: jobTargetId,
      force: options.force ?? false,
      include_docx: options.includeDocx ?? true,
      template_style: options.templateStyle,
      voice_preset: options.voicePreset,
      run_id: options.runId,
      locked_paragraphs: options.lockedParagraphs,
      regenerate_paragraph_index: options.regenerateParagraphIndex,
      seed_text: options.seedText,
      parent_document_id: options.parentDocumentId,
    }),
  });
}

/** Tailored resume draft for a job target (never fabricates employers/degrees). */
export async function generateResumeVariant(
  jobTargetId: string,
  options: { force?: boolean; runId?: string } = {},
): Promise<GeneratedDocumentRead> {
  return apiFetch<GeneratedDocumentRead>("/api/documents/generate-resume-variant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      job_target_id: jobTargetId,
      force: options.force ?? false,
      run_id: options.runId,
    }),
  });
}

export async function patchCoverLetter(
  documentId: string,
  body: {
    text?: string;
    locked_paragraphs?: number[];
    locked_template?: boolean;
    template_style?: string;
    voice_preset?: string;
  },
): Promise<GeneratedDocumentRead> {
  return apiFetch<GeneratedDocumentRead>(`/api/documents/${documentId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function duplicateCoverLetter(
  documentId: string,
  jobTargetId?: string,
): Promise<GeneratedDocumentRead> {
  return apiFetch<GeneratedDocumentRead>(`/api/documents/${documentId}/duplicate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(jobTargetId ? { job_target_id: jobTargetId } : {}),
  });
}

export function documentDownloadUrl(path: string): string {
  return `${getApiBaseUrl()}${path}`;
}
