/** Map API auth errors to user-safe messages (no raw JSON bodies). */
export function parseAuthError(err: unknown, fallback: string): string {
  if (!(err instanceof Error)) return fallback;

  const raw = err.message.trim();
  if (!raw) return fallback;

  try {
    const parsed = JSON.parse(raw) as { detail?: string | { msg?: string }[] };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (Array.isArray(parsed.detail) && parsed.detail[0]?.msg) {
      return parsed.detail[0].msg;
    }
  } catch {
    // plain text body
  }

  if (raw.includes("Too many failed")) {
    return "Too many failed attempts. Try again later.";
  }
  if (raw.includes("Account locked")) {
    return "Account locked after too many attempts. Contact support.";
  }

  return fallback;
}
