"use client";

import { buttonVariants } from "@/components/ui/button";
import type { CanvasSurface } from "@/stores/workspace-store";
import { motionMicro, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const SURFACES: { id: CanvasSurface; label: string }[] = [
  { id: "browser", label: "Browser" },
  { id: "document", label: "Document" },
  { id: "fill-diff", label: "Fill diff" },
  { id: "review", label: "Review" },
];

export function CanvasSurfaceTabs({
  value,
  onChange,
  showReview,
}: {
  value: CanvasSurface;
  onChange: (surface: CanvasSurface) => void;
  showReview?: boolean;
}) {
  const tabs = showReview ? SURFACES : SURFACES.filter((s) => s.id !== "review");

  return (
    <div className="inline-flex rounded-md border bg-muted/30 p-0.5" role="tablist" aria-label="Canvas surface">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={value === tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            buttonVariants({ variant: value === tab.id ? "secondary" : "ghost", size: "xs" }),
            motionMicro,
            motionPress,
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
