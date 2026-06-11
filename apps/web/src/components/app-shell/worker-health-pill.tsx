"use client";

import { useQuery } from "@tanstack/react-query";
import { Circle } from "lucide-react";

import { fetchReadiness } from "@/lib/api/health";
import { getApiBaseUrl } from "@/lib/api/client";
import { cn } from "@/lib/utils";

function degradedHint(detail?: string): string {
  const base = getApiBaseUrl();
  const hint = `Worker is not reachable at ${base}. Check your connection or try again shortly.`;
  return detail ? `${detail}\n${hint}` : hint;
}

export function WorkerHealthPill() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["readiness"],
    queryFn: fetchReadiness,
    refetchInterval: 15_000,
  });

  const ready = !isPending && !isError && data?.status === "ready";
  const label = isPending
    ? "Checking worker…"
    : ready
      ? "Worker healthy"
      : "Worker degraded";

  return (
    <div
      className={cn(
        "inline-flex max-w-[min(100%,14rem)] items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium sm:max-w-none",
        ready
          ? "border-accent/30 bg-accent/10 text-accent"
          : "border-destructive/30 bg-destructive/10 text-destructive",
      )}
      role="status"
      aria-live="polite"
      title={ready ? undefined : degradedHint(data?.detail)}
    >
      <Circle
        className={cn("size-2 shrink-0 fill-current", ready ? "text-accent" : "text-destructive")}
        aria-hidden
      />
      <span className="truncate">{label}</span>
    </div>
  );
}
