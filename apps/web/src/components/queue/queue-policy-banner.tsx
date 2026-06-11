"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { fetchDailyPlan, fetchDashboardSummary } from "@/lib/api/batches";
import { cn } from "@/lib/utils";

export function QueuePolicyBanner({ className }: { className?: string }) {
  const summaryQuery = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary,
    refetchInterval: 30_000,
  });
  const planQuery = useQuery({
    queryKey: ["daily-plan"],
    queryFn: fetchDailyPlan,
    staleTime: 60_000,
  });

  const paused = summaryQuery.data?.worker.globally_paused;

  if (paused) {
    return (
      <div
        className={cn(
          "rounded-lg border border-amber-500/35 bg-amber-500/10 px-3 py-2 text-sm text-amber-950 dark:text-amber-100",
          className,
        )}
        role="status"
      >
        Queue is paused — workers will not pick up new runs.{" "}
        <Link href="/dashboard" className="font-medium underline underline-offset-2">
          Resume from dashboard
        </Link>
      </div>
    );
  }

  const pacingNote = planQuery.data?.pacing_note;
  if (!pacingNote) {
    return null;
  }

  return (
    <p className={cn("text-xs text-muted-foreground", className)} role="note">
      {pacingNote}{" "}
      <Link href="/dashboard" className="underline underline-offset-2">
        Batch control
      </Link>
    </p>
  );
}
