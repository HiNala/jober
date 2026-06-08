"use client";

import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface MotionCrossfadeProps {
  /** Change to re-trigger enter animation (view mode, surface, route). */
  motionKey: string;
  children: React.ReactNode;
  className?: string;
}

/** Cross-fade wrapper — opacity/transform only; no layout thrash during SSE bursts. */
export function MotionCrossfade({ motionKey, children, className }: MotionCrossfadeProps) {
  return (
    <div key={motionKey} className={cn("min-h-0", motionFadeIn, className)}>
      {children}
    </div>
  );
}
