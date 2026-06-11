/** Map errors to user-safe messages (no stack traces or raw API payloads). */
export function friendlyPageError(error: Error): string {
  if (error.name === "AbortError") {
    return "Request was cancelled. Please try again.";
  }
  return "Something went wrong loading this page. Please try again.";
}
