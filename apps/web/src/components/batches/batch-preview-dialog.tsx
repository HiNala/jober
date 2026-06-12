"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  createBatch,
  enqueueBatch,
  previewBatch,
  type BatchPolicy,
  type BatchPreviewResult,
} from "@/lib/api/batches";
import { formatBatchExclusionReason } from "@/lib/jobs/status-vocabulary";
import { cn } from "@/lib/utils";

const POLICY_COPY: Record<BatchPolicy, { title: string; detail: string }> = {
  dry_run: {
    title: "Dry run",
    detail: "Fills forms and stops before submit — no application sent.",
  },
  review_before_submit: {
    title: "Review before submit",
    detail: "Pauses at review-and-submit for your approval on each job.",
  },
};

export type BatchPreviewDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  filters: Record<string, unknown>;
  batchName: string;
  defaultPolicy?: BatchPolicy;
  onEnqueued?: (includedCount: number) => void;
};

function BatchPreviewBody({
  filters,
  batchName,
  defaultPolicy,
  onClose,
  onEnqueued,
}: {
  filters: Record<string, unknown>;
  batchName: string;
  defaultPolicy: BatchPolicy;
  onClose: () => void;
  onEnqueued?: (includedCount: number) => void;
}) {
  const [preview, setPreview] = useState<BatchPreviewResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [policy, setPolicy] = useState<BatchPolicy>(defaultPolicy);
  const onCloseRef = useRef(onClose);
  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      try {
        const data = await previewBatch(filters);
        if (!cancelled) {
          setPreview(data);
        }
      } catch (err) {
        if (!cancelled) {
          toast.error(err instanceof Error ? err.message : "Could not preview batch");
          onCloseRef.current();
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [filters]);

  const included = preview?.included ?? [];
  const excluded = preview?.excluded ?? [];

  async function confirmEnqueue() {
    if (included.length === 0) {
      toast.error("No runnable jobs in this preview");
      return;
    }
    setBusy(true);
    try {
      const batch = (await createBatch({
        name: batchName,
        policy,
        filters,
      })) as { id: string };
      await enqueueBatch(batch.id);
      toast.success(
        `Queued ${included.length} job${included.length === 1 ? "" : "s"} (${POLICY_COPY[policy].title})`,
      );
      onEnqueued?.(included.length);
      onClose();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Could not enqueue batch");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading preview…</p>;
  }

  if (!preview) {
    return null;
  }

  return (
    <>
      <div className="space-y-4 text-sm">
        <div className="flex flex-wrap gap-3 text-muted-foreground">
          <span>
            <strong className="text-foreground">{included.length}</strong> runnable
          </span>
          <span>·</span>
          <span>
            <strong className="text-foreground">{excluded.length}</strong> excluded
          </span>
          <span>·</span>
          <span>
            ~${preview.estimated_cost_usd.toFixed(2)} est. · {preview.domain_count} domain
            {preview.domain_count === 1 ? "" : "s"}
          </span>
        </div>

        {included.length > 0 ? (
          <section aria-labelledby="batch-included-heading">
            <h3 id="batch-included-heading" className="mb-1 font-medium">
              Included
            </h3>
            <ul className="max-h-32 space-y-0.5 overflow-y-auto rounded-md border p-2 text-xs">
              {included.slice(0, 12).map((row) => (
                <li key={row.job_target_id}>
                  {row.company} — {row.role}
                  {row.priority ? ` · ${row.priority}` : ""}
                </li>
              ))}
              {included.length > 12 ? (
                <li className="text-muted-foreground">+{included.length - 12} more</li>
              ) : null}
            </ul>
          </section>
        ) : null}

        {excluded.length > 0 ? (
          <section aria-labelledby="batch-excluded-heading">
            <h3 id="batch-excluded-heading" className="mb-1 font-medium">
              Excluded
            </h3>
            <ul className="max-h-32 space-y-1 overflow-y-auto rounded-md border border-amber-500/25 bg-amber-500/5 p-2 text-xs">
              {excluded.slice(0, 10).map((row) => (
                <li key={`${row.job_target_id}-${row.reason ?? "x"}`}>
                  <span className="font-medium">
                    {row.company} — {row.role}
                  </span>
                  <span className="text-muted-foreground">
                    {" "}
                    — {formatBatchExclusionReason(row.reason ?? "unknown")}
                  </span>
                </li>
              ))}
              {excluded.length > 10 ? (
                <li className="text-muted-foreground">+{excluded.length - 10} more</li>
              ) : null}
            </ul>
          </section>
        ) : null}

        <fieldset className="space-y-2">
          <legend className="text-sm font-medium">Run policy</legend>
          {(["dry_run", "review_before_submit"] as const).map((value) => (
            <label
              key={value}
              className={cn(
                "flex cursor-pointer gap-2 rounded-lg border p-3",
                policy === value ? "border-primary/50 bg-primary/5" : "border-border/60",
              )}
            >
              <input
                type="radio"
                name="batch-policy"
                value={value}
                checked={policy === value}
                onChange={() => setPolicy(value)}
                className="mt-0.5"
              />
              <span>
                <span className="font-medium">{POLICY_COPY[value].title}</span>
                <span className="mt-0.5 block text-xs text-muted-foreground">
                  {POLICY_COPY[value].detail}
                </span>
              </span>
            </label>
          ))}
          <p className="text-xs text-muted-foreground">
            Auto-submit is opt-in only — enable under Settings → Application defaults. It never runs
            from this dialog unless you have opted in there.
          </p>
        </fieldset>
      </div>

      <DialogFooter className="gap-2 sm:gap-0">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button
          type="button"
          data-testid="batch-enqueue"
          disabled={busy || included.length === 0}
          onClick={() => void confirmEnqueue()}
        >
          Enqueue batch
        </Button>
      </DialogFooter>
    </>
  );
}

export function BatchPreviewDialog({
  open,
  onOpenChange,
  filters,
  batchName,
  defaultPolicy = "review_before_submit",
  onEnqueued,
}: BatchPreviewDialogProps) {
  const filterKey = JSON.stringify(filters);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-h-[min(90vh,640px)] max-w-lg overflow-y-auto"
        data-testid="batch-preview-dialog"
      >
        <DialogHeader>
          <DialogTitle>Batch preview</DialogTitle>
          <DialogDescription>
            Included jobs will run with pacing and quiet-hour rules. Excluded jobs stay in your queue
            — fix URLs or status, then preview again.
          </DialogDescription>
        </DialogHeader>

        {open ? (
          <BatchPreviewBody
            key={filterKey + defaultPolicy}
            filters={filters}
            batchName={batchName}
            defaultPolicy={defaultPolicy}
            onClose={() => onOpenChange(false)}
            onEnqueued={onEnqueued}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
