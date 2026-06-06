import { MobileNav } from "@/components/app-shell/mobile-nav";
import { WorkerHealthPill } from "@/components/app-shell/worker-health-pill";

export function AppTopbar({ title }: { title: string }) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b px-4 md:px-6">
      <div className="flex min-w-0 items-center gap-2">
        <MobileNav />
        <h1 className="truncate text-lg font-medium tracking-tight">{title}</h1>
      </div>
      <WorkerHealthPill />
    </header>
  );
}
