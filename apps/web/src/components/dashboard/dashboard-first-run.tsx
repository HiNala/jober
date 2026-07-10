import Link from "next/link";

import { AmbientCanvas } from "@/components/design-system/ambient-canvas";
import { SuggestionChips } from "@/components/design-system/suggestion-chips";
import { buttonVariants } from "@/components/ui/button";
import { DemoWorkspaceButton } from "@/components/onboarding/demo-workspace-button";
import { DASHBOARD_FIRST_RUN } from "@/lib/states/onboarding-copy";

const FIRST_RUN_CHIPS = [
  { id: "import", label: "Import tracker", href: "/queue?import=1" },
  { id: "discover", label: "Discover jobs", href: "/discover" },
  { id: "vault", label: "Open vault", href: "/vault" },
  { id: "docs", label: "Document studio", href: "/documents" },
] as const;

export function DashboardFirstRun() {
  return (
    <div className="relative mx-auto max-w-3xl space-y-10">
      {/* Hyperagent / Grok empty power moment */}
      <AmbientCanvas
        className="pointer-events-none absolute inset-x-0 -top-8 h-64 rounded-3xl opacity-70"
        drift
      />
      <div className="relative space-y-4 text-center">
        <p className="font-mono text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-muted-foreground">
          Command center
        </p>
        <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl sm:tracking-[-0.02em]">
          {DASHBOARD_FIRST_RUN.title}
        </h2>
        <p className="mx-auto max-w-md text-sm text-muted-foreground sm:text-base">
          {DASHBOARD_FIRST_RUN.description}
        </p>
        <SuggestionChips className="pt-1" label="Get started" chips={[...FIRST_RUN_CHIPS]} />
        <div className="flex flex-wrap justify-center gap-3 pt-1">
          <Link href="/queue?import=1" className={buttonVariants({ size: "sm" })}>
            Import spreadsheet
          </Link>
          <Link href="/discover" className={buttonVariants({ variant: "outline", size: "sm" })}>
            Discover jobs
          </Link>
          <DemoWorkspaceButton />
        </div>
        <p className="pt-2 text-xs text-muted-foreground">
          Follow the guided checklist below — it tracks live progress as you go.
        </p>
      </div>
    </div>
  );
}
