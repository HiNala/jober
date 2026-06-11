"use client";

import { useEffect, useState } from "react";

import { BatchPreviewDialog } from "@/components/batches/batch-preview-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  fetchDailyPlan,
  pauseAllQueue,
  resumeAllQueue,
  type BatchPolicy,
  type DailyPlan,
} from "@/lib/api/batches";

export function BatchPanel() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewPolicy, setPreviewPolicy] = useState<BatchPolicy>("dry_run");

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchDailyPlan();
        if (!cancelled) setPlan(data);
      } catch {
        if (!cancelled) setPlan(null);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function loadPlan() {
    try {
      setPlan(await fetchDailyPlan());
    } catch {
      setPlan(null);
    }
  }

  function openPreview(policy: BatchPolicy) {
    setPreviewPolicy(policy);
    setPreviewOpen(true);
  }

  const filters = plan?.proposed_filters ?? { priority: "A", status: "new", limit: 50 };

  return (
    <>
      <Card className="border-border/60 bg-card/80">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Batch control</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {plan ? (
            <p className="text-sm text-muted-foreground">{plan.summary}</p>
          ) : (
            <p className="text-sm text-muted-foreground">Loading daily plan…</p>
          )}
          {plan?.pacing_note ? (
            <p className="text-xs text-muted-foreground">{plan.pacing_note}</p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={() => openPreview("dry_run")}>
              Preview dry-run
            </Button>
            <Button size="sm" variant="secondary" onClick={() => openPreview("review_before_submit")}>
              Preview apply batch
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => void pauseAllQueue().then(() => setMessage("Queue paused"))}
            >
              Pause all
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => void resumeAllQueue().then(() => setMessage("Queue resumed"))}
            >
              Resume all
            </Button>
          </div>
          {message ? <p className="text-xs text-muted-foreground">{message}</p> : null}
        </CardContent>
      </Card>

      <BatchPreviewDialog
        open={previewOpen}
        onOpenChange={(open) => {
          setPreviewOpen(open);
          if (!open) {
            void loadPlan();
          }
        }}
        filters={filters}
        batchName={
          previewPolicy === "dry_run" ? "Dashboard dry-run" : "Dashboard apply batch"
        }
        defaultPolicy={previewPolicy}
      />
    </>
  );
}
