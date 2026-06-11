"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { CheckCircle2, CircleAlert, FileText, SkipForward } from "lucide-react";
import { useMemo } from "react";
import { toast } from "sonner";

import { PageEmpty } from "@/components/states/page-states";
import { Skeleton } from "@/components/ui/skeleton";
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
import {
  fetchReviewPackage,
  skipApplicationSubmit,
  submitApplicationRun,
  type ReviewPackage,
} from "@/lib/api/verification";
import { formatApiError } from "@/lib/api/errors";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export interface ReviewSubmitPanelProps {
  jobTargetId: string;
  onEditField?: (fieldKey: string) => void;
}

function ReadinessChecks({ readiness }: { readiness: ReviewPackage["readiness"] }) {
  return (
    <ul className="space-y-2 text-sm">
      {readiness.checks.map((check) => (
        <li key={check.check_id} className="flex items-start gap-2">
          {check.passed ? (
            <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-600" aria-hidden />
          ) : (
            <CircleAlert className="mt-0.5 size-4 shrink-0 text-rose-600" aria-hidden />
          )}
          <span>
            <span className="font-medium">{check.check_id.replace(/_/g, " ")}</span>
            {" — "}
            {check.reason}
          </span>
        </li>
      ))}
    </ul>
  );
}

export function ReviewSubmitPanel({ jobTargetId, onEditField }: ReviewSubmitPanelProps) {
  const queryClient = useQueryClient();
  const queryKey = useMemo(() => ["review-package", jobTargetId], [jobTargetId]);

  const reviewQuery = useQuery({
    queryKey,
    queryFn: () => fetchReviewPackage(jobTargetId),
    retry: false,
  });

  const submitMutation = useMutation({
    mutationFn: (runId: string) => submitApplicationRun(runId),
    onSuccess: (result) => {
      toast.success(
        result.outcome === "success"
          ? "Application submitted"
          : `Submission outcome: ${result.outcome}`,
      );
      void queryClient.invalidateQueries({ queryKey });
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  const skipMutation = useMutation({
    mutationFn: (runId: string) => skipApplicationSubmit(runId),
    onSuccess: () => {
      toast.message("Submit skipped — run remains in review");
      void queryClient.invalidateQueries({ queryKey });
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  const review = reviewQuery.data;

  if (reviewQuery.isLoading) {
    return (
      <div className="space-y-3" aria-busy="true">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!review) {
    return (
      <PageEmpty
        title="No run awaiting review"
        description="Complete form fill and readiness checks first. A run will appear here when it reaches review and submit."
      />
    );
  }

  const ready = review.readiness.passed;

  return (
    <section
      className={cn("space-y-4 rounded-lg p-4", surface.workspace, motionFadeIn)}
      aria-labelledby="review-submit-heading"
    >
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border/60 pb-4">
        <div>
          <h3 id="review-submit-heading" className="text-base font-semibold">
            {ready ? "Ready to submit" : "Review required before submit"}
          </h3>
          <p className="mt-1 max-w-prose text-sm text-muted-foreground">
            {review.human_summary}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={ready ? "secondary" : "destructive"}>
            {review.status.replace(/_/g, " ")}
          </Badge>
          <Link
            href={`/runs/${review.run_id}`}
            className="text-xs text-primary underline-offset-4 hover:underline"
          >
            Open run console
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          onClick={() => submitMutation.mutate(review.run_id)}
          disabled={submitMutation.isPending || !ready}
        >
          Submit application
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => skipMutation.mutate(review.run_id)}
          disabled={skipMutation.isPending}
        >
          <SkipForward className="mr-1 size-4" aria-hidden />
          Skip submit
        </Button>
      </div>

      <div>
        <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Readiness report
        </h4>
        <ReadinessChecks readiness={review.readiness} />
      </div>

      {review.fill_diffs.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Fill diff (masked values)
          </h4>
          <div className="overflow-x-auto rounded-md border">
            <Table>
              <caption className="sr-only">
                Proposed versus actual field values for this application run
              </caption>
              <TableHeader>
                <TableRow>
                  <TableHead scope="col">Field</TableHead>
                  <TableHead scope="col">Proposed</TableHead>
                  <TableHead scope="col">Actual</TableHead>
                  <TableHead scope="col" className="w-16">
                    Match
                  </TableHead>
                  <TableHead scope="col" className="w-20">
                    <span className="sr-only">Actions</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {review.fill_diffs.map((row) => (
                  <TableRow key={row.field_key}>
                    <TableCell className="font-medium">{row.label ?? row.field_key}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {row.proposed_redacted ?? "—"}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {row.actual_redacted ?? "—"}
                    </TableCell>
                    <TableCell>{row.matched ? "✓" : "—"}</TableCell>
                    <TableCell>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => onEditField?.(row.field_key)}
                      >
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border p-3 text-sm">
          <div className="mb-1 flex items-center gap-2 font-medium">
            <FileText className="size-4" aria-hidden />
            Resume
          </div>
          <p className="text-muted-foreground">{review.resume_filename ?? "Not attached"}</p>
        </div>
        <div className="rounded-md border p-3 text-sm">
          <div className="mb-1 font-medium">Cover letter</div>
          <p className="line-clamp-4 text-muted-foreground">
            {review.cover_letter_preview ?? "No generated letter on file"}
          </p>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Run policy: {review.policy.replace(/_/g, " ")}. You approve the final submit — Jober does
        not hide automation from you or the employer.
      </p>
    </section>
  );
}
