"use client";

import { usePathname } from "next/navigation";

import { AppShell } from "@/components/app-shell/app-shell";
import { RunCanvasProvider } from "@/contexts/run-canvas-context";

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/queue": "Queue",
  "/discover": "Discover",
  "/library": "Library",
  "/search": "Search",
  "/analytics": "Analytics",
  "/settings": "Settings",
};

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  let title = TITLES[pathname] ?? "Jober";
  if (pathname.startsWith("/runs/")) {
    title = "Run console";
  }

  return (
    <RunCanvasProvider>
      <AppShell title={title}>{children}</AppShell>
    </RunCanvasProvider>
  );
}
