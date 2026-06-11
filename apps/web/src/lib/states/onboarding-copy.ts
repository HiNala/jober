/** User-facing empty-state copy — no dev commands or internal tooling references. */

export const QUEUE_EMPTY = {
  title: "Import your job tracker",
  description:
    "Upload your spreadsheet to populate the queue. Jober maps companies, roles, and ATS URLs into runnable targets.",
} as const;

export const QUEUE_FILTER_EMPTY = "No matches — try adjusting your filters.";

export const DASHBOARD_FIRST_RUN = {
  title: "Welcome to Jober",
  description:
    "Import your tracker, upload a resume, then run a dry-run batch to watch Jober fill applications while you review every step.",
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
