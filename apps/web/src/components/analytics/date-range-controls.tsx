"use client";

import type { AnalyticsRangePreset } from "@/lib/api/analytics-dashboard";
import { cn } from "@/lib/utils";

const PRESETS: { id: AnalyticsRangePreset; label: string }[] = [
  { id: "7d", label: "7d" },
  { id: "30d", label: "30d" },
  { id: "90d", label: "90d" },
];

export function DateRangeControls({
  preset,
  onPresetChange,
  comparePrevious,
  onComparePreviousChange,
  exportHref,
}: {
  preset: AnalyticsRangePreset;
  onPresetChange: (preset: AnalyticsRangePreset) => void;
  comparePrevious: boolean;
  onComparePreviousChange: (value: boolean) => void;
  exportHref?: string;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex rounded-md border border-border/60 p-0.5" role="group" aria-label="Date range">
        {PRESETS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={cn(
              "rounded px-2.5 py-1 text-xs",
              preset === item.id
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
            onClick={() => onPresetChange(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <input
          type="checkbox"
          checked={comparePrevious}
          onChange={(event) => onComparePreviousChange(event.target.checked)}
        />
        Compare to previous period
      </label>
      {exportHref ? (
        <a
          href={exportHref}
          className="text-xs text-primary underline-offset-4 hover:underline"
          download
        >
          Export CSV
        </a>
      ) : null}
    </div>
  );
}
