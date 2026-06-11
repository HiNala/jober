import type { FileUploadKind } from "@/components/import/file-upload";

export const SPREADSHEET_EXTENSIONS = [".xlsx", ".xls"] as const;
export const RESUME_EXTENSIONS = [".pdf", ".docx"] as const;

/** Client-side guardrails — server remains authoritative. */
export const MAX_SPREADSHEET_BYTES = 20 * 1024 * 1024;
export const MAX_RESUME_BYTES = 10 * 1024 * 1024;

function extensionOf(filename: string): string {
  const lower = filename.toLowerCase();
  const dot = lower.lastIndexOf(".");
  return dot >= 0 ? lower.slice(dot) : "";
}

function formatMegabytes(bytes: number): string {
  return `${Math.round(bytes / (1024 * 1024))} MB`;
}

export function validateUploadFile(file: File, kind: FileUploadKind): string | null {
  const ext = extensionOf(file.name);
  if (kind === "spreadsheet") {
    if (!SPREADSHEET_EXTENSIONS.includes(ext as (typeof SPREADSHEET_EXTENSIONS)[number])) {
      return "Choose an Excel workbook (.xlsx or .xls)";
    }
    if (file.size > MAX_SPREADSHEET_BYTES) {
      return `Workbook must be under ${formatMegabytes(MAX_SPREADSHEET_BYTES)}`;
    }
    return null;
  }

  if (!RESUME_EXTENSIONS.includes(ext as (typeof RESUME_EXTENSIONS)[number])) {
    return "Only PDF and DOCX resumes are supported";
  }
  if (file.size > MAX_RESUME_BYTES) {
    return `Resume must be under ${formatMegabytes(MAX_RESUME_BYTES)}`;
  }
  return null;
}
