"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  CheckCircle2,
  Circle,
  Compass,
  FileText,
  ListTodo,
  Play,
  Upload,
  X,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useSyncExternalStore } from "react";

import { DemoWorkspaceButton } from "@/components/onboarding/demo-workspace-button";
import { Button, buttonVariants } from "@/components/ui/button";
import { fetchDashboardSummary } from "@/lib/api/batches";
import { fetchJobTargets } from "@/lib/api/jobs";
import {
  fetchLibraryCoverLetters,
  fetchLibraryResumes,
  fetchLibraryRuns,
} from "@/lib/api/library";
import {
  FIRST_APPLY_STEPS,
  isWalkthroughHidden,
  isWalkthroughMarkedComplete,
  setWalkthroughDismissed,
  setWalkthroughMarkedComplete,
  stepIsDone,
  subscribeWalkthroughStorage,
  walkthroughStats,
  type WalkthroughProgress,
  type WalkthroughStepId,
} from "@/lib/onboarding/first-apply-walkthrough";
import { motionFadeIn, motionPress } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const STEP_ICONS: Record<WalkthroughStepId, typeof Compass> = {
  add_jobs: Compass,
  upload_resume: Upload,
  tailor_docs: FileText,
  dry_run: Play,
  review_approve: ListTodo,
};

type FirstApplyWalkthroughProps = {
  /** Compact strip vs full empty-state companion. */
  variant?: "card" | "embedded";
  className?: string;
  /** When true, ignore dismiss so empty dashboard always teaches. */
  forceShow?: boolean;
};

export function FirstApplyWalkthrough({
  variant = "card",
  className,
  forceShow = false,
}: FirstApplyWalkthroughProps) {
  const dismissed = useSyncExternalStore(
    subscribeWalkthroughStorage,
    isWalkthroughHidden,
    () => false,
  );

  const jobsQuery = useQuery({
    queryKey: ["job-targets"],
    queryFn: () => fetchJobTargets(),
    staleTime: 15_000,
  });
  const resumesQuery = useQuery({
    queryKey: ["library", "resumes"],
    queryFn: async () => (await fetchLibraryResumes()).items,
    staleTime: 15_000,
  });
  const docsQuery = useQuery({
    queryKey: ["library", "cover-letters-walkthrough"],
    queryFn: async () => (await fetchLibraryCoverLetters()).items,
    staleTime: 15_000,
  });
  const summaryQuery = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary,
    staleTime: 15_000,
  });
  const runsQuery = useQuery({
    queryKey: ["library", "runs-walkthrough"],
    queryFn: async () => (await fetchLibraryRuns()).items,
    staleTime: 15_000,
  });

  const progress: WalkthroughProgress = useMemo(() => {
    const jobs = jobsQuery.data ?? [];
    const resumes = resumesQuery.data ?? [];
    const docs = docsQuery.data ?? [];
    const runs = runsQuery.data ?? [];
    const summary = summaryQuery.data;
    const needs = summary?.needs_review ?? 0;
    const finishedOk = runs.some((r) =>
      ["succeeded", "applied", "review_and_submit", "needs_human"].includes(r.status),
    );
    return {
      hasJobs: jobs.length > 0,
      hasResume: resumes.length > 0,
      hasDocuments: docs.length > 0,
      hasRuns: runs.length > 0 || (summary?.active_runs ?? 0) > 0,
      hasReviewOrSuccess: needs > 0 || finishedOk,
    };
  }, [
    jobsQuery.data,
    resumesQuery.data,
    docsQuery.data,
    runsQuery.data,
    summaryQuery.data,
  ]);

  const stats = walkthroughStats(progress);

  useEffect(() => {
    if (stats.allRequiredDone && !isWalkthroughMarkedComplete()) {
      setWalkthroughMarkedComplete(true);
    }
  }, [stats.allRequiredDone]);

  const dismiss = useCallback(() => {
    setWalkthroughDismissed(true);
  }, []);

  const restore = useCallback(() => {
    setWalkthroughDismissed(false);
    setWalkthroughMarkedComplete(false);
  }, []);

  if (!forceShow && dismissed && !stats.allRequiredDone) {
    // Collapsed teaser so power users can reopen
    if (variant === "card") {
      return (
        <div className={cn("flex justify-end", className)}>
          <Button type="button" variant="ghost" size="sm" className={motionPress} onClick={restore}>
            Show first-apply guide
          </Button>
        </div>
      );
    }
    return null;
  }
  if (!forceShow && dismissed && stats.allRequiredDone) return null;

  const pct = Math.round((stats.done / stats.total) * 100);
  const nextStep = FIRST_APPLY_STEPS.find((s) => !stepIsDone(s.id, progress));

  return (
    <section
      className={cn(
        surface.workspace,
        "relative overflow-hidden p-4 sm:p-5",
        motionFadeIn,
        className,
      )}
      aria-labelledby="first-apply-walkthrough-heading"
      data-testid="first-apply-walkthrough"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <p className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Guided walkthrough
          </p>
          <h2
            id="first-apply-walkthrough-heading"
            className="text-base font-semibold tracking-tight sm:text-lg"
          >
            {stats.allRequiredDone
              ? "You’re ready to apply for real"
              : "Your first application in five steps"}
          </h2>
          <p className="max-w-xl text-sm text-muted-foreground">
            {stats.allRequiredDone
              ? "Required steps are done. Keep reviewing diffs before every submit."
              : "Jober fills forms and drafts letters — you stay in control at review."}
          </p>
        </div>
        {!forceShow ? (
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={dismiss}
            aria-label="Dismiss walkthrough"
            className={motionPress}
          >
            <X className="size-4" aria-hidden />
          </Button>
        ) : null}
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
          <span>
            {stats.done} of {stats.total} steps
            {stats.requiredDone < stats.requiredTotal
              ? ` · ${stats.requiredTotal - stats.requiredDone} required left`
              : null}
          </span>
          <span className="font-mono tabular-nums">{pct}%</span>
        </div>
        <div
          className="h-1.5 w-full overflow-hidden rounded-full bg-muted"
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Walkthrough progress"
        >
          <div
            className="h-full rounded-full bg-primary motion-safe:transition-[width] motion-safe:duration-[var(--motion-view)] motion-safe:ease-[var(--ease-organic)]"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <ol className="mt-5 space-y-2">
        {FIRST_APPLY_STEPS.map((step, index) => {
          const done = stepIsDone(step.id, progress);
          const Icon = STEP_ICONS[step.id];
          const isNext =
            !done && FIRST_APPLY_STEPS.findIndex((s) => !stepIsDone(s.id, progress)) === index;
          return (
            <li
              key={step.id}
              className={cn(
                "flex flex-col gap-2 rounded-xl border px-3 py-3 sm:flex-row sm:items-center sm:justify-between",
                done
                  ? "border-border/50 bg-muted/20"
                  : isNext
                    ? "border-primary/35 bg-primary/5"
                    : "border-border/60 bg-background/40",
              )}
            >
              <div className="flex min-w-0 items-start gap-3">
                <span className="mt-0.5 shrink-0" aria-hidden>
                  {done ? (
                    <CheckCircle2 className="size-5 text-primary" />
                  ) : (
                    <Circle
                      className={cn(
                        "size-5",
                        isNext ? "text-primary" : "text-muted-foreground/50",
                      )}
                    />
                  )}
                </span>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <Icon className="size-3.5 text-muted-foreground" aria-hidden />
                    <p className="text-sm font-medium">
                      {index + 1}. {step.title}
                    </p>
                    {step.optional ? (
                      <span className="rounded-full border border-border/60 px-1.5 py-px font-mono text-[0.6rem] uppercase tracking-wide text-muted-foreground">
                        optional
                      </span>
                    ) : null}
                    {done ? (
                      <span className="sr-only">Completed</span>
                    ) : isNext ? (
                      <span className="rounded-full bg-primary/15 px-1.5 py-px font-mono text-[0.6rem] font-semibold uppercase tracking-wide text-primary">
                        Up next
                      </span>
                    ) : null}
                  </div>
                  <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground">{step.body}</p>
                </div>
              </div>
              {!done ? (
                <Link
                  href={step.href}
                  className={cn(
                    buttonVariants({
                      size: "sm",
                      variant: isNext ? "default" : "outline",
                    }),
                    "shrink-0 self-start sm:self-center",
                    motionPress,
                  )}
                >
                  {step.cta}
                </Link>
              ) : null}
            </li>
          );
        })}
      </ol>

      <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border/50 pt-4">
        {nextStep && !stats.allRequiredDone ? (
          <Link
            href={nextStep.href}
            className={cn(buttonVariants({ size: "sm" }), motionPress)}
          >
            Continue: {nextStep.cta}
          </Link>
        ) : null}
        <DemoWorkspaceButton size="sm" variant="outline" redirectTo="/queue" />
        {!forceShow && !stats.allRequiredDone ? (
          <Button type="button" variant="ghost" size="sm" onClick={dismiss}>
            Skip for now
          </Button>
        ) : null}
      </div>
    </section>
  );
}
