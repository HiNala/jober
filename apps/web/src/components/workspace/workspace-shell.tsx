"use client";

import { useSyncExternalStore } from "react";

import { WorkspaceCenterHeader } from "@/components/workspace/workspace-center-header";
import { WorkspaceCommandBar } from "@/components/workspace/workspace-command-bar";
import { useWorkspaceKeyboard } from "@/components/workspace/workspace-keyboard";
import { WorkspaceShellPanels } from "@/components/workspace/workspace-shell-panels";

export function WorkspaceShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );

  useWorkspaceKeyboard();

  if (!mounted) {
    return (
      <div className="flex h-screen flex-col overflow-hidden bg-background">
        <WorkspaceCenterHeader title={title} />
        <main id="main-content" tabIndex={-1} className="min-h-0 flex-1 overflow-auto">
          {children}
        </main>
        <WorkspaceCommandBar />
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
      <WorkspaceShellPanels title={title}>{children}</WorkspaceShellPanels>
    </div>
  );
}
