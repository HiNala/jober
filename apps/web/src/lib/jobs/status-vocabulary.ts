import type { JobTargetStatus } from "@jober/schemas";

/** Shared queue + batch status labels — keep table filters and batch preview aligned. */
export const JOB_STATUS_LABEL: Record<JobTargetStatus, string> = {
  new: "Not started",
  queued: "Queued",
  in_progress: "In progress",
  applied: "Applied",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
  skipped: "Skipped",
};

export const JOB_STATUS_OPTIONS: JobTargetStatus[] = [
  "new",
  "queued",
  "in_progress",
  "applied",
  "rejected",
  "withdrawn",
  "skipped",
];

/** Batch preview uses the same status filter vocabulary as the queue table. */
export const BATCH_FILTER_STATUS_OPTIONS = JOB_STATUS_OPTIONS.map((value) => ({
  value,
  label: JOB_STATUS_LABEL[value],
}));

export const BATCH_EXCLUSION_LABEL: Record<string, string> = {
  already_applied: "Already marked applied in your tracker",
  prior_successful_run: "Prior run succeeded for this job",
  missing_apply_url: "Missing apply URL — add a link before batching",
};

export function formatBatchExclusionReason(reason: string): string {
  return BATCH_EXCLUSION_LABEL[reason] ?? reason.replace(/_/g, " ");
}
