import { motionLivePulse, motionStatusEnter } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export type LiveStatus = "live" | "idle" | "needs_you";

export interface StatusLivePillProps {
  status: LiveStatus;
  /** Override display label. */
  label?: string;
  className?: string;
}

const LABELS: Record<LiveStatus, string> = {
  live: "Live",
  idle: "Idle",
  needs_you: "Needs you",
};

const TONE: Record<LiveStatus, string> = {
  live: "border-[color-mix(in_oklab,var(--live)_45%,transparent)] bg-[color-mix(in_oklab,var(--live)_14%,transparent)] text-[var(--live)]",
  idle: "border-border/60 bg-muted/50 text-muted-foreground",
  needs_you:
    "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-200",
};

/**
 * Live / Idle / Needs you pill — Live uses motionLivePulse on the indicator.
 */
export function StatusLivePill({ status, label, className }: StatusLivePillProps) {
  const display = label ?? LABELS[status];

  return (
    <span
      key={status}
      className={cn(
        "inline-flex h-6 items-center gap-1.5 rounded-full border px-2.5 text-xs font-medium tabular-nums",
        TONE[status],
        motionStatusEnter,
        className,
      )}
      data-slot="status-live-pill"
      data-status={status}
    >
      <span
        className={cn(
          "size-1.5 shrink-0 rounded-full",
          status === "live" && cn("bg-[var(--live)]", motionLivePulse),
          status === "idle" && "bg-muted-foreground/70",
          status === "needs_you" && "bg-amber-500",
        )}
        aria-hidden
      />
      {display}
    </span>
  );
}
