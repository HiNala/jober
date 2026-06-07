"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  createBatch,
  enqueueBatch,
  fetchDailyPlan,
  pauseAllQueue,
  previewBatch,
  resumeAllQueue,
  type DailyPlan,
} from "@/lib/api/batches";

export function BatchPanel() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadPlan = useCallback(async () => {
    try {
      setPlan(await fetchDailyPlan());
    } catch {
      setPlan(null);
    }
  }, []);

  useEffect(() => {
    void loadPlan();
  }, [loadPlan]);

  async function startDryRunBatch() {
    setBusy(true);
    setMessage(null);
    try {
      const filters = plan?.proposed_filters ?? { priority: "A", status: "new", limit: 50 };
      await previewBatch(filters);
      const batch = (await createBatch({
        name: "Dashboard dry-run",
        policy: "dry_run",
        filters,
      })) as { id: string };
      await enqueueBatch(batch.id);
      setMessage("Batch enqueued (dry_run). Watch live activity below.");
      await loadPlan();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Batch failed");
    } finally {
      setBusy(false);
    }
  }

  return (
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
          <Button size="sm" disabled={busy} onClick={() => void startDryRunBatch()}>
            Start dry-run batch
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={busy}
            onClick={() => void pauseAllQueue().then(() => setMessage("Queue paused"))}
          >
            Pause all
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={busy}
            onClick={() => void resumeAllQueue().then(() => setMessage("Queue resumed"))}
          >
            Resume all
          </Button>
        </div>
        {message ? <p className="text-xs text-muted-foreground">{message}</p> : null}
      </CardContent>
    </Card>
  );
}
