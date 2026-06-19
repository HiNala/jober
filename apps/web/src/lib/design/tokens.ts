/**
 * Jober design tokens — single source for spacing, motion, shadow, and copy terms.
 * CSS variables live in `globals.css`; this module documents runtime/class usage.
 */

import { surfaceFamilyClasses } from "@/lib/design/surface-variants";

export const spacing = {
  page: "p-5 md:p-7",
  section: "space-y-6",
  card: "p-5",
  stack: "space-y-4",
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

/** Surface family class strings — see `surface-variants.ts` and `components/ui/surface.tsx`. */
export const surface = {
  marketing: surfaceFamilyClasses.marketing,
  workspace: surfaceFamilyClasses.workspace,
  terminal: surfaceFamilyClasses.terminal,
  /** @deprecated Use `surface.workspace` or `surface.marketing`. */
  card: surfaceFamilyClasses.workspace,
  muted: "bg-muted/30",
  inset: "bg-muted/20",
  terminalMuted: "text-[var(--terminal-muted)]",
  terminalMedia: "bg-[var(--terminal-bg)]",
} as const;

/** Consistent product terminology (Mission 16 copy pass). */
export const terms = {
  run: "run",
  attempt: "attempt",
  checkpoint: "checkpoint",
  batch: "batch",
} as const;
