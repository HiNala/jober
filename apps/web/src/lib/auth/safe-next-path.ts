/**
 * Allow only same-origin relative paths for post-login redirects.
 * Blocks open redirects (//evil.com, https://…).
 */
export function safeNextPath(raw: string | null | undefined, fallback = "/dashboard"): string {
  if (!raw) return fallback;
  const path = raw.trim();
  if (!path.startsWith("/")) return fallback;
  if (path.startsWith("//")) return fallback;
  if (path.includes("://")) return fallback;
  if (path.startsWith("/login") || path.startsWith("/signup")) return fallback;
  return path;
}
