"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { fetchDashboardSummary, type DashboardSummary } from "@/lib/api/batches";

export function WorkerStatusPanel() {
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

  const worker = summary?.worker;
  const max = worker?.max_concurrency ?? 1;
  const active = worker?.active_runs ?? 0;
  const pct = max > 0 ? Math.min(100, (active / max) * 100) : 0;
  const label = worker?.globally_paused ? "Paused" : active > 0 ? "Running" : "Idle";

  return (
    <div className="rounded-lg border border-border/60 bg-card/80 p-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-medium">Worker pool</h2>
          <p className="text-xs text-muted-foreground">Celery + Playwright</p>
        </div>
        <Badge variant="outline" className="text-xs">
          {label}
        </Badge>
      </div>
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Capacity</span>
          <span>
            {active} / {max} slots
          </span>
        </div>
        <Progress value={pct} aria-label="Worker capacity used" />
      </div>
    </div>
  );
}
