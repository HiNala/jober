import { ApiError } from "@/lib/api/client";

function detailMessage(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }
  if (detail && typeof detail === "object") {
    const obj = detail as { message?: string; unsupported?: string[] };
    if (obj.message && obj.unsupported?.length) {
      return `${obj.message}: ${obj.unsupported.join(", ")}`;
    }
    if (obj.message) {
      return obj.message;
    }
  }
  return null;
}

/** Turn API failures into user-facing toast copy (budget cap, claims guard, missing resume). */
export function formatApiError(err: unknown, fallback = "Something went wrong"): string {
  if (!(err instanceof ApiError)) {
    return err instanceof Error ? err.message : fallback;
  }

  if (err.body) {
    try {
      const parsed = JSON.parse(err.body) as { detail?: unknown };
      const message = detailMessage(parsed.detail);
      if (message) {
        return message;
      }
    } catch {
      // Fall through to status-based defaults.
    }
  }

  if (err.status === 402) {
    return "LLM monthly budget exceeded. Generation blocked until next month or budget is raised.";
  }
  if (err.status === 422) {
    return "Could not generate letter. Upload a resume in Vault or regenerate with supported claims.";
  }

  return err.message;
}
