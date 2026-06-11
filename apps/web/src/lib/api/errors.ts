import { ApiError } from "@/lib/api/client";
import { formatMappedErrors, mapApiErrors } from "@/lib/forms/map-api-errors";

/** Turn API failures into user-facing toast or form copy. */
export function formatApiError(err: unknown, fallback = "Something went wrong"): string {
  if (!(err instanceof ApiError)) {
    return err instanceof Error && err.message ? err.message : fallback;
  }
  return formatMappedErrors(mapApiErrors(err, fallback), fallback);
}
