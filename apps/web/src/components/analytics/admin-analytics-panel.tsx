"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { AnalyticsBarChart } from "@/components/analytics/charts/bar-chart";
import { FunnelChart } from "@/components/analytics/charts/funnel-chart";
import { AnalyticsLineChart } from "@/components/analytics/charts/line-chart";
import { BigNumber } from "@/components/analytics/charts/big-number";
import { DateRangeControls } from "@/components/analytics/date-range-controls";
import { ExportCsvButton } from "@/components/analytics/export-csv-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import {
  fetchAdminCost,
  fetchAdminFunnel,
  fetchAdminTraffic,
  rangeFromPreset,
  type AnalyticsRangePreset,
  type FunnelStep,
} from "@/lib/api/analytics-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function funnelDropOffDelta(
  step: FunnelStep,
  previousByStep: Map<string, FunnelStep> | undefined,
): string | null {
  if (!previousByStep) return null;
  const prev = previousByStep.get(step.step);
  if (!prev) return null;
  const delta = Math.round((step.drop_off_rate - prev.drop_off_rate) * 100);
  if (delta === 0) return "same";
  const sign = delta > 0 ? "+" : "";
  return `${sign}${delta}pp drop-off`;
}

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
    return (
      <PageError
        message="Could not load admin analytics."
        onRetry={() => {
          void funnel.refetch();
          void traffic.refetch();
          void cost.refetch();
        }}
      />
    );
  }

  const previousByStep = funnel.data.previous_steps
    ? new Map(funnel.data.previous_steps.map((row) => [row.step, row]))
    : undefined;
  const funnelAttention = previousByStep
    ? funnel.data.steps
        .filter((step) => {
          const prev = previousByStep.get(step.step);
          return prev && step.drop_off_rate > prev.drop_off_rate + 0.05;
        })
        .map(
          (step) =>
            `Drop-off at "${step.step.replace(/_/g, " ")}" rose vs the previous period.`,
        )
    : [];
  const attention = [...funnelAttention, ...(cost.data.attention ?? []).map((n) => n.message)];

  return (
    <div className={cn(spacing.section)}>
      <DateRangeControls
        preset={preset}
        onPresetChange={setPreset}
        comparePrevious={comparePrevious}
        onComparePreviousChange={setComparePrevious}
        range={range}
        exportPath="/api/analytics/admin/funnel/export.csv"
        exportFilename="funnel.csv"
      />

      {attention.map((message) => (
        <p
          key={message}
          className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive"
        >
          {message}
        </p>
      ))}

      <Card className={surface.workspace}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">Signup funnel</CardTitle>
          <ExportCsvButton
            path="/api/analytics/admin/funnel/export.csv"
            range={range}
            filename="funnel.csv"
            label="Export funnel CSV"
          />
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
                  {comparePrevious ? <th className="py-1">vs prior</th> : null}
                </tr>
              </thead>
              <tbody>
                {funnel.data.steps.map((row) => {
                  const delta = funnelDropOffDelta(row, previousByStep);
                  return (
                    <tr key={row.step} className="border-t border-border/40">
                      <td className="py-1 capitalize">{row.step.replace(/_/g, " ")}</td>
                      <td className="py-1 tabular-nums">{row.unique_sessions}</td>
                      <td className="py-1 tabular-nums">
                        {row.drop_off_sessions} ({Math.round(row.drop_off_rate * 100)}%)
                      </td>
                      {comparePrevious ? (
                        <td
                          className={cn(
                            "py-1 tabular-nums",
                            delta && delta !== "same" && delta.startsWith("+")
                              ? "text-destructive"
                              : "text-muted-foreground",
                          )}
                        >
                          {delta ?? "—"}
                        </td>
                      ) : null}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card className={surface.workspace}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">Traffic</CardTitle>
          <ExportCsvButton
            path="/api/analytics/admin/traffic/export.csv"
            range={range}
            filename="traffic.csv"
            label="Export traffic CSV"
          />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <AnalyticsBarChart
                data={traffic.data.pages.slice(0, 8).map((p) => ({
                  page: p.page,
                  views: p.page_views,
                }))}
                xKey="page"
                yKey="views"
                label="Page views"
              />
            </div>
            <div>
              <BigNumber label="Page views" value={String(traffic.data.totals.page_views)} />
              <BigNumber
                className="mt-4"
                label="Sessions"
                value={String(traffic.data.totals.sessions)}
              />
              <div className="mt-4">
                <AnalyticsLineChart
                  data={traffic.data.active_users}
                  xKey="day"
                  yKey="dau"
                  label="DAU"
                />
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="py-1">Page</th>
                  <th className="py-1">Views</th>
                  <th className="py-1">Sessions</th>
                  <th className="py-1">Avg time</th>
                  <th className="py-1">Bounce</th>
                </tr>
              </thead>
              <tbody>
                {traffic.data.pages.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-2 text-muted-foreground">
                      No page traffic in this range.
                    </td>
                  </tr>
                ) : (
                  traffic.data.pages.map((row) => (
                    <tr key={row.page} className="border-t border-border/40">
                      <td className="max-w-[12rem] truncate py-1" title={row.page}>
                        {row.page}
                      </td>
                      <td className="py-1 tabular-nums">{row.page_views}</td>
                      <td className="py-1 tabular-nums">{row.unique_sessions}</td>
                      <td className="py-1 tabular-nums">{row.avg_time_on_page_sec}s</td>
                      <td className="py-1 tabular-nums">
                        {Math.round(row.bounce_rate * 100)}%
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card className={surface.workspace}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">LLM cost</CardTitle>
          <ExportCsvButton
            path="/api/analytics/admin/cost/export.csv"
            range={range}
            filename="cost.csv"
            label="Export cost CSV"
          />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <BigNumber label="Rollup total" value={`$${cost.data.rollup_total_usd.toFixed(2)}`} />
            <BigNumber
              label="LlmCall total"
              value={`$${cost.data.llm_call_total_usd.toFixed(2)}`}
            />
            <BigNumber label="Reconciled" value={cost.data.reconciled ? "Yes" : "No"} />
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
