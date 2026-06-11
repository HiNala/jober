"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, Hand } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { resolveRunCheckpoint, type RunConsoleSnapshot } from "@/lib/api/run-console";
import { ApiError } from "@/lib/api/client";
import { formatApiError } from "@/lib/api/errors";
import { motionAttentionEnter, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface CheckpointCardProps {
  runId: string;
  snapshot: RunConsoleSnapshot;
  onResolved?: () => void;
}

const VALUE_CHECKPOINT_TYPES = new Set([
  "captcha",
  "sensitive_field",
  "manual_intervention",
  "two_factor",
]);

export function CheckpointCard({ runId, snapshot, onResolved }: CheckpointCardProps) {
  const checkpoint = snapshot.open_checkpoint;
  const queryClient = useQueryClient();
  const [gateValue, setGateValue] = useState("");
  const [conflict, setConflict] = useState(false);

  const resolveMutation = useMutation({
    mutationFn: (params: { action: "approve" | "deny" | "edit" | "skip"; value?: string }) =>
      resolveRunCheckpoint(runId, checkpoint!.id, params.action, params.value),
    onSuccess: (result) => {
      setConflict(false);
      toast.message(`Checkpoint ${result.action} — run ${result.run_status.replace(/_/g, " ")}`);
      void queryClient.invalidateQueries({ queryKey: ["run-console", runId] });
      onResolved?.();
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError && err.status === 422) {
        const detail = err.body ?? "";
        if (detail.includes("already resolved")) {
          setConflict(true);
          return;
        }
      }
      toast.error(formatApiError(err));
    },
  });

  if (!checkpoint) {
    return null;
  }

  if (conflict) {
    return (
      <section
        className={cn(
          "space-y-3 rounded-lg border border-border/60 bg-muted/30 p-4",
          motionAttentionEnter,
        )}
        aria-labelledby="checkpoint-conflict-heading"
      >
        <div className="flex items-center gap-2">
          <AlertCircle className="size-4 text-muted-foreground" aria-hidden />
          <h3 id="checkpoint-conflict-heading" className="text-sm font-semibold">
            Checkpoint already resolved
          </h3>
        </div>
        <p className="text-sm text-muted-foreground">
          This checkpoint was handled in another session. Sync the run console to see the latest
          state.
        </p>
        <Button
          size="sm"
          variant="outline"
          className={motionPress}
          onClick={() => {
            setConflict(false);
            onResolved?.();
          }}
        >
          Sync console
        </Button>
      </section>
    );
  }

  const isReview = checkpoint.checkpoint_type === "review_submit";
  const needsValue = VALUE_CHECKPOINT_TYPES.has(checkpoint.checkpoint_type);
  const typeLabel = checkpoint.checkpoint_type.replace(/_/g, " ");

  const approve = () => {
    resolveMutation.mutate({
      action: "approve",
      value: needsValue && gateValue.trim() ? gateValue.trim() : undefined,
    });
  };

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
      {needsValue ? (
        <div className="space-y-1">
          <label htmlFor="checkpoint-gate-value" className="text-xs font-medium text-muted-foreground">
            Response value
          </label>
          <Input
            id="checkpoint-gate-value"
            value={gateValue}
            onChange={(event) => setGateValue(event.target.value)}
            placeholder="Enter code or value to continue"
            disabled={resolveMutation.isPending}
          />
        </div>
      ) : null}
      <div className="flex flex-wrap gap-2" role="group" aria-label="Checkpoint actions">
        {isReview ? (
          <>
            <Button
              size="sm"
              className={motionPress}
              onClick={() => resolveMutation.mutate({ action: "approve" })}
              disabled={resolveMutation.isPending}
            >
              Approve submit
            </Button>
            <Button
              size="sm"
              variant="secondary"
              className={motionPress}
              onClick={() => resolveMutation.mutate({ action: "edit" })}
              disabled={resolveMutation.isPending}
            >
              Edit form
            </Button>
            <Button
              size="sm"
              variant="outline"
              className={motionPress}
              onClick={() => resolveMutation.mutate({ action: "skip" })}
              disabled={resolveMutation.isPending}
            >
              Skip
            </Button>
            <Button
              size="sm"
              variant="destructive"
              className={motionPress}
              onClick={() => resolveMutation.mutate({ action: "deny" })}
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
              onClick={approve}
              disabled={resolveMutation.isPending || (needsValue && !gateValue.trim())}
            >
              Continue
            </Button>
            <Button
              size="sm"
              variant="outline"
              className={motionPress}
              onClick={() => resolveMutation.mutate({ action: "skip" })}
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
