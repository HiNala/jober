/** Mirrors `RunEventType` in packages/schemas — used for SSE listeners. */
export const RUN_SSE_EVENT_TYPES = [
  "run.started",
  "state.changed",
  "browser.navigated",
  "browser.action",
  "browser.screenshot",
  "form.discovered",
  "field.filled",
  "document.generated",
  "verification.warning",
  "human.required",
  "attempt.failed",
  "attempt.retrying",
  "run.succeeded",
  "run.failed",
] as const;

export type RunSseEventType = (typeof RUN_SSE_EVENT_TYPES)[number];
