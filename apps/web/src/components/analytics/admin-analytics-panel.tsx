"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { AnalyticsBarChart } from "@/components/analytics/charts/bar-chart";
import { FunnelChart } from "@/components/analytics/charts/funnel-chart";
import { AnalyticsLineChart } from "@/components/analytics/charts/line-chart";
import { BigNumber } from "@/components/analytics/charts/big-number";
import { DateRangeControls } from "@/components/analytics/date-range-controls";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import {
  exportCsvUrl,
  fetchAdminCost,
  fetchAdminFunnel,
  fetchAdminTraffic,
  rangeFromPreset,
  type AnalyticsRangePreset,
} from "@/lib/api/analytics-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AdminAnalyticsPanel() {
  const [preset, setPreset] = useState<AnalyticsRangePreset>("30d");
  const [comparePrevious, setComparePrevious] = useState(false);
  const range = rangeFromPreset(preset);

  const funnel = useQuery({
    queryKey: ["analytics-funnel", range, comparePrevious],
    queryFn: () => fetchAdminFunnel(range, comparePrevious),
  });
  const traffic = useQuery({
    queryKey: ["analytics-traffic", range],
    queryFn: () => fetchAdminTraffic(range),
  });
  const cost = useQuery({
    queryKey: ["analytics-cost", range],
    queryFn: () => fetchAdminCost(range),
  });

  const loading = funnel.isLoading || traffic.isLoading || cost.isLoading;
  const error = funnel.isError || traffic.isError || cost.isError;

  if (loading) return <PageLoading label="Loading product analytics" />;
  if (error || !funnel.data || !traffic.data || !cost.data) {
    return <PageError message="Could not load admin analytics." onRetry={() => {
      void funnel.refetch();
      void traffic.refetch();
      void cost.refetch();
    }} />;
  }

  const attention = [...(cost.data.attention ?? [])];

  return (
    <div className={cn(spacing.section)}>
      <DateRangeControls
        preset={preset}
        onPresetChange={setPreset}
        comparePrevious={comparePrevious}
        onComparePreviousChange={setComparePrevious}
        exportHref={exportCsvUrl("/api/analytics/admin/funnel/export.csv", range)}
      />

      {attention.map((note) => (
        <p
          key={note.message}
          className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive"
        >
          {note.message}
        </p>
      ))}

      <Card className={surface.card}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">Signup funnel</CardTitle>
          <a
            href={exportCsvUrl("/api/analytics/admin/funnel/export.csv", range)}
            className="text-xs text-primary underline-offset-4 hover:underline"
          >
            Export funnel CSV
          </a>
        </CardHeader>
        <CardContent>
          <FunnelChart steps={funnel.data.steps} />
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="py-1">Step</th>
                  <th className="py-1">Sessions</th>
                  <th className="py-1">Drop-off</th>
                </tr>
              </thead>
              <tbody>
                {funnel.data.steps.map((row) => (
                  <tr key={row.step} className="border-t border-border/40">
                    <td className="py-1 capitalize">{row.step.replace(/_/g, " ")}</td>
                    <td className="py-1 tabular-nums">{row.unique_sessions}</td>
                    <td className="py-1 tabular-nums">
                      {row.drop_off_sessions} ({Math.round(row.drop_off_rate * 100)}%)
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className={cn(surface.card, "lg:col-span-2")}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Traffic by page</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsBarChart
              data={traffic.data.pages.slice(0, 8).map((p) => ({
                page: p.page,
                views: p.page_views,
              }))}
              xKey="page"
              yKey="views"
              label="Page views"
            />
          </CardContent>
        </Card>
        <Card className={surface.card}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Active users</CardTitle>
          </CardHeader>
          <CardContent>
            <BigNumber label="Page views" value={String(traffic.data.totals.page_views)} />
            <div className="mt-4">
              <AnalyticsLineChart
                data={traffic.data.active_users}
                xKey="day"
                yKey="dau"
                label="DAU"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className={surface.card}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">LLM cost</CardTitle>
          <a
            href={exportCsvUrl("/api/analytics/admin/cost/export.csv", range)}
            className="text-xs text-primary underline-offset-4 hover:underline"
          >
            Export cost CSV
          </a>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <BigNumber
              label="Rollup total"
              value={`$${cost.data.rollup_total_usd.toFixed(2)}`}
            />
            <BigNumber
              label="LlmCall total"
              value={`$${cost.data.llm_call_total_usd.toFixed(2)}`}
            />
            <BigNumber
              label="Reconciled"
              value={cost.data.reconciled ? "Yes" : "No"}
            />
          </div>
          <AnalyticsLineChart
            data={cost.data.by_day}
            xKey="day"
            yKey="cost_usd"
            label="Daily cost"
          />
        </CardContent>
      </Card>
    </div>
  );
}
