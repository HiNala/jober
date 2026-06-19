"use client";

import { useEffect, useState } from "react";

import { Progress } from "@/components/ui/progress";
import { fetchDashboardSummary, type DashboardSummary } from "@/lib/api/batches";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function StatusBadge({ label }: { label: "Running" | "Paused" | "Idle" }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        label === "Running" && "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
        label === "Paused" && "bg-amber-500/10 text-amber-600 dark:text-amber-400",
        label === "Idle" && "bg-muted text-muted-foreground",
      )}
    >
      <span
        className={cn(
          "size-1.5 rounded-full",
          label === "Running" && "animate-pulse bg-emerald-500",
          label === "Paused" && "bg-amber-500",
          label === "Idle" && "bg-muted-foreground/50",
        )}
        aria-hidden
      />
      {label}
    </span>
  );
}

export function WorkerStatusPanel() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [fetchError, setFetchError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchDashboardSummary();
        if (!cancelled) {
          setSummary(data);
          setFetchError(false);
        }
      } catch {
        if (!cancelled) {
          setSummary(null);
          setFetchError(true);
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

  const worker = summary?.worker;
  const max = worker?.max_concurrency ?? 1;
  const active = worker?.active_runs ?? 0;
  const pct = max > 0 ? Math.min(100, (active / max) * 100) : 0;
  const label: "Running" | "Paused" | "Idle" = worker?.globally_paused
    ? "Paused"
    : active > 0
      ? "Running"
      : "Idle";

  return (
    <div className={cn(surface.workspace, "p-4")}>
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-medium">Worker pool</h2>
          <p className="text-xs text-muted-foreground">
            {fetchError ? (
              <span className="text-destructive/70">Connection error — retrying…</span>
            ) : (
              "Celery + Playwright"
            )}
          </p>
        </div>
        <StatusBadge label={label} />
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
