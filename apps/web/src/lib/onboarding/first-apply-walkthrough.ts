/**
 * Guided first-apply walkthrough — client progress + step catalog.
 * Completion is derived from live data; dismiss is localStorage only.
 */

export type WalkthroughStepId =
  | "add_jobs"
  | "upload_resume"
  | "tailor_docs"
  | "dry_run"
  | "review_approve";

export type WalkthroughStepDef = {
  id: WalkthroughStepId;
  title: string;
  body: string;
  href: string;
  cta: string;
  optional?: boolean;
};

export const FIRST_APPLY_STEPS: WalkthroughStepDef[] = [
  {
    id: "add_jobs",
    title: "Add jobs to your queue",
    body: "Import a spreadsheet or discover roles from company boards.",
    href: "/discover",
    cta: "Discover or import",
  },
  {
    id: "upload_resume",
    title: "Upload your resume",
    body: "Your vault resume grounds letters, form fills, and tailored variants.",
    href: "/vault",
    cta: "Open vault",
  },
  {
    id: "tailor_docs",
    title: "Tailor materials for a role",
    body: "Generate a cover letter or resume variant for a job you care about.",
    href: "/documents",
    cta: "Document studio",
    optional: true,
  },
  {
    id: "dry_run",
    title: "Start a dry-run batch",
    body: "Select jobs in the queue and preview a dry-run — nothing is submitted.",
    href: "/queue",
    cta: "Open queue",
  },
  {
    id: "review_approve",
    title: "Review and approve",
    body: "When a run needs you, open the console, read the fill diff, then approve.",
    href: "/queue",
    cta: "Check runs",
  },
];

const DISMISS_KEY = "jober-first-apply-walkthrough-dismissed";
const COMPLETE_KEY = "jober-first-apply-walkthrough-complete";
/** Same-tab notify for useSyncExternalStore subscribers. */
const WALKTHROUGH_CHANGE_EVENT = "jober-first-apply-walkthrough-change";

export type WalkthroughProgress = {
  hasJobs: boolean;
  hasResume: boolean;
  hasDocuments: boolean;
  hasRuns: boolean;
  hasReviewOrSuccess: boolean;
};

export function stepIsDone(id: WalkthroughStepId, p: WalkthroughProgress): boolean {
  switch (id) {
    case "add_jobs":
      return p.hasJobs;
    case "upload_resume":
      return p.hasResume;
    case "tailor_docs":
      return p.hasDocuments;
    case "dry_run":
      return p.hasRuns;
    case "review_approve":
      return p.hasReviewOrSuccess;
    default:
      return false;
  }
}

export function walkthroughStats(p: WalkthroughProgress): {
  done: number;
  total: number;
  requiredDone: number;
  requiredTotal: number;
  allRequiredDone: boolean;
} {
  const required = FIRST_APPLY_STEPS.filter((s) => !s.optional);
  const done = FIRST_APPLY_STEPS.filter((s) => stepIsDone(s.id, p)).length;
  const requiredDone = required.filter((s) => stepIsDone(s.id, p)).length;
  return {
    done,
    total: FIRST_APPLY_STEPS.length,
    requiredDone,
    requiredTotal: required.length,
    allRequiredDone: requiredDone >= required.length,
  };
}

function notifyWalkthroughChange(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(WALKTHROUGH_CHANGE_EVENT));
}

export function subscribeWalkthroughStorage(onStoreChange: () => void): () => void {
  if (typeof window === "undefined") return () => {};
  const handler = () => onStoreChange();
  window.addEventListener("storage", handler);
  window.addEventListener(WALKTHROUGH_CHANGE_EVENT, handler);
  return () => {
    window.removeEventListener("storage", handler);
    window.removeEventListener(WALKTHROUGH_CHANGE_EVENT, handler);
  };
}

export function isWalkthroughDismissed(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(DISMISS_KEY) === "1";
}

export function setWalkthroughDismissed(dismissed: boolean): void {
  if (typeof window === "undefined") return;
  if (dismissed) window.localStorage.setItem(DISMISS_KEY, "1");
  else window.localStorage.removeItem(DISMISS_KEY);
  notifyWalkthroughChange();
}

export function isWalkthroughMarkedComplete(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(COMPLETE_KEY) === "1";
}

export function setWalkthroughMarkedComplete(complete: boolean): void {
  if (typeof window === "undefined") return;
  if (complete) window.localStorage.setItem(COMPLETE_KEY, "1");
  else window.localStorage.removeItem(COMPLETE_KEY);
  notifyWalkthroughChange();
}

/** True when the card should hide (dismissed or auto-completed). SSR snapshot: false. */
export function isWalkthroughHidden(): boolean {
  return isWalkthroughDismissed() || isWalkthroughMarkedComplete();
}
