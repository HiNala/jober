import { cn } from "@/lib/utils";

/** Micro-interactions: hover, focus rings, button feedback (100–200ms). */
export const motionMicro = "motion-safe:transition-[color,background-color,border-color,opacity,transform] motion-safe:duration-150 motion-safe:ease-out";

/** View transitions: panels, sidebar, route content (200–500ms). */
export const motionView = "motion-safe:transition-[opacity,transform] motion-safe:duration-300 motion-safe:ease-out";

export const motionFadeIn = "motion-safe:animate-[jober-fade-in_300ms_ease-out_both]";

export function withMotion(
  base: string,
  opts?: { micro?: boolean; fadeIn?: boolean },
): string {
  return cn(
    base,
    opts?.micro !== false && motionMicro,
    opts?.fadeIn && motionFadeIn,
  );
}
