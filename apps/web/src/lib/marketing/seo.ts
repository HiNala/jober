/** Workspace and auth paths excluded from crawlers (not in sitemap). */
export const ROBOTS_DISALLOW_PATHS = [
  "/dashboard",
  "/queue",
  "/discover",
  "/search",
  "/analytics",
  "/settings",
  "/library",
  "/documents",
  "/vault",
  "/runs",
  "/admin",
  "/verify-email",
  "/reset-password",
  "/forgot-password",
  "/kitchen-sink",
] as const;
