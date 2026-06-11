import { ApiError } from "@/lib/api/client";

export type ApiFieldErrors = Record<string, string>;

export type MappedApiErrors = {
  formError: string | null;
  fieldErrors: ApiFieldErrors;
};

type PydanticErrorItem = {
  loc?: (string | number)[];
  msg?: string;
};

type ApiErrorBody = {
  detail?: unknown;
  code?: string;
  correlation_id?: string;
};

function parseJsonBody(raw: string): ApiErrorBody | null {
  try {
    return JSON.parse(raw) as ApiErrorBody;
  } catch {
    return null;
  }
}

/** Map FastAPI/Pydantic `loc` to a flat field key (drops body/query prefixes). */
export function locToFieldPath(loc: (string | number)[]): string | null {
  const parts = loc.filter(
    (segment) => segment !== "body" && segment !== "query" && typeof segment === "string",
  );
  if (parts.length === 0) return null;
  return parts.join(".");
}

function mapDetail(detail: unknown, fallback: string): MappedApiErrors {
  if (typeof detail === "string" && detail.trim()) {
    return { formError: detail.trim(), fieldErrors: {} };
  }

  if (Array.isArray(detail)) {
    const fieldErrors: ApiFieldErrors = {};
    const formMessages: string[] = [];

    for (const item of detail) {
      if (!item || typeof item !== "object") continue;
      const row = item as PydanticErrorItem;
      const message = typeof row.msg === "string" ? row.msg.trim() : "";
      if (!message) continue;
      const path = Array.isArray(row.loc) ? locToFieldPath(row.loc) : null;
      if (path) {
        fieldErrors[path] = fieldErrors[path] ? `${fieldErrors[path]} ${message}` : message;
      } else {
        formMessages.push(message);
      }
    }

    if (Object.keys(fieldErrors).length > 0) {
      return {
        formError: formMessages[0] ?? null,
        fieldErrors,
      };
    }
    if (formMessages.length > 0) {
      return { formError: formMessages[0], fieldErrors: {} };
    }
  }

  if (detail && typeof detail === "object") {
    const obj = detail as { message?: string; code?: string };
    if (obj.code === "dependency_unavailable" && obj.message?.trim()) {
      return { formError: obj.message.trim(), fieldErrors: {} };
    }
    if (obj.message?.trim()) {
      return { formError: obj.message.trim(), fieldErrors: {} };
    }
  }

  return { formError: fallback, fieldErrors: {} };
}

export function extractApiBody(err: unknown): string | undefined {
  if (err instanceof ApiError) return err.body;
  if (err instanceof Error) {
    const raw = err.message.trim();
    if (raw.startsWith("{")) return raw;
  }
  return undefined;
}

/** Normalize API failures into form-level and field-level messages. */
export function mapApiErrors(err: unknown, fallback = "Something went wrong"): MappedApiErrors {
  const body = extractApiBody(err);
  if (body) {
    const parsed = parseJsonBody(body);
    if (parsed) {
      return mapDetail(parsed.detail, fallback);
    }
  }

  if (err instanceof ApiError) {
    if (err.status === 402) {
      return {
        formError:
          "LLM monthly budget exceeded. Generation blocked until next month or budget is raised.",
        fieldErrors: {},
      };
    }
    if (err.status === 503) {
      const parsed = body ? parseJsonBody(body) : null;
      const detail = parsed?.detail;
      if (detail && typeof detail === "object") {
        const obj = detail as { message?: string };
        if (obj.message?.trim()) {
          return { formError: obj.message.trim(), fieldErrors: {} };
        }
      }
      return {
        formError: "A required service is temporarily unavailable. Try again shortly.",
        fieldErrors: {},
      };
    }
    if (err.message && !err.message.startsWith("API ")) {
      return { formError: err.message, fieldErrors: {} };
    }
  }

  if (err instanceof Error) {
    const raw = err.message.trim();
    if (raw.includes("Too many failed")) {
      return { formError: "Too many failed attempts. Try again later.", fieldErrors: {} };
    }
    if (raw.includes("Account locked")) {
      return {
        formError: "Account locked after too many attempts. Contact support.",
        fieldErrors: {},
      };
    }
  }

  return { formError: fallback, fieldErrors: {} };
}

export function remapFieldErrors(
  fieldErrors: ApiFieldErrors,
  aliases: Record<string, string>,
): ApiFieldErrors {
  const next: ApiFieldErrors = { ...fieldErrors };
  for (const [from, to] of Object.entries(aliases)) {
    if (from in next && !(to in next)) {
      next[to] = next[from];
      delete next[from];
    }
  }
  return next;
}

export function formatMappedErrors(mapped: MappedApiErrors, fallback: string): string {
  if (mapped.formError) return mapped.formError;
  const firstField = Object.values(mapped.fieldErrors)[0];
  return firstField ?? fallback;
}
