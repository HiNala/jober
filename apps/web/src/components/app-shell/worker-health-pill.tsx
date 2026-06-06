"use client";

import { useQuery } from "@tanstack/react-query";
import { Circle } from "lucide-react";

import { fetchReadiness } from "@/lib/api/health";
import { cn } from "@/lib/utils";

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
        "inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium",
        ready
          ? "border-accent/30 bg-accent/10 text-accent"
          : "border-destructive/30 bg-destructive/10 text-destructive",
      )}
      role="status"
      aria-live="polite"
      title={data?.detail}
    >
      <Circle
        className={cn("size-2 fill-current", ready ? "text-accent" : "text-destructive")}
        aria-hidden
      />
      <span>{label}</span>
    </div>
  );
}
