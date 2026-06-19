"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { BatchPreviewDialog } from "@/components/batches/batch-preview-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  fetchDailyPlan,
  pauseAllQueue,
  resumeAllQueue,
  type BatchPolicy,
  type DailyPlan,
} from "@/lib/api/batches";
import { fetchTenantPolicy } from "@/lib/api/settings";

export function BatchPanel() {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewPolicy, setPreviewPolicy] = useState<BatchPolicy>("dry_run");
  const policyQuery = useQuery({
    queryKey: ["tenant-policy"],
    queryFn: fetchTenantPolicy,
  });
  const tenantDefault = (policyQuery.data?.policy.default_run_policy ??
    "review_before_submit") as BatchPolicy;

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchDailyPlan();
        if (!cancelled) {
          setPlan(data);
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          setPlan(null);
          setLoading(false);
        }
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

  const defaultFilters = useMemo(() => ({ priority: "A", status: "new", limit: 50 }), []);
  const filters = plan?.proposed_filters ?? defaultFilters;

  return (
    <>
      <Card className="border-border/60 bg-card/80">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Batch control</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading ? (
            <div className="space-y-2" aria-busy="true">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : (
            <>
              {plan ? (
                <p className="text-sm text-muted-foreground">{plan.summary}</p>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No daily plan available. Check the API connection.
                </p>
              )}
              {plan?.pacing_note ? (
                <p className="text-xs text-muted-foreground">{plan.pacing_note}</p>
              ) : null}
            </>
          )}

          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              data-testid="preview-batch-tenant-default"
              onClick={() => openPreview(tenantDefault)}
            >
              Preview batch
            </Button>
            <Button size="sm" onClick={() => openPreview("dry_run")}>
              Preview dry-run
            </Button>
            <Button size="sm" variant="secondary" onClick={() => openPreview("review_before_submit")}>
              Preview apply batch
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() =>
                void pauseAllQueue().then(() => toast.success("Queue paused"))
              }
            >
              Pause all
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() =>
                void resumeAllQueue().then(() => toast.success("Queue resumed"))
              }
            >
              Resume all
            </Button>
          </div>
        </CardContent>
      </Card>

      <BatchPreviewDialog
        open={previewOpen}
        onOpenChange={(open) => {
          setPreviewOpen(open);
          if (!open) void loadPlan();
        }}
        filters={filters}
        batchName={previewPolicy === "dry_run" ? "Dashboard dry-run" : "Dashboard apply batch"}
        defaultPolicy={previewPolicy}
      />
    </>
  );
}
