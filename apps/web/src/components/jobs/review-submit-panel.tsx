"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, CircleAlert, FileText, SkipForward } from "lucide-react";
import { useMemo } from "react";
import { toast } from "sonner";

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
      toast.message("Submit skipped");
      void queryClient.invalidateQueries({ queryKey });
    },
    onError: (err: unknown) => toast.error(formatApiError(err)),
  });

  const review = reviewQuery.data;

  if (reviewQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading review state…</p>;
  }

  if (!review) {
    return (
      <p className="text-sm text-muted-foreground">
        No application awaiting review. Complete form fill and readiness verification first.
      </p>
    );
  }

  return (
    <section className="space-y-4 rounded-lg border border-border/80 bg-card/40 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">Review &amp; submit</h3>
        <Badge variant={review.readiness.passed ? "secondary" : "destructive"}>
          {review.status.replace(/_/g, " ")}
        </Badge>
      </div>

      <p className="rounded-md bg-muted/50 p-3 text-sm leading-relaxed">{review.human_summary}</p>

      <div>
        <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Readiness report
        </h4>
        <ReadinessChecks readiness={review.readiness} />
      </div>

      {review.fill_diffs.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Fill diff (masked)
          </h4>
          <div className="overflow-x-auto rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Field</TableHead>
                  <TableHead>Proposed</TableHead>
                  <TableHead>Actual</TableHead>
                  <TableHead className="w-16">Match</TableHead>
                  <TableHead className="w-20" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {review.fill_diffs.map((row) => (
                  <TableRow key={row.field_key}>
                    <TableCell className="font-medium">{row.label ?? row.field_key}</TableCell>
                    <TableCell className="font-mono text-xs">{row.proposed_redacted ?? "—"}</TableCell>
                    <TableCell className="font-mono text-xs">{row.actual_redacted ?? "—"}</TableCell>
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

      <div className="flex flex-wrap gap-2 pt-1">
        <Button
          type="button"
          onClick={() => submitMutation.mutate(review.run_id)}
          disabled={submitMutation.isPending || !review.readiness.passed}
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
          Skip
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">
        Policy: {review.policy.replace(/_/g, " ")}. Email confirmation may follow on-page success.
      </p>
    </section>
  );
}
