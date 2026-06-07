"use client";

import { cn } from "@/lib/utils";
import type { RunConsoleSnapshot } from "@/lib/api/run-console";

export interface StateTimelineProps {
  snapshot: RunConsoleSnapshot;
  selectedSeq: number | null;
  onSelectSeq: (seq: number | null) => void;
}

export function StateTimeline({ snapshot, selectedSeq, onSelectSeq }: StateTimelineProps) {
  if (snapshot.timeline.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Status: <span className="font-medium text-foreground">{snapshot.status}</span>
        {snapshot.current_step ? ` · step ${snapshot.current_step}` : null}
        {" · "}
        {snapshot.attempt_count} attempt{snapshot.attempt_count === 1 ? "" : "s"}
      </p>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">Scrub timeline — click a state to inspect</p>
      <ol className="flex flex-wrap gap-2">
        {snapshot.timeline.map((item) => (
          <li key={item.seq}>
            <button
              type="button"
              onClick={() => onSelectSeq(selectedSeq === item.seq ? null : item.seq)}
              className={cn(
                "rounded-md border px-2 py-1 text-xs transition-colors",
                selectedSeq === item.seq
                  ? "border-primary bg-primary/10 text-foreground"
                  : "border-border/60 text-muted-foreground hover:bg-muted/50",
              )}
            >
              {item.step ?? item.status ?? "state"}
            </button>
          </li>
        ))}
      </ol>
    </div>
  );
}
