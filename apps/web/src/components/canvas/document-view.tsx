"use client";

import { FileText } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { CoverLetterEditor } from "@/components/canvas/cover-letter-editor";
import { PageEmpty, PageLoading } from "@/components/states/page-states";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { fetchReviewPackageByRun } from "@/lib/api/verification";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function DocumentView() {
  const runCanvas = useRunCanvas();
  const runId = runCanvas?.runId;

  const reviewQuery = useQuery({
    queryKey: ["review-package-run", runId],
    queryFn: () => fetchReviewPackageByRun(runId!),
    enabled: Boolean(runId),
  });

  if (!runId) {
    return (
      <PageEmpty
        title="No document"
        description="Documents appear when a run generates a cover letter or readiness report."
      />
    );
  }

  if (reviewQuery.isLoading) {
    return <PageLoading label="Loading documents…" />;
  }

  const review = reviewQuery.data;
  const cover = review?.cover_letter;

  return (
    <div className={cn("space-y-4 p-4", motionFadeIn)}>
      <div className={cn("rounded-lg p-4", surface.workspace)}>
        <div className="mb-3 flex items-center gap-2 font-medium">
          <FileText className="size-4" aria-hidden />
          Cover letter
        </div>

        {!cover ? (
          <p className="text-sm text-muted-foreground">
            {review?.cover_letter_preview
              ? review.cover_letter_preview
              : "No generated letter for this run — letter generation was skipped or not required."}
          </p>
        ) : (
          <CoverLetterEditor
            key={cover.id}
            cover={cover}
            jobTargetId={review!.job_target_id}
            runId={runId}
          />
        )}
      </div>
      <div className={cn("rounded-lg p-4", surface.workspace)}>
        <p className="mb-1 font-medium">Resume in use</p>
        <p className="text-sm text-muted-foreground">
          {review?.resume_filename ?? "Not attached"}
        </p>
      </div>
      {review?.readiness ? (
        <div className={cn("rounded-lg p-4", surface.workspace)}>
          <p className="mb-2 font-medium">Readiness report</p>
          <ul className="space-y-1 text-sm">
            {review.readiness.checks.map((check) => (
              <li key={check.check_id} className="text-muted-foreground">
                <span className="font-medium text-foreground">
                  {check.check_id.replace(/_/g, " ")}
                </span>
                {" — "}
                {check.reason}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
