"use client";

import { useState } from "react";

import { downloadAnalyticsCsv } from "@/lib/api/analytics-dashboard";
import { cn } from "@/lib/utils";

export function ExportCsvButton({
  path,
  range,
  filename,
  label = "Export CSV",
  className,
}: {
  path: string;
  range: { start: string; end: string };
  filename: string;
  label?: string;
  className?: string;
}) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <span className={cn("inline-flex flex-col items-start gap-1", className)}>
      <button
        type="button"
        className="text-xs text-primary underline-offset-4 hover:underline disabled:opacity-50"
        disabled={pending}
        onClick={() => {
          setError(null);
          setPending(true);
          void downloadAnalyticsCsv(path, range, filename)
            .catch((err: unknown) => {
              setError(err instanceof Error ? err.message : "Export failed");
            })
            .finally(() => setPending(false));
        }}
      >
        {pending ? "Exporting…" : label}
      </button>
      {error ? <span className="text-xs text-destructive">{error}</span> : null}
    </span>
  );
}
