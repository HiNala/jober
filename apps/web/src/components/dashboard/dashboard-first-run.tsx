"use client";

import Link from "next/link";
import { FileSpreadsheet, Play, Upload } from "lucide-react";

import { PageEmpty } from "@/components/states/page-states";
import { buttonVariants } from "@/components/ui/button";
import { DASHBOARD_FIRST_RUN } from "@/lib/states/onboarding-copy";
import { cn } from "@/lib/utils";
import { surface } from "@/lib/design/tokens";

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
    <div className="space-y-8">
      <PageEmpty
        title={DASHBOARD_FIRST_RUN.title}
        description={DASHBOARD_FIRST_RUN.description}
        action={
          <Link href="/queue" className={buttonVariants({ size: "sm" })}>
            Import spreadsheet
          </Link>
        }
        secondaryAction={
          <Link href="/vault" className={buttonVariants({ variant: "outline", size: "sm" })}>
            Upload resume
          </Link>
        }
      />
      <ol className="mx-auto grid max-w-3xl gap-4 sm:grid-cols-3">
        {STEPS.map(({ step, title, body, href, cta, icon: Icon }) => (
          <li key={step} className={cn(surface.card, "rounded-xl p-4")}>
            <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
              <span className="flex size-6 items-center justify-center rounded-full bg-muted font-mono">
                {step}
              </span>
              <Icon className="size-4" aria-hidden />
            </div>
            <h3 className="mt-3 text-sm font-medium">{title}</h3>
            <p className="mt-1 text-xs text-muted-foreground">{body}</p>
            <Link
              href={href}
              className={cn(buttonVariants({ variant: "link", size: "sm" }), "mt-3 h-auto p-0")}
            >
              {cta} →
            </Link>
          </li>
        ))}
      </ol>
    </div>
  );
}
