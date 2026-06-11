"use client";

import { useQuery } from "@tanstack/react-query";

import { AttentionBanner } from "@/components/admin/attention-banner";
import { AnalyticsBarChart } from "@/components/analytics/charts/bar-chart";
import { AnalyticsLineChart } from "@/components/analytics/charts/line-chart";
import { BigNumber } from "@/components/analytics/charts/big-number";
import { ExportCsvButton } from "@/components/analytics/export-csv-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import { fetchAdminCostDashboard } from "@/lib/api/admin-dashboard";
import { rangeFromPreset } from "@/lib/api/analytics-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AdminCostPanel() {
  const range = rangeFromPreset("30d");
  const cost = useQuery({
    queryKey: ["admin-cost-dashboard", range],
    queryFn: () => fetchAdminCostDashboard(),
  });

  if (cost.isLoading) return <PageLoading label="Loading cost…" />;
  if (cost.isError || !cost.data) {
    return <PageError message="Could not load cost." onRetry={() => cost.refetch()} />;
  }

  const data = cost.data;

  return (
    <div className={cn(spacing.section)}>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Cost & budgets</h1>
          <p className="text-sm text-muted-foreground">
            Token spend reconciled against source LLM call tables.
          </p>
        </div>
        <ExportCsvButton
          path="/api/analytics/admin/cost/export.csv"
          range={range}
          filename="cost.csv"
          label="Export CSV"
        />
      </div>

      <AttentionBanner items={data.attention ?? []} />

      <div className="grid gap-4 sm:grid-cols-3">
        <BigNumber label="Rollup total" value={`$${data.rollup_total_usd.toFixed(2)}`} />
        <BigNumber label="LlmCall total" value={`$${data.llm_call_total_usd.toFixed(2)}`} />
        <BigNumber label="Reconciled" value={data.reconciled ? "Yes" : "No"} />
      </div>

      <Card className={surface.workspace}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Daily spend</CardTitle>
        </CardHeader>
        <CardContent>
          <AnalyticsLineChart data={data.by_day} xKey="day" yKey="cost_usd" label="Daily cost" />
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className={surface.workspace}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">By model</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsBarChart
              data={data.by_model.slice(0, 8)}
              xKey="model"
              yKey="cost_usd"
              label="Cost USD"
            />
          </CardContent>
        </Card>
        <Card className={surface.workspace}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">By agent</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsBarChart
              data={data.by_agent.slice(0, 8)}
              xKey="agent_role"
              yKey="cost_usd"
              label="Cost USD"
            />
          </CardContent>
        </Card>
      </div>

      {data.anomalies.length ? (
        <Card className={surface.workspace}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Spend anomalies</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="py-1">Day</th>
                  <th className="py-1">Cost</th>
                </tr>
              </thead>
              <tbody>
                {data.anomalies.map((row) => (
                  <tr key={row.day} className="border-t border-border/40">
                    <td className="py-1">{row.day}</td>
                    <td className="py-1 tabular-nums">${row.cost_usd.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
