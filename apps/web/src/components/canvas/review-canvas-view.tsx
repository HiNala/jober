"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, CircleAlert } from "lucide-react";
import { toast } from "sonner";

import { PageEmpty, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { formatApiError } from "@/lib/api/errors";
import { resolveRunCheckpoint } from "@/lib/api/run-console";
import {
  fetchReviewPackageByRun,
  skipApplicationSubmit,
  submitApplicationRun,
} from "@/lib/api/verification";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function ReviewCanvasView() {
  const runCanvas = useRunCanvas();
  const runId = runCanvas?.runId;
  const queryClient = useQueryClient();

  const reviewQuery = useQuery({
    queryKey: ["review-package-run", runId],
    queryFn: () => fetchReviewPackageByRun(runId!),
    enabled: Boolean(runId),
    retry: false,
  });

  const submitMutation = useMutation({
    mutationFn: () => submitApplicationRun(runId!),
    onSuccess: () => {
      toast.success("Application submitted");
      void queryClient.invalidateQueries({ queryKey: ["review-package-run", runId] });
      void runCanvas?.reconnect();
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  const skipMutation = useMutation({
    mutationFn: () => skipApplicationSubmit(runId!),
    onSuccess: () => {
      toast.message("Submit skipped");
      void runCanvas?.reconnect();
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  const checkpointMutation = useMutation({
    mutationFn: (action: "approve" | "deny" | "edit" | "skip") => {
      const checkpointId = runCanvas?.snapshot?.open_checkpoint?.id;
      if (!checkpointId || !runId) {
        throw new Error("No open checkpoint");
      }
      return resolveRunCheckpoint(runId, checkpointId, action);
    },
    onSuccess: () => {
      toast.message("Checkpoint resolved");
      void runCanvas?.reconnect();
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  if (!runId) {
    return (
      <PageEmpty
        title="No review pending"
        description="Review surfaces appear when a run reaches review and submit."
      />
    );
  }

  if (reviewQuery.isLoading) {
    return <PageLoading label="Loading review package…" />;
  }

  const review = reviewQuery.data;
  const screenshotUrl = runCanvas?.displayScreenshotUrl;

  if (!review && !runCanvas?.isReviewState) {
    return (
      <PageEmpty
        title="Not at review yet"
        description="Complete verification first. This canvas will show letter, fill diff, and readiness together."
      />
    );
  }

  const ready = review?.readiness.passed ?? false;

  return (
    <div className={cn("grid h-full gap-3 overflow-auto p-3 lg:grid-cols-2", motionFadeIn)}>
      <figure className={cn("overflow-hidden rounded-lg", surface.card)}>
        {screenshotUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={screenshotUrl}
            alt="Final form screenshot before submit"
            className="aspect-video w-full bg-[var(--terminal-bg)] object-contain"
          />
        ) : (
          <figcaption className="flex aspect-video items-center justify-center text-sm text-muted-foreground">
            No screenshot yet
          </figcaption>
        )}
      </figure>

      <div className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={ready ? "secondary" : "destructive"}>
            {review?.status.replace(/_/g, " ") ?? "review"}
          </Badge>
          <Button
            size="sm"
            onClick={() => submitMutation.mutate()}
            disabled={submitMutation.isPending || !ready || !review}
          >
            Submit application
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => skipMutation.mutate()}
            disabled={skipMutation.isPending}
          >
            Skip
          </Button>
          {runCanvas?.snapshot?.open_checkpoint ? (
            <>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => checkpointMutation.mutate("approve")}
                disabled={checkpointMutation.isPending}
              >
                Approve checkpoint
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => checkpointMutation.mutate("edit")}
                disabled={checkpointMutation.isPending}
              >
                Edit
              </Button>
            </>
          ) : null}
        </div>

        <p className="text-sm text-muted-foreground">{review?.human_summary}</p>

        {review?.cover_letter_preview ? (
          <div className={cn("rounded-lg p-3 text-sm", surface.card)}>
            <p className="mb-1 font-medium">Cover letter</p>
            <p className="line-clamp-6 whitespace-pre-wrap text-muted-foreground">
              {review.cover_letter_preview}
            </p>
          </div>
        ) : null}

        {review?.readiness ? (
          <ul className="space-y-1 text-sm">
            {review.readiness.checks.map((check) => (
              <li key={check.check_id} className="flex items-start gap-2">
                {check.passed ? (
                  <CheckCircle2 className="mt-0.5 size-4 text-emerald-600" aria-hidden />
                ) : (
                  <CircleAlert className="mt-0.5 size-4 text-rose-600" aria-hidden />
                )}
                <span>{check.reason}</span>
              </li>
            ))}
          </ul>
        ) : null}

        {review && review.fill_diffs.length > 0 ? (
          <div className="overflow-x-auto rounded-md border">
            <Table>
              <caption className="sr-only">Fill diff for review</caption>
              <TableHeader>
                <TableRow>
                  <TableHead scope="col">Field</TableHead>
                  <TableHead scope="col">Proposed</TableHead>
                  <TableHead scope="col">Actual</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {review.fill_diffs.slice(0, 8).map((row) => (
                  <TableRow key={row.field_key}>
                    <TableCell>{row.label ?? row.field_key}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {row.proposed_redacted ?? "—"}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {row.actual_redacted ?? "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : null}
      </div>
    </div>
  );
}
