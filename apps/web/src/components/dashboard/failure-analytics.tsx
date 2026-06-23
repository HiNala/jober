"use client";

import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { fetchFailureAnalytics } from "@/lib/api/recovery";
import { surface } from "@/lib/design/tokens";

export function FailureAnalyticsPanel() {
  const analyticsQuery = useQuery({
    queryKey: ["failure-analytics"],
    queryFn: fetchFailureAnalytics,
  });

  const data = analyticsQuery.data;
  if (analyticsQuery.isError || !data || data.buckets.length === 0) {
    return (
      <Card className={surface.workspace}>
        <CardHeader>
          <CardTitle className="text-sm font-semibold tracking-tight">Failure analytics</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          {analyticsQuery.isError
            ? "Could not load failure data."
            : "No failure events recorded yet."}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={surface.workspace}>
      <CardHeader>
        <CardTitle className="text-sm font-semibold tracking-tight">Failure analytics by ATS</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {data.alerts.length > 0 && (
          <ul className="space-y-1 text-sm text-rose-600">
            {data.alerts.map((alert) => (
              <li key={`${String(alert.platform)}-${String(alert.failure_class)}`}>
                {String(alert.message)}
              </li>
            ))}
          </ul>
        )}
        <div className="overflow-x-auto rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Platform</TableHead>
                <TableHead>Failure class</TableHead>
                <TableHead className="text-right">Count</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.buckets.map((row) => (
                <TableRow
                  key={`${row.platform}-${row.failure_class}`}
                  className={row.circuit_tripped ? "bg-rose-500/5" : undefined}
                >
                  <TableCell>{row.platform}</TableCell>
                  <TableCell>{row.failure_class}</TableCell>
                  <TableCell className="text-right tabular-nums">{row.count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
