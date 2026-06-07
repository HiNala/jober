/**
 * Jober design tokens — single source for spacing, motion, shadow, and copy terms.
 * CSS variables live in `globals.css`; this module documents runtime/class usage.
 */

export const spacing = {
  page: "p-4 md:p-6",
  section: "space-y-6",
  card: "p-4",
  stack: "space-y-3",
} as const;

export const shadow = {
  surface: "shadow-sm",
  elevated: "shadow-md",
  none: "shadow-none",
} as const;

export const radius = {
  card: "rounded-lg",
  control: "rounded-md",
  pill: "rounded-full",
} as const;

export const surface = {
  card: "border border-border/60 bg-card/80",
  muted: "bg-muted/30",
  inset: "bg-muted/20",
  terminal: "bg-[var(--terminal-bg)] text-[var(--terminal-fg)]",
} as const;

/** Consistent product terminology (Mission 16 copy pass). */
export const terms = {
  run: "run",
  attempt: "attempt",
  checkpoint: "checkpoint",
  batch: "batch",
} as const;
