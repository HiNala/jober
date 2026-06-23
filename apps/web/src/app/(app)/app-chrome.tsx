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
  "/library": "Library",
  "/search": "Search",
  "/analytics": "Analytics",
  "/admin/users": "Admin users",
  "/settings": "Settings",
};

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const layoutMode = layoutModeForPath(pathname);
  let title = TITLES[pathname] ?? "Jober";
  if (pathname.startsWith("/runs/")) {
    title = "Run console";
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
