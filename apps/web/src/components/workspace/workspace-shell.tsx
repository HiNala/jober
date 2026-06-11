"use client";

import { usePathname } from "next/navigation";
import { useSyncExternalStore } from "react";

import { WorkspaceCommandPalette } from "@/components/workspace/workspace-command-palette";
import { useWorkspaceKeyboard } from "@/components/workspace/workspace-keyboard";
import { WorkspaceShellPanels } from "@/components/workspace/workspace-shell-panels";
import type { WorkspaceLayoutMode } from "@/lib/workspace/layout";

export function WorkspaceShell({
  title,
  layoutMode,
  children,
}: {
  title: string;
  layoutMode: WorkspaceLayoutMode;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );

  useWorkspaceKeyboard(pathname);

  if (!mounted) {
    return (
      <div className="flex h-screen flex-col overflow-hidden bg-background">
        <main id="main-content" tabIndex={-1} className="min-h-0 flex-1 overflow-auto">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>
      <WorkspaceShellPanels title={title} layoutMode={layoutMode}>
        {children}
      </WorkspaceShellPanels>
      <WorkspaceCommandPalette />
    </div>
  );
}
