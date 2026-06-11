"use client";

import { useQuery } from "@tanstack/react-query";

import { BigNumber } from "@/components/analytics/charts/big-number";
import { AnalyticsLineChart } from "@/components/analytics/charts/line-chart";
import { DateRangeControls } from "@/components/analytics/date-range-controls";
import Link from "next/link";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageEmpty, PageError, PageLoading } from "@/components/states/page-states";
import { buttonVariants } from "@/components/ui/button";
import {
  fetchUserAnalytics,
  rangeFromPreset,
  type AnalyticsRangePreset,
} from "@/lib/api/analytics-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { useState } from "react";

function deltaLabel(current: number, previous: number | undefined): string | undefined {
  if (previous === undefined) return undefined;
  const diff = current - previous;
  if (diff === 0) return "Same as previous period";
  const sign = diff > 0 ? "+" : "";
  return `${sign}${diff} vs previous period`;
}

export function UserAnalyticsPanel() {
  const [preset, setPreset] = useState<AnalyticsRangePreset>("30d");
  const [comparePrevious, setComparePrevious] = useState(false);
  const range = rangeFromPreset(preset);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["analytics-me", range, comparePrevious],
    queryFn: () => fetchUserAnalytics(range, comparePrevious),
  });

  if (isLoading) return <PageLoading label="Loading your analytics" />;
  if (isError || !data) return <PageError message="Could not load analytics." onRetry={() => refetch()} />;

  const hasActivity =
    data.summary.applications_sent > 0 ||
    data.summary.letters_generated > 0 ||
    data.activity.some((row) => row.runs > 0);

  return (
    <div className={cn(spacing.section)}>
      <DateRangeControls
        preset={preset}
        onPresetChange={setPreset}
        comparePrevious={comparePrevious}
        onComparePreviousChange={setComparePrevious}
        range={range}
        exportPath="/api/analytics/me/export.csv"
        exportFilename="user-analytics.csv"
      />

      {!hasActivity ? (
        <PageEmpty
          title="Analytics appear after your first run"
          description="Import jobs, launch a dry-run batch, and metrics will populate here — applications sent, letter usage, and LLM cost."
          action={
            <Link href="/queue" className={buttonVariants({ size: "sm" })}>
              Open queue
            </Link>
          }
        />
      ) : null}

      {data.attention.length > 0 ? (
        <div className="space-y-2">
          {data.attention.map((note) => (
            <p
              key={note.message}
              className={cn(
                "rounded-md border px-3 py-2 text-sm",
                note.level === "warn"
                  ? "border-destructive/40 bg-destructive/10 text-destructive"
                  : "border-border/60 bg-muted/40 text-muted-foreground",
              )}
            >
              {note.message}
            </p>
          ))}
        </div>
      ) : null}

      {hasActivity ? <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className={surface.card}>
          <CardContent className="pt-4">
            <BigNumber
              label="Applications sent"
              value={String(data.summary.applications_sent)}
              delta={deltaLabel(data.summary.applications_sent, data.previous?.applications_sent)}
            />
          </CardContent>
        </Card>
        <Card className={surface.card}>
          <CardContent className="pt-4">
            <BigNumber
              label="Responses tracked"
              value={String(data.summary.responses_tracked)}
              hint="Applied + rejected outcomes"
            />
          </CardContent>
        </Card>
        <Card className={surface.card}>
          <CardContent className="pt-4">
            <BigNumber
              label="Letters generated"
              value={String(data.summary.letters_generated)}
              delta={deltaLabel(data.summary.letters_generated, data.previous?.letters_generated)}
            />
          </CardContent>
        </Card>
        <Card className={surface.card}>
          <CardContent className="pt-4">
            <BigNumber
              label="LLM cost"
              value={`$${data.summary.llm_cost_usd.toFixed(2)}`}
              delta={
                data.previous
                  ? `$${(data.summary.llm_cost_usd - data.previous.llm_cost_usd).toFixed(2)} vs previous`
                  : undefined
              }
              hint={`${Math.round(data.summary.budget_used_ratio * 100)}% of $${data.summary.llm_budget_usd} budget`}
            />
          </CardContent>
        </Card>
      </div> : null}

      {hasActivity ? <div className="grid gap-4 lg:grid-cols-2">
        <Card className={surface.card}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Runs over time</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsLineChart data={data.activity} xKey="day" yKey="runs" label="Runs" />
          </CardContent>
        </Card>
        <Card className={surface.card}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">LLM cost over time</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsLineChart
              data={data.cost_series}
              xKey="day"
              yKey="cost_usd"
              label="Cost (USD)"
            />
          </CardContent>
        </Card>
      </div> : null}
    </div>
  );
}
