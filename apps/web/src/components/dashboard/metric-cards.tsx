"use client";

import { useEffect, useState } from "react";
import { Activity, CheckCircle2, Clock, ListTodo } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchDashboardSummary, type DashboardSummary } from "@/lib/api/batches";

export function MetricCards() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchDashboardSummary();
        if (!cancelled) setSummary(data);
      } catch {
        if (!cancelled) setSummary(null);
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
    },
    {
      label: "Active runs",
      value: summary ? String(summary.active_runs) : "0",
      hint: "Workers executing",
      icon: Activity,
    },
    {
      label: "Needs review",
      value: summary ? String(summary.needs_review) : "0",
      hint: "Human checkpoints",
      icon: Clock,
    },
    {
      label: "Running batches",
      value: summary ? String(summary.batches.length) : "0",
      hint: "Live batch jobs",
      icon: CheckCircle2,
    },
  ] as const;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map(({ label, value, hint, icon: Icon }) => (
        <Card key={label} className="border-border/60 bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {label}
            </CardTitle>
            <Icon className="size-4 text-muted-foreground" aria-hidden />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold tabular-nums">{value}</div>
            <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
