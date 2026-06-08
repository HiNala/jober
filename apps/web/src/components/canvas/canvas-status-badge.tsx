"use client";

import { AlertCircle, Hand, Radio } from "lucide-react";

import { StatusPill } from "@/components/motion/status-pill";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { cn } from "@/lib/utils";

export function CanvasStatusBadge() {
  const runCanvas = useRunCanvas();
  const warnings = runCanvas?.warningCount ?? 0;
  const needsHuman = runCanvas?.snapshot?.open_checkpoint != null;

  if (!runCanvas?.runId) {
    return <StatusPill status="idle" label="Idle" />;
  }

  if (needsHuman) {
    return (
      <StatusPill
        status="review_and_submit"
        label="Needs you"
        icon={<Hand className="size-3" aria-hidden />}
        className="shadow-sm"
      />
    );
  }

  if (warnings > 0) {
    return (
      <span
        className={cn(
          "inline-flex h-5 items-center gap-1 rounded-full border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-800 shadow-sm dark:text-amber-200",
        )}
      >
        <AlertCircle className="size-3" aria-hidden />
        {warnings} warning{warnings === 1 ? "" : "s"}
      </span>
    );
  }

  const streaming = runCanvas.status === "open";
  return (
    <StatusPill
      status={streaming ? "in_progress" : runCanvas.snapshot?.status ?? "idle"}
      label={streaming ? "Streaming" : runCanvas.status}
      icon={streaming ? <Radio className="size-3" aria-hidden /> : undefined}
      className="shadow-sm"
    />
  );
}
