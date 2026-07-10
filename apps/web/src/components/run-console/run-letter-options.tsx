"use client";

import { useMutation } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { patchRunOptions, type RunConsoleSnapshot } from "@/lib/api/run-console";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const TERMINAL_STATUSES = new Set([
  "succeeded",
  "failed_final",
  "failed_retryable",
  "skipped",
  "applied",
]);

export function RunLetterOptions({
  runId,
  snapshot,
}: {
  runId: string;
  snapshot: RunConsoleSnapshot;
}) {
  const serverOverride = snapshot.run_options?.generate_cover_letter ?? null;
  const [override, setOverride] = useState<boolean | null>(serverOverride);
  const canEdit = !TERMINAL_STATUSES.has(snapshot.status);

  useEffect(() => {
    setOverride(serverOverride);
  }, [serverOverride, runId]);

  const mutation = useMutation({
    mutationFn: (generate: boolean | null) => patchRunOptions(runId, generate),
    onMutate: (generate) => {
      setOverride(generate);
    },
    onSuccess: () => {
      toast.success("Run letter preference updated");
    },
    onError: (_err, _vars, _ctx) => {
      setOverride(serverOverride);
      toast.error("Could not update run letter preference");
    },
  });

  if (!canEdit && override === null) return null;

  return (
    <section className={cn(surface.workspace, "rounded-lg p-3")} aria-label="Cover letter for this run">
      <div className="flex items-start gap-2">
        <FileText className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
        <div className="space-y-2 text-sm">
          <p className="font-medium">Cover letter for this run</p>
          <p className="text-xs text-muted-foreground">
            {override === null
              ? "Using your Settings default."
              : override
                ? "Will generate a letter when the form has a cover-letter field."
                : "Skipped for this run — resume only."}
          </p>
          {canEdit ? (
            <div className="flex flex-wrap gap-2">
              <label className="flex items-center gap-1.5 text-xs">
                <input
                  type="radio"
                  name={`letter-${runId}`}
                  checked={override === null}
                  onChange={() => mutation.mutate(null)}
                  disabled={mutation.isPending}
                />
                Default
              </label>
              <label className="flex items-center gap-1.5 text-xs">
                <input
                  type="radio"
                  name={`letter-${runId}`}
                  checked={override === true}
                  onChange={() => mutation.mutate(true)}
                  disabled={mutation.isPending}
                />
                Generate
              </label>
              <label className="flex items-center gap-1.5 text-xs">
                <input
                  type="radio"
                  name={`letter-${runId}`}
                  checked={override === false}
                  onChange={() => mutation.mutate(false)}
                  disabled={mutation.isPending}
                />
                Skip
              </label>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
