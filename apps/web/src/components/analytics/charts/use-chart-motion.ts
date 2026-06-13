"use client";

import { usePrefersReducedMotion } from "@/lib/hooks/use-prefers-reduced-motion";

/** Recharts draw-in — disabled when user prefers reduced motion. */
export function useChartMotion() {
  const reduced = usePrefersReducedMotion();
  return {
    isAnimationActive: !reduced,
    animationDuration: reduced ? 0 : 800,
    animationBegin: 0,
  } as const;
}
