"use client";

import { useEffect, useState, useSyncExternalStore } from "react";

import { motionFadeIn, motionStreamReveal, statusToneClasses } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const DEMO_LINES = [
  "[09:14:02] run.start — Staff engineer @ Northwind Labs",
  "[09:14:18] field.filled — work_authorization",
  "[09:14:31] field.filled — resume_upload",
  "[09:14:44] checkpoint.human_required — Review letter before submit",
  "[09:14:52] run.paused — Awaiting your approval",
] as const;

function subscribeReducedMotion(onStoreChange: () => void) {
  const media = window.matchMedia("(prefers-reduced-motion: reduce)");
  media.addEventListener("change", onStoreChange);
  return () => media.removeEventListener("change", onStoreChange);
}

function getReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function ProductVisual({ className }: { className?: string }) {
  const [animatedLines, setAnimatedLines] = useState(1);
  const reducedMotion = useSyncExternalStore(subscribeReducedMotion, getReducedMotion, () => true);
  const visibleLines = reducedMotion ? DEMO_LINES.length : animatedLines;

  useEffect(() => {
    if (reducedMotion || animatedLines >= DEMO_LINES.length) return;
    const timer = window.setTimeout(() => {
      setAnimatedLines((count) => Math.min(count + 1, DEMO_LINES.length));
    }, 1200);
    return () => window.clearTimeout(timer);
  }, [animatedLines, reducedMotion]);

  return (
    <div
      className={cn(
        "relative mx-auto w-full max-w-xl rounded-xl border border-border/70 bg-card/80 p-4 shadow-md backdrop-blur-sm",
        motionFadeIn,
        className,
      )}
      aria-hidden
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-destructive/80" />
          <span className="size-2 rounded-full bg-amber-400/80" />
          <span className="size-2 rounded-full bg-emerald-500/80" />
        </div>
        <span
          className={cn(
            "rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide",
            statusToneClasses.review,
          )}
        >
          Awaiting your review
        </span>
      </div>

      <div className="grid gap-3 md:grid-cols-[1fr_1.1fr]">
        <div className="space-y-2 rounded-lg border border-border/50 bg-muted/20 p-3">
          <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            Application preview
          </p>
          <div className="space-y-2">
            <div className="h-2 w-3/4 rounded bg-muted" />
            <div className="h-2 w-full rounded bg-muted" />
            <div className="h-8 rounded border border-dashed border-primary/30 bg-primary/5" />
            <div className="h-2 w-5/6 rounded bg-muted" />
          </div>
        </div>

        <div
          className={cn(
            "min-h-[148px] rounded-lg border p-3 font-mono text-[10px] leading-relaxed",
            surface.terminal,
          )}
        >
          <p className="mb-2 text-[10px] font-medium text-muted-foreground">Event stream</p>
          <ul className="space-y-1">
            {DEMO_LINES.slice(0, visibleLines).map((line) => (
              <li key={line} className={motionStreamReveal}>
                {line}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
