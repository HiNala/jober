"use client";

import Link from "next/link";
import { CheckCircle2, SkipForward, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { motionFadeIn } from "@/lib/design/motion";
import type { RunConsoleSnapshot } from "@/lib/api/run-console";
import { cn } from "@/lib/utils";

import { ArtifactLinks } from "./artifact-links";

const TERMINAL_STATUSES = new Set([
  "succeeded",
  "applied",
  "failed_final",
  "skipped",
]);

export function isTerminalRunStatus(status: string): boolean {
  return TERMINAL_STATUSES.has(status);
}

export function RunEndStateSummary({
  snapshot,
  className,
}: {
  snapshot: RunConsoleSnapshot;
  className?: string;
}) {
  if (!isTerminalRunStatus(snapshot.status)) {
    return null;
  }

  const isSuccess = snapshot.status === "succeeded" || snapshot.status === "applied";
  const isSkipped = snapshot.status === "skipped";
  const isFailed = snapshot.status === "failed_final";

  const title = isSuccess
    ? "Application submitted"
    : isSkipped
      ? "Run skipped"
      : "Run failed";

  const description = isSuccess
    ? "This run finished successfully. Artifacts are available below."
    : isSkipped
      ? "You chose to skip this application. The run is closed."
      : "The run ended without a successful submit. Review artifacts and the failure report in the job drawer.";

  const Icon = isSuccess ? CheckCircle2 : isSkipped ? SkipForward : XCircle;
  const iconClass = isSuccess
    ? "text-accent"
    : isSkipped
      ? "text-muted-foreground"
      : "text-destructive";

  return (
    <section
      className={cn(
        "space-y-4 rounded-lg border border-border/60 bg-muted/20 p-4",
        motionFadeIn,
        className,
      )}
      aria-labelledby="run-end-state-heading"
    >
      <div className="flex items-start gap-3">
        <Icon className={cn("mt-0.5 size-5 shrink-0", iconClass)} aria-hidden />
        <div className="min-w-0 space-y-1">
          <h2 id="run-end-state-heading" className="text-base font-semibold">
            {title}
          </h2>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
      {snapshot.artifacts.length > 0 ? (
        <ArtifactLinks artifacts={snapshot.artifacts} />
      ) : null}
      <div className="flex flex-wrap gap-2">
        <Button variant="outline" size="sm" render={<Link href="/queue" />}>
          Back to queue
        </Button>
        {isFailed ? (
          <Button
            variant="secondary"
            size="sm"
            render={<Link href={`/queue?job=${snapshot.job_target_id}`} />}
          >
            View job in queue
          </Button>
        ) : null}
      </div>
    </section>
  );
}
