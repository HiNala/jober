import { WorkerHealthPill } from "@/components/app-shell/worker-health-pill";

export function AppTopbar({ title }: { title: string }) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b px-4 md:px-6">
      <h1 className="text-lg font-medium tracking-tight">{title}</h1>
      <WorkerHealthPill />
    </header>
  );
}
