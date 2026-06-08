"use client";

import { motionShimmer } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface ReasoningShimmerProps {
  label?: string;
  className?: string;
}

/** In-progress agent step — calm shimmer; disabled under prefers-reduced-motion. */
export function ReasoningShimmer({ label = "Reasoning…", className }: ReasoningShimmerProps) {
  return (
    <span
      className={cn("inline-flex items-center gap-1.5 text-sm", className)}
      role="status"
      aria-live="polite"
    >
      <span
        className={cn(
          "bg-gradient-to-r from-muted-foreground/40 via-foreground/70 to-muted-foreground/40 bg-[length:200%_auto] bg-clip-text font-medium text-transparent",
          motionShimmer,
        )}
      >
        {label}
      </span>
    </span>
  );
}
