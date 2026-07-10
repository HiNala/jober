"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface UnlockFeatureCard {
  id: string;
  title: string;
  description: string;
  icon?: React.ReactNode;
}

export interface UnlockModalProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  title?: string;
  description?: string;
  /** Illustration / art slot above the feature cards. */
  illustration?: React.ReactNode;
  features?: UnlockFeatureCard[];
  ctaLabel?: string;
  onCta?: () => void;
  secondaryLabel?: string;
  onSecondary?: () => void;
  className?: string;
}

const DEFAULT_FEATURES: UnlockFeatureCard[] = [
  {
    id: "priority",
    title: "Priority runs",
    description: "Jump the queue when applications are time-sensitive.",
  },
  {
    id: "limits",
    title: "Higher limits",
    description: "More batches and documents per day without throttling.",
  },
  {
    id: "support",
    title: "Priority support",
    description: "Faster help when a form or ATS needs a human assist.",
  },
];

/**
 * Grok-style unlock dialog: illustration slot, 3 feature cards, primary CTA.
 */
export function UnlockModal({
  open,
  onOpenChange,
  title = "You're unlocked",
  description = "Pro tools are ready — higher limits, priority runs, and faster support.",
  illustration,
  features = DEFAULT_FEATURES,
  ctaLabel = "Continue",
  onCta,
  secondaryLabel,
  onSecondary,
  className,
}: UnlockModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={cn(
          "sm:max-w-md gap-5 overflow-hidden p-0 sm:max-w-lg",
          motionFadeIn,
          className,
        )}
        data-slot="unlock-modal"
      >
        <div className="relative flex min-h-28 items-center justify-center overflow-hidden border-b border-border/50 bg-[radial-gradient(ellipse_80%_70%_at_50%_40%,var(--canvas-ambient-mid),transparent_70%)] px-6 pt-8 pb-4">
          {illustration ?? (
            <div
              className="flex size-16 items-center justify-center rounded-2xl bg-primary/15 text-2xl font-semibold text-primary ring-1 ring-primary/25"
              aria-hidden
            >
              ★
            </div>
          )}
        </div>

        <div className="space-y-4 px-6 pb-2">
          <DialogHeader className="text-center sm:text-center">
            <DialogTitle className="text-xl tracking-tight">{title}</DialogTitle>
            <DialogDescription className="text-balance">{description}</DialogDescription>
          </DialogHeader>

          <ul className="grid gap-2.5 sm:grid-cols-3">
            {features.slice(0, 3).map((feature) => (
              <li
                key={feature.id}
                className="rounded-xl border border-border/60 bg-muted/25 p-3 text-left"
              >
                {feature.icon ? (
                  <div className="mb-2 text-primary" aria-hidden>
                    {feature.icon}
                  </div>
                ) : null}
                <p className="text-sm font-medium leading-snug">{feature.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </li>
            ))}
          </ul>
        </div>

        <DialogFooter className="mx-0 mb-0 rounded-none border-t border-border/50 bg-transparent p-4 sm:justify-center">
          {secondaryLabel ? (
            <Button type="button" variant="ghost" onClick={onSecondary}>
              {secondaryLabel}
            </Button>
          ) : null}
          <Button
            type="button"
            className="min-w-40"
            onClick={() => {
              onCta?.();
              onOpenChange?.(false);
            }}
          >
            {ctaLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
