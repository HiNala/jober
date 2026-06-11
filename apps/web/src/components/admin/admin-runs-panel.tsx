"use client";

import { useQuery } from "@tanstack/react-query";

import { AttentionBanner } from "@/components/admin/attention-banner";
import { AnalyticsBarChart } from "@/components/analytics/charts/bar-chart";
import { BigNumber } from "@/components/analytics/charts/big-number";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import { fetchAdminRuns } from "@/lib/api/admin-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AdminRunsPanel() {
  const runs = useQuery({ queryKey: ["admin-runs"], queryFn: fetchAdminRuns });

  if (runs.isLoading) return <PageLoading label="Loading runs…" />;
  if (runs.isError || !runs.data) {
    return <PageError message="Could not load runs." onRetry={() => runs.refetch()} />;
  }

  const data = runs.data;
  const failureChart = data.failures_by_platform.slice(0, 10).map((row) => ({
    label: `${row.platform} · ${row.failure_class}`,
    count: row.count,
  }));

  return (
    <div className={cn(spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Runs & reliability</h1>
        <p className="text-sm text-muted-foreground">
          Product-wide outcomes and failure classes — no private job content.
        </p>
      </div>

      <AttentionBanner items={data.attention} />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <BigNumber label="Runs" value={String(data.totals.runs)} />
        <BigNumber label="Succeeded" value={String(data.totals.succeeded)} />
        <BigNumber label="Failed" value={String(data.totals.failed)} />
        <BigNumber
          label="Needs human"
          value={String(data.totals.needs_human_backlog)}
        />
      </div>

      <Card className={surface.workspace}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Recovery rate</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-semibold tabular-nums">
            {Math.round(data.totals.recovery_rate * 100)}%
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Succeeded / (succeeded + failed) in {data.range.start} → {data.range.end}
          </p>
        </CardContent>
      </Card>

      <Card className={surface.workspace}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Failures by ATS platform</CardTitle>
        </CardHeader>
        <CardContent>
          {failureChart.length ? (
            <AnalyticsBarChart
              data={failureChart}
              xKey="label"
              yKey="count"
              label="Failure count"
            />
          ) : (
            <p className="text-sm text-muted-foreground">No failure events in range.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
