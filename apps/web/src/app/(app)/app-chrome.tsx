"use client";

import { usePathname } from "next/navigation";

import { AppShell } from "@/components/app-shell/app-shell";
import { AppNotifications } from "@/components/notifications/app-notifications";
import { ConsentSheet } from "@/components/product/consent-sheet";
import { RunCanvasProvider } from "@/contexts/run-canvas-context";
import { layoutModeForPath } from "@/lib/workspace/layout";

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/queue": "Queue",
  "/discover": "Discover",
  "/documents": "Documents",
  "/library": "Library",
  "/vault": "Vault",
  "/search": "Search",
  "/analytics": "Analytics",
  "/admin": "Admin",
  "/admin/users": "Admin users",
  "/admin/runs": "Admin runs",
  "/admin/cost": "Admin cost",
  "/admin/system": "Admin system",
  "/admin/acquisition": "Admin acquisition",
  "/admin/config": "Admin config",
  "/settings": "Settings",
};

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const layoutMode = layoutModeForPath(pathname);
  let title = TITLES[pathname] ?? "Jober";
  if (pathname.startsWith("/runs/")) {
    title = "Run console";
  } else if (pathname.startsWith("/admin/") && !TITLES[pathname]) {
    title = "Admin";
  }

  return (
    <RunCanvasProvider>
      <AppShell title={title} layoutMode={layoutMode}>
        {children}
      </AppShell>
      <AppNotifications />
      <ConsentSheet key={pathname} />
    </RunCanvasProvider>
  );
}
