"use client";

import { useQuery } from "@tanstack/react-query";

import { BatchPanel } from "@/components/dashboard/batch-panel";
import { DashboardFirstRun } from "@/components/dashboard/dashboard-first-run";
import { EventStream } from "@/components/dashboard/event-stream";
import { FailureAnalyticsPanel } from "@/components/dashboard/failure-analytics";
import { MetricCards } from "@/components/dashboard/metric-cards";
import { NeedsAttentionBanner } from "@/components/dashboard/needs-attention";
import { WorkerStatusPanel } from "@/components/dashboard/worker-status";
import { PageLoading } from "@/components/states/page-states";
import { fetchJobTargets } from "@/lib/api/jobs";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function DashboardContent() {
  const jobsQuery = useQuery({
    queryKey: ["job-targets"],
    queryFn: () => fetchJobTargets(),
  });

  if (jobsQuery.isLoading) {
    return <PageLoading label="Loading dashboard…" />;
  }

  const isFirstRun = (jobsQuery.data?.length ?? 0) === 0;

  if (isFirstRun) {
    return (
      <div className={cn(spacing.section, spacing.page)}>
        <header className="sr-only">
          <h1>Dashboard</h1>
        </header>
        <DashboardFirstRun />
      </div>
    );
  }

  return (
    <div className={cn(spacing.section, spacing.page)}>
      <header className="sr-only">
        <h1>Dashboard</h1>
      </header>
      <NeedsAttentionBanner />
      <MetricCards />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <EventStream />
          <FailureAnalyticsPanel />
        </div>
        <div className="space-y-4">
          <WorkerStatusPanel />
          <BatchPanel />
        </div>
      </div>
    </div>
  );
}
