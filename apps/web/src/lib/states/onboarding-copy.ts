/** User-facing empty-state copy — no dev commands or internal tooling references. */

export const QUEUE_EMPTY = {
  title: "Import your job tracker",
  description:
    "Upload your spreadsheet to populate the queue. Jober maps companies, roles, and ATS URLs into runnable targets.",
} as const;

export const QUEUE_FILTER_EMPTY = "No matches — try adjusting your filters.";

export const DASHBOARD_FIRST_RUN = {
  title: "Let's get to work.",
  description:
    "Import your tracker or discover perfect-fit roles, upload a resume, then run a dry-run batch. You review the fill diff and approve before anything is sent.",
} as const;

export const DOCUMENTS_EMPTY_JOBS = {
  title: "Add jobs to generate letters",
  description:
    "Import your job tracker on the queue page, then return here to generate a tailored cover letter for each role.",
} as const;

export const DOCUMENTS_ERROR_JOBS =
  "Could not load jobs. Import your tracker on the queue page, then try again.";

export const BLOG_LEAD =
  "Product updates, launch notes, and changelog entries from the Jober team.";
