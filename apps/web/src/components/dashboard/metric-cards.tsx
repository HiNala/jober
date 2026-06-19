"use client";

import { useEffect, useState } from "react";
import { Activity, CheckCircle2, Clock, ListTodo } from "lucide-react";

import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { fetchDashboardSummary, type DashboardSummary } from "@/lib/api/batches";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function MetricCards() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchDashboardSummary();
        if (!cancelled) {
          setSummary(data);
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          setSummary(null);
          setLoading(false);
        }
      }
    };
    void load();
    const timer = setInterval(() => void load(), 5000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const metrics = [
    {
      label: "Queue depth",
      value: summary ? String(summary.queue_depth_priority_a) : "—",
      hint: "Priority A targets",
      icon: ListTodo,
      emphasize: false,
    },
    {
      label: "Active runs",
      value: summary ? String(summary.active_runs) : "0",
      hint: "In-flight attempts",
      icon: Activity,
      emphasize: (summary?.active_runs ?? 0) > 0,
    },
    {
      label: "Needs review",
      value: summary ? String(summary.needs_review) : "0",
      hint: "Open checkpoints",
      icon: Clock,
      emphasize: (summary?.needs_review ?? 0) > 0,
    },
    {
      label: "Running batches",
      value: summary ? String(summary.batches.length) : "0",
      hint: "Live batch jobs",
      icon: CheckCircle2,
      emphasize: false,
    },
  ] as const;

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-busy="true">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  return (
    <div className={cn("grid gap-4 sm:grid-cols-2 xl:grid-cols-4", motionFadeIn)}>
      {metrics.map(({ label, value, hint, icon: Icon, emphasize }) => (
        <Card
          key={label}
          className={cn(
            surface.workspace,
            emphasize && "border-primary/50 ring-1 ring-primary/30",
          )}
        >
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {label}
            </CardTitle>
            <Icon
              className={cn(
                "size-4",
                emphasize ? "text-primary" : "text-muted-foreground",
              )}
              aria-hidden
            />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold tabular-nums tracking-tight">{value}</div>
            <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
