"use client";

import Link from "next/link";
import { FileSpreadsheet, Play, Upload } from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
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

export function DashboardFirstRun() {
  return (
    <div className="mx-auto max-w-3xl space-y-10">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-semibold tracking-tight">{DASHBOARD_FIRST_RUN.title}</h2>
        <p className="mx-auto max-w-md text-sm text-muted-foreground">
          {DASHBOARD_FIRST_RUN.description}
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <Link href="/queue" className={buttonVariants({ size: "sm" })}>
            Import spreadsheet
          </Link>
          <Link href="/vault" className={buttonVariants({ variant: "outline", size: "sm" })}>
            Upload resume
          </Link>
        </div>
      </div>

      <ol className="grid gap-4 sm:grid-cols-3">
        {STEPS.map(({ step, title, body, href, cta, icon: Icon }) => (
          <li key={step} className={cn(surface.workspace, "relative flex flex-col rounded-xl p-5")}>
            <div className="flex items-center gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
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
