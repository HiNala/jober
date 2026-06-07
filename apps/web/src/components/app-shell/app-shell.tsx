import { WorkspaceShell } from "@/components/workspace/workspace-shell";

export function AppShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return <WorkspaceShell title={title}>{children}</WorkspaceShell>;
}
