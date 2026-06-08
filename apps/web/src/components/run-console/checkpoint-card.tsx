"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Hand } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { resolveRunCheckpoint, type RunConsoleSnapshot } from "@/lib/api/run-console";
import { formatApiError } from "@/lib/api/errors";
import { motionAttentionEnter, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

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
      toast.message(`Checkpoint ${result.action} — run ${result.run_status.replace(/_/g, " ")}`);
      void queryClient.invalidateQueries({ queryKey: ["run-console", runId] });
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  if (!checkpoint) {
    return null;
  }

  const isReview = checkpoint.checkpoint_type === "review_submit";
  const typeLabel = checkpoint.checkpoint_type.replace(/_/g, " ");

  return (
    <section
      className={cn(
        "space-y-3 rounded-lg border border-amber-500/35 bg-amber-500/5 p-4",
        motionAttentionEnter,
      )}
      aria-labelledby="open-checkpoint-heading"
    >
      <div className="flex items-center gap-2">
        <Hand className="size-4 text-amber-600" aria-hidden />
        <h3 id="open-checkpoint-heading" className="text-sm font-semibold">
          Your checkpoint
        </h3>
        <Badge variant="outline">{typeLabel}</Badge>
      </div>
      <p className="text-sm leading-relaxed text-muted-foreground">{checkpoint.prompt}</p>
      <div className="flex flex-wrap gap-2" role="group" aria-label="Checkpoint actions">
        {isReview ? (
          <>
            <Button
              size="sm"
              className={motionPress}
              onClick={() => resolveMutation.mutate("approve")}
              disabled={resolveMutation.isPending}
            >
              Approve submit
            </Button>
            <Button
              size="sm"
              variant="secondary"
              className={motionPress}
              onClick={() => resolveMutation.mutate("edit")}
              disabled={resolveMutation.isPending}
            >
              Edit form
            </Button>
            <Button
              size="sm"
              variant="outline"
              className={motionPress}
              onClick={() => resolveMutation.mutate("skip")}
              disabled={resolveMutation.isPending}
            >
              Skip
            </Button>
            <Button
              size="sm"
              variant="destructive"
              className={motionPress}
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
              className={motionPress}
              onClick={() => resolveMutation.mutate("approve")}
              disabled={resolveMutation.isPending}
            >
              Continue
            </Button>
            <Button
              size="sm"
              variant="outline"
              className={motionPress}
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
