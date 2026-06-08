"use client";

import { StatusPill } from "@/components/motion/status-pill";
import { motionMicro, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import type { RunConsoleSnapshot } from "@/lib/api/run-console";

export interface StateTimelineProps {
  snapshot: RunConsoleSnapshot;
  selectedSeq: number | null;
  onSelectSeq: (seq: number | null) => void;
}

export function StateTimeline({ snapshot, selectedSeq, onSelectSeq }: StateTimelineProps) {
  const activeSeq = selectedSeq ?? snapshot.timeline[snapshot.timeline.length - 1]?.seq;

  if (snapshot.timeline.length === 0) {
    return (
      <div className="flex flex-wrap items-center gap-2">
        <StatusPill status={snapshot.status} />
        {snapshot.current_step ? (
          <span className="text-xs text-muted-foreground">step {snapshot.current_step}</span>
        ) : null}
        <span className="text-xs text-muted-foreground">
          {snapshot.attempt_count} attempt{snapshot.attempt_count === 1 ? "" : "s"}
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <StatusPill status={snapshot.status} />
        <p className="text-xs text-muted-foreground">Scrub timeline — click a state to inspect</p>
      </div>
      <ol className="flex flex-wrap gap-2">
        {snapshot.timeline.map((item) => {
          const selected = activeSeq === item.seq;
          const stepStatus = item.status ?? snapshot.status;
          return (
            <li key={item.seq}>
              <button
                type="button"
                onClick={() => onSelectSeq(selectedSeq === item.seq ? null : item.seq)}
                className={cn(
                  "rounded-md border px-2 py-1 text-xs",
                  motionMicro,
                  motionPress,
                  selected
                    ? "border-primary bg-primary/10 text-foreground shadow-sm"
                    : "border-border/60 text-muted-foreground hover:bg-muted/50",
                )}
                aria-pressed={selected}
              >
                {item.step ?? stepStatus.replace(/_/g, " ") ?? "state"}
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
