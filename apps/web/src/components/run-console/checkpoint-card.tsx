"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { resolveRunCheckpoint, type RunConsoleSnapshot } from "@/lib/api/run-console";
import { formatApiError } from "@/lib/api/errors";

export interface CheckpointCardProps {
  runId: string;
  snapshot: RunConsoleSnapshot;
}

export function CheckpointCard({ runId, snapshot }: CheckpointCardProps) {
  const checkpoint = snapshot.open_checkpoint;
  const queryClient = useQueryClient();

  const resolveMutation = useMutation({
    mutationFn: (action: "approve" | "deny" | "edit" | "skip") =>
      resolveRunCheckpoint(runId, checkpoint!.id, action),
    onSuccess: (result) => {
      toast.message(`Checkpoint ${result.action} — run ${result.run_status}`);
      void queryClient.invalidateQueries({ queryKey: ["run-console", runId] });
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  if (!checkpoint) {
    return null;
  }

  const isReview = checkpoint.checkpoint_type === "review_submit";

  return (
    <section className="space-y-3 rounded-lg border border-amber-500/40 bg-amber-500/5 p-4">
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-semibold">Human checkpoint</h3>
        <Badge variant="outline">{checkpoint.checkpoint_type.replace(/_/g, " ")}</Badge>
      </div>
      <p className="text-sm text-muted-foreground">{checkpoint.prompt}</p>
      <div className="flex flex-wrap gap-2">
        {isReview ? (
          <>
            <Button
              size="sm"
              onClick={() => resolveMutation.mutate("approve")}
              disabled={resolveMutation.isPending}
            >
              Approve
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => resolveMutation.mutate("edit")}
              disabled={resolveMutation.isPending}
            >
              Edit
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => resolveMutation.mutate("skip")}
              disabled={resolveMutation.isPending}
            >
              Skip
            </Button>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => resolveMutation.mutate("deny")}
              disabled={resolveMutation.isPending}
            >
              Deny
            </Button>
          </>
        ) : (
          <>
            <Button
              size="sm"
              onClick={() => resolveMutation.mutate("approve")}
              disabled={resolveMutation.isPending}
            >
              Continue
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => resolveMutation.mutate("skip")}
              disabled={resolveMutation.isPending}
            >
              Skip
            </Button>
          </>
        )}
      </div>
    </section>
  );
}
