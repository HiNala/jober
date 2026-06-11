import { formatMappedErrors, mapApiErrors } from "@/lib/forms/map-api-errors";

/** Map API auth errors to user-safe messages (no raw JSON bodies). */
export function parseAuthError(err: unknown, fallback: string): string {
  return formatMappedErrors(mapApiErrors(err, fallback), fallback);
}
