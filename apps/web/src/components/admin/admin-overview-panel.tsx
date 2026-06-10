"use client";

import { useQuery } from "@tanstack/react-query";

import { AttentionBanner } from "@/components/admin/attention-banner";
import { BigNumber } from "@/components/analytics/charts/big-number";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import { fetchAdminOverview } from "@/lib/api/admin-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AdminOverviewPanel() {
  const overview = useQuery({ queryKey: ["admin-overview"], queryFn: fetchAdminOverview });

  if (overview.isLoading) return <PageLoading label="Loading admin overview…" />;
  if (overview.isError || !overview.data) {
    return (
      <PageError message="Could not load overview." onRetry={() => overview.refetch()} />
    );
  }

  const data = overview.data;

  return (
    <div className={cn(spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Overview</h1>
        <p className="text-sm text-muted-foreground">
          What needs attention now — growth, runs, cost, and system health.
        </p>
      </div>

      <AttentionBanner items={data.attention} />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <BigNumber label="DAU" value={String(data.active_users.dau)} />
        <BigNumber label="WAU" value={String(data.active_users.wau)} />
        <BigNumber label="MAU" value={String(data.active_users.mau)} />
        <BigNumber label="Signups (30d)" value={String(data.signups.last_30d)} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className={surface.card}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Runs (30d)</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Total</p>
              <p className="text-xl font-semibold tabular-nums">{data.runs.total}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Succeeded</p>
              <p className="text-xl font-semibold tabular-nums">{data.runs.succeeded}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Failed</p>
              <p className="text-xl font-semibold tabular-nums">{data.runs.failed}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Needs human</p>
              <p className="text-xl font-semibold tabular-nums text-amber-600">
                {data.runs.needs_human}
              </p>
            </div>
            <div className="col-span-2">
              <p className="text-muted-foreground">Submits (30d)</p>
              <p className="text-xl font-semibold tabular-nums">{data.submits_30d}</p>
            </div>
          </CardContent>
        </Card>

        <Card className={surface.card}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Cost & health</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">LLM spend (30d)</span>
              <span className="font-medium tabular-nums">
                ${data.cost.last_30d_usd.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Forecast (month)</span>
              <span className="font-medium tabular-nums">
                ${data.cost.forecast_monthly_usd.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Infrastructure</span>
              <span
                className={cn(
                  "font-medium capitalize",
                  data.health.status === "ready" ? "text-emerald-600" : "text-destructive",
                )}
              >
                {data.health.status.replace("_", " ")}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Queue paused</span>
              <span className="font-medium">
                {data.health.queue.globally_paused ? "Yes" : "No"}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Active runs</span>
              <span className="font-medium tabular-nums">{data.health.queue.active_runs}</span>
            </div>
            {data.ops?.budget ? (
              <div className="flex justify-between gap-4">
                <span className="text-muted-foreground">LLM budget (month)</span>
                <span
                  className={cn(
                    "font-medium tabular-nums",
                    data.ops.budget.hard_stop
                      ? "text-destructive"
                      : data.ops.budget.soft_warn
                        ? "text-amber-600"
                        : undefined,
                  )}
                >
                  ${data.ops.budget.spent_usd.toFixed(2)} / ${data.ops.budget.monthly_budget_usd.toFixed(0)}
                </span>
              </div>
            ) : null}
            {typeof data.ops?.recovery_rate_30d === "number" ? (
              <div className="flex justify-between gap-4">
                <span className="text-muted-foreground">Run success rate (30d)</span>
                <span className="font-medium tabular-nums">
                  {Math.round(data.ops.recovery_rate_30d * 100)}%
                </span>
              </div>
            ) : null}
            {typeof data.health.queue.celery_broker_depth === "number" ? (
              <div className="flex justify-between gap-4">
                <span className="text-muted-foreground">Celery backlog</span>
                <span className="font-medium tabular-nums">
                  {data.health.queue.celery_broker_depth}
                </span>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
