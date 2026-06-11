import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import type { WorkspaceLayoutMode } from "@/lib/workspace/layout";

export function AppShell({
  title,
  layoutMode,
  children,
}: {
  title: string;
  layoutMode: WorkspaceLayoutMode;
  children: React.ReactNode;
}) {
  return (
    <WorkspaceShell title={title} layoutMode={layoutMode}>
      {children}
    </WorkspaceShell>
  );
}
