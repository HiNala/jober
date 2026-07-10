import { cn } from "@/lib/utils";

/**
 * Central motion vocabulary — durations, easings, and Tailwind class bundles.
 * CSS variables are defined in `globals.css`; do not hard-code durations in feature components.
 */

/** Canonical durations (ms). Micro ≤200, view/layout ≤500. */
export const MOTION_MS = {
  micro: 150,
  fast: 200,
  view: 300,
  layout: 400,
  max: 500,
} as const;

/** Layout shift distances (px) — transform only, never margin/padding animation. */
export const MOTION_DISTANCE = {
  sm: 4,
  md: 8,
} as const;

/** Micro-interactions: hover, focus, press (100–200ms). */
export const motionMicro =
  "motion-safe:transition-[color,background-color,border-color,opacity,transform,box-shadow] motion-safe:duration-[var(--motion-micro)] motion-safe:ease-out";

/** Crisp press/active feedback for buttons and toggles. */
export const motionPress = `${motionMicro} motion-safe:active:scale-[0.97]`;

/** View transitions: panels, cross-fades, route content (200–500ms). */
export const motionView =
  "motion-safe:transition-[opacity,transform] motion-safe:duration-[var(--motion-view)] motion-safe:ease-[var(--ease-organic)]";

/** Layout chrome: filmstrip expand, pane resize settle. */
export const motionLayout =
  "motion-safe:transition-[opacity,transform,max-height] motion-safe:duration-[var(--motion-layout)] motion-safe:ease-[var(--ease-organic)]";

export const motionFadeIn =
  "motion-safe:animate-[jober-fade-in_var(--motion-view)_var(--ease-organic)_both]";

/** Hero entrance stagger delay (ms) — §18 landing. */
export const HERO_STAGGER_MS = 50;

export function motionHeroStagger(index: number): string {
  if (index <= 0) return motionFadeIn;
  return cn(
    motionFadeIn,
    `motion-safe:[animation-delay:${index * HERO_STAGGER_MS}ms]`,
  );
}

/** Gentle product preview float — marketing hero only. */
export const motionHeroFloat =
  "motion-safe:animate-[jober-hero-float_6s_ease-in-out_infinite]";

export const motionFadeOut =
  "motion-safe:animate-[jober-fade-out_var(--motion-micro)_ease-out_both]";

/** In-progress agent step — single-cycle shimmer, not infinite idle noise. */
export const motionShimmer =
  "motion-safe:animate-[jober-shimmer_2s_ease-in-out_infinite]";

/** New stream line / checkpoint enter. */
export const motionStreamReveal =
  "motion-safe:animate-[jober-stream-reveal_var(--motion-view)_var(--ease-organic)_both]";

/** Status pill state change. */
export const motionStatusEnter =
  "motion-safe:animate-[jober-status-enter_var(--motion-micro)_var(--ease-organic)_both]";

/** Drag release settle — spring overshoot. */
export const motionSpringSettle =
  "motion-safe:animate-[jober-spring-settle_var(--motion-fast)_var(--ease-spring)_both]";

/** Empty-state icon — plays once, does not loop. */
export const motionEmptyPulse =
  "motion-safe:animate-[jober-empty-pulse_3s_ease-in-out_1]";

/** Resize handle affordance. */
export const motionDragHandle = `${motionMicro} cursor-col-resize hover:bg-primary/15 active:bg-primary/25`;

/** Kanban / list card grab affordance. */
export const motionDragItem = `${motionMicro} cursor-grab active:cursor-grabbing motion-safe:active:scale-[1.01] motion-safe:active:shadow-md`;

/** Toast / checkpoint attention enter. */
export const motionAttentionEnter =
  "motion-safe:animate-[jober-attention-enter_var(--motion-view)_var(--ease-organic)_both]";

/** LIVE stream badge — opacity/scale pulse (not shimmer). */
export const motionLivePulse =
  "motion-safe:animate-[jober-live-pulse_2s_ease-in-out_infinite]";

/** Ambient canvas gradient blob drift — decorative; gated by motion-safe. */
export const motionAmbientDrift =
  "motion-safe:animate-[jober-ambient-drift_20s_ease-in-out_infinite]";

/** Unified skeleton loading shimmer. */
export const motionSkeleton =
  "jober-skeleton-shimmer motion-safe:animate-[jober-skeleton-shimmer_2s_ease-in-out_infinite]";

/** Marketing primary CTA / pricing card border accent (21st.dev border-beam pattern). */
export const brandBorderBeam = "brand-border-beam";

/** How-it-works stepper connector gradient flow. */
export const brandStepperConnector = "brand-stepper-connector h-px";

/** Clickable table rows — tokenized hover transition. */
export const motionTableRow = `${motionMicro} transition-colors hover:bg-muted/50`;

export function withMotion(
  base: string,
  opts?: { micro?: boolean; fadeIn?: boolean; press?: boolean },
): string {
  return cn(
    base,
    opts?.micro !== false && motionMicro,
    opts?.press && motionPress,
    opts?.fadeIn && motionFadeIn,
  );
}

/** Run lifecycle status → visual tone for coordinated pill animation. */
export type RunStatusTone = "queued" | "running" | "review" | "submitted" | "failed" | "idle";

export function runStatusTone(status: string): RunStatusTone {
  const normalized = status.toLowerCase();
  if (normalized.includes("queue") || normalized === "new") return "queued";
  if (
    normalized.includes("progress") ||
    normalized.includes("running") ||
    normalized.includes("filling") ||
    normalized.includes("navigat")
  ) {
    return "running";
  }
  if (normalized.includes("review") || normalized.includes("checkpoint") || normalized.includes("human")) {
    return "review";
  }
  if (
    normalized.includes("submit") ||
    normalized.includes("applied") ||
    normalized.includes("complete") ||
    normalized.includes("success")
  ) {
    return "submitted";
  }
  if (normalized.includes("fail") || normalized.includes("error") || normalized.includes("denied")) {
    return "failed";
  }
  return "idle";
}

export const statusToneClasses: Record<RunStatusTone, string> = {
  queued: "border-border/60 bg-muted/50 text-muted-foreground",
  running: "border-primary/30 bg-primary/10 text-primary",
  review: "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-200",
  submitted: "border-emerald-500/35 bg-emerald-500/10 text-emerald-800 dark:text-emerald-200",
  failed: "border-destructive/35 bg-destructive/10 text-destructive",
  idle: "border-border/60 bg-secondary text-secondary-foreground",
};
