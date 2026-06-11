/** In-app layout modes — Mission 09 workspace discipline. */
export type WorkspaceLayoutMode = "ops-desk" | "editorial";

const OPS_DESK_PREFIX = "/runs/";

/** Explicit per-route layout declaration consumed by `app-chrome.tsx`. */
export function layoutModeForPath(pathname: string): WorkspaceLayoutMode {
  if (pathname.startsWith(OPS_DESK_PREFIX)) {
    return "ops-desk";
  }
  return "editorial";
}

export function isOpsDeskPath(pathname: string): boolean {
  return layoutModeForPath(pathname) === "ops-desk";
}
