import Link from "next/link";

import { motionMicro, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface SuggestionChip {
  id: string;
  label: string;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export interface SuggestionChipsProps {
  chips: SuggestionChip[];
  className?: string;
  /** Accessible name for the chip group. */
  label?: string;
}

/**
 * Row of chip buttons for empty-state quick starts (Grok / Hyperagent style).
 */
export function SuggestionChips({
  chips,
  className,
  label = "Suggestions",
}: SuggestionChipsProps) {
  return (
    <div
      className={cn("flex flex-wrap items-center justify-center gap-2", className)}
      role="group"
      aria-label={label}
      data-slot="suggestion-chips"
    >
      {chips.map((chip) => {
        const classes = cn(
          "inline-flex h-8 items-center rounded-full border border-border/70 bg-card/60 px-3.5 text-sm text-foreground/90",
          "hover:border-primary/35 hover:bg-primary/8 hover:text-foreground",
          "focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
          "disabled:pointer-events-none disabled:opacity-50",
          motionMicro,
          motionPress,
        );

        if (chip.href && !chip.disabled) {
          return (
            <Link key={chip.id} href={chip.href} className={classes}>
              {chip.label}
            </Link>
          );
        }

        return (
          <button
            key={chip.id}
            type="button"
            className={classes}
            onClick={chip.onClick}
            disabled={chip.disabled}
          >
            {chip.label}
          </button>
        );
      })}
    </div>
  );
}
