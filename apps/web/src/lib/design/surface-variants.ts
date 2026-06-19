import { cva, type VariantProps } from "class-variance-authority";

/**
 * Three deliberate surface families — Mission 10 component tiering.
 * marketing: expressive bento / funnel surfaces
 * workspace: dense data panels and tables
 * terminal: mono live-stream / run console
 */
export const surfaceVariants = cva("", {
  variants: {
    family: {
      marketing:
        "rounded-2xl border border-slate-200 bg-white shadow-md",
      workspace: "rounded-xl border border-border/70 bg-card shadow-sm",
      terminal:
        "rounded-lg border border-border/40 bg-[var(--terminal-bg)] font-mono text-xs text-[var(--terminal-fg)] shadow-[inset_0_1px_0_0_oklch(1_0_0/6%)]",
    },
    padding: {
      none: "",
      sm: "p-3",
      md: "p-4",
      lg: "p-6",
    },
  },
  defaultVariants: {
    family: "workspace",
    padding: "none",
  },
});

export type SurfaceFamily = NonNullable<VariantProps<typeof surfaceVariants>["family"]>;
export type SurfacePadding = NonNullable<VariantProps<typeof surfaceVariants>["padding"]>;

/** Pre-resolved class strings for `cn()` composition without the Surface component. */
export const surfaceFamilyClasses = {
  marketing: surfaceVariants({ family: "marketing" }),
  workspace: surfaceVariants({ family: "workspace" }),
  terminal: surfaceVariants({ family: "terminal" }),
} as const;
