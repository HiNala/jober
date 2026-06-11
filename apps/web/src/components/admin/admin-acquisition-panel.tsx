"use client";

import { useQuery } from "@tanstack/react-query";

import { AnalyticsBarChart } from "@/components/analytics/charts/bar-chart";
import { FunnelChart } from "@/components/analytics/charts/funnel-chart";
import { AnalyticsLineChart } from "@/components/analytics/charts/line-chart";
import { BigNumber } from "@/components/analytics/charts/big-number";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import { fetchAdminAcquisition } from "@/lib/api/admin-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AdminAcquisitionPanel() {
  const acquisition = useQuery({
    queryKey: ["admin-acquisition"],
    queryFn: fetchAdminAcquisition,
  });

  if (acquisition.isLoading) return <PageLoading label="Loading acquisition…" />;
  if (acquisition.isError || !acquisition.data) {
    return (
      <PageError message="Could not load acquisition." onRetry={() => acquisition.refetch()} />
    );
  }

  const data = acquisition.data;

  return (
    <div className={cn(spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Acquisition & funnel</h1>
        <p className="text-sm text-muted-foreground">
          Traffic sources, signup funnel, and coarse geo — rollup data only.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <BigNumber label="Account signups" value={String(data.signups)} />
        <BigNumber label="Funnel signups" value={String(data.funnel_signups)} />
        <BigNumber
          label="Sessions"
          value={String(data.traffic.totals.sessions)}
        />
      </div>

      <Card className={surface.workspace}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Signup funnel</CardTitle>
        </CardHeader>
        <CardContent>
          <FunnelChart steps={data.funnel.steps} />
        </CardContent>
      </Card>

      <Card className={surface.workspace}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Traffic & DAU</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <AnalyticsBarChart
            data={data.traffic.pages.slice(0, 8).map((p) => ({
              page: p.page,
              views: p.page_views,
            }))}
            xKey="page"
            yKey="views"
            label="Page views"
          />
          <AnalyticsLineChart
            data={data.traffic.active_users}
            xKey="day"
            yKey="dau"
            label="DAU"
          />
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className={surface.workspace}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">UTM sources</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="py-1">Source</th>
                  <th className="py-1">Medium</th>
                  <th className="py-1">Events</th>
                </tr>
              </thead>
              <tbody>
                {data.utm_sources.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="py-2 text-muted-foreground">
                      No UTM-tagged traffic in range.
                    </td>
                  </tr>
                ) : (
                  data.utm_sources.map((row) => (
                    <tr key={`${row.utm_source}-${row.utm_medium}`} className="border-t border-border/40">
                      <td className="py-1">{row.utm_source}</td>
                      <td className="py-1">{row.utm_medium ?? "—"}</td>
                      <td className="py-1 tabular-nums">{row.sessions}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card className={surface.workspace}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Geo (coarse)</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="py-1">Country</th>
                  <th className="py-1">Sessions</th>
                </tr>
              </thead>
              <tbody>
                {data.geo.map((row) => (
                  <tr key={row.country} className="border-t border-border/40">
                    <td className="py-1">{row.country}</td>
                    <td className="py-1 tabular-nums">{row.sessions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
