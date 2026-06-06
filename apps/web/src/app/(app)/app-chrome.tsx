"use client";

import { usePathname } from "next/navigation";

import { AppShell } from "@/components/app-shell/app-shell";

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/queue": "Queue",
  "/documents": "Documents",
  "/vault": "Vault",
  "/settings": "Settings",
};

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const title = TITLES[pathname] ?? "Jober";

  return <AppShell title={title}>{children}</AppShell>;
}
