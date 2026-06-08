import { describe, expect, it } from "vitest";

import { buildCanvasArtifacts } from "@/lib/canvas/artifacts";
import type { RunConsoleSnapshot } from "@/lib/api/run-console";

const baseSnapshot: RunConsoleSnapshot = {
  run_id: "run-1",
  job_target_id: "job-1",
  company: "Acme",
  role: "Eng",
  status: "running",
  current_step: "fill",
  attempt_count: 1,
  latest_screenshot_url: "https://example.com/live.png",
  latest_screenshot_key: "k",
  open_checkpoint: null,
  timeline: [
    {
      seq: 1,
      ts: "2026-01-01T00:00:00Z",
      status: "running",
      step: "navigate",
      screenshot_url: "https://example.com/t1.png",
    },
  ],
  artifacts: [
    {
      attempt_index: 1,
      trace_url: "https://example.com/trace.zip",
      screenshot_url: "https://example.com/a1.png",
    },
  ],
  last_event_seq: 1,
  events: [],
};

describe("buildCanvasArtifacts", () => {
  it("includes timeline, attempt artifacts, and live fallback", () => {
    const items = buildCanvasArtifacts(baseSnapshot, []);
    expect(items.some((item) => item.id === "timeline-1")).toBe(true);
    expect(items.some((item) => item.kind === "trace")).toBe(true);
    expect(items.some((item) => item.id === "attempt-1-screenshot")).toBe(true);
  });

  it("adds document.generated events", () => {
    const items = buildCanvasArtifacts(baseSnapshot, [
      {
        id: "e1",
        seq: 2,
        ts: "2026-01-01T00:01:00Z",
        level: "info",
        event_type: "document.generated",
        message: "letter",
        payload: { filename: "cover.pdf" },
      },
    ]);
    expect(items.some((item) => item.kind === "document")).toBe(true);
  });
});
