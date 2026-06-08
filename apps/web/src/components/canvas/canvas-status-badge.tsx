"use client";

import { AlertCircle, Hand } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { useRunCanvas } from "@/contexts/run-canvas-context";

export function CanvasStatusBadge() {
  const runCanvas = useRunCanvas();
  const warnings = runCanvas?.warningCount ?? 0;
  const needsHuman = runCanvas?.snapshot?.open_checkpoint != null;

  if (!runCanvas?.runId) {
    return (
      <Badge variant="secondary" className="gap-1 shadow-sm">
        Idle
      </Badge>
    );
  }

  if (needsHuman) {
    return (
      <Badge variant="destructive" className="gap-1 shadow-sm">
        <Hand className="size-3" aria-hidden />
        Needs you
      </Badge>
    );
  }

  if (warnings > 0) {
    return (
      <Badge variant="secondary" className="gap-1 border-amber-500/40 bg-amber-500/10 shadow-sm">
        <AlertCircle className="size-3" aria-hidden />
        {warnings} warning{warnings === 1 ? "" : "s"}
      </Badge>
    );
  }

  return (
    <Badge variant="secondary" className="gap-1 shadow-sm">
      {runCanvas.status === "open" ? "Streaming" : runCanvas.status}
    </Badge>
  );
}
