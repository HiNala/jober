import Link from "next/link";
import { FileSpreadsheet, Play, Upload } from "lucide-react";

import { AmbientCanvas } from "@/components/design-system/ambient-canvas";
import { SuggestionChips } from "@/components/design-system/suggestion-chips";
import { buttonVariants } from "@/components/ui/button";
import { DemoWorkspaceButton } from "@/components/onboarding/demo-workspace-button";
import { DASHBOARD_FIRST_RUN } from "@/lib/states/onboarding-copy";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const STEPS = [
  {
    step: "1",
    title: "Import your job tracker",
    body: "Upload your spreadsheet on the queue page. Jober maps companies, roles, and ATS URLs.",
    href: "/queue",
    cta: "Open queue",
    icon: FileSpreadsheet,
  },
  {
    step: "2",
    title: "Upload your resume",
    body: "Add a canonical resume in Vault so cover letters stay grounded in your real experience.",
    href: "/vault",
    cta: "Open vault",
    icon: Upload,
  },
  {
    step: "3",
    title: "Run a dry-run batch",
    body: "Launch a dry-run from the dashboard to watch Jober fill applications while you review every step.",
    href: "/queue",
    cta: "View queue",
    icon: Play,
  },
] as const;

const FIRST_RUN_CHIPS = [
  { id: "import", label: "Import tracker", href: "/queue" },
  { id: "discover", label: "Discover jobs", href: "/discover" },
  { id: "vault", label: "Open vault", href: "/vault" },
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
          <Link href="/queue" className={buttonVariants({ size: "sm" })}>
            Import spreadsheet
          </Link>
          <Link href="/discover" className={buttonVariants({ variant: "outline", size: "sm" })}>
            Discover jobs
          </Link>
          <DemoWorkspaceButton />
        </div>
      </div>

      <ol className="relative grid gap-4 sm:grid-cols-3">
        {STEPS.map(({ step, title, body, href, cta, icon: Icon }) => (
          <li
            key={step}
            className={cn(
              surface.workspace,
              "group relative flex flex-col overflow-hidden p-5 transition-shadow hover:shadow-md",
            )}
          >
            <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-primary/60 via-primary/30 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            <div className="flex items-center gap-3">
              <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 text-sm font-bold text-primary ring-1 ring-primary/20">
                {step}
              </div>
              <Icon className="size-4 text-muted-foreground" aria-hidden />
            </div>
            <h3 className="mt-4 font-semibold leading-snug">{title}</h3>
            <p className="mt-2 flex-1 text-sm leading-relaxed text-muted-foreground">{body}</p>
            <Link
              href={href}
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "mt-5 w-full justify-center",
              )}
            >
              {cta}
            </Link>
          </li>
        ))}
      </ol>
    </div>
  );
}
