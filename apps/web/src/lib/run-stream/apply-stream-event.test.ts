import { describe, expect, it } from "vitest";

import type { RunConsoleSnapshot } from "@/lib/api/run-console";

import { applyStreamEvent } from "@/lib/run-stream/apply-stream-event";

const baseSnapshot: RunConsoleSnapshot = {
  run_id: "run-1",
  job_target_id: "job-1",
  company: "Acme",
  role: "Eng",
  status: "running",
  current_step: "navigate",
  attempt_count: 1,
  latest_screenshot_url: "https://example.com/old.png",
  latest_screenshot_key: "old",
  open_checkpoint: null,
  timeline: [],
  artifacts: [],
  last_event_seq: 1,
  events: [],
};

describe("applyStreamEvent", () => {
  it("updates latest screenshot from browser.screenshot events", () => {
    const next = applyStreamEvent(baseSnapshot, {
      id: "e2",
      seq: 2,
      ts: "2026-01-01T00:00:00Z",
      level: "info",
      event_type: "browser.screenshot",
      message: "frame",
      screenshot_url: "https://example.com/new.png",
      screenshot_key: "new",
    });
    expect(next?.latest_screenshot_url).toBe("https://example.com/new.png");
    expect(next?.last_event_seq).toBe(2);
  });

  it("updates status on state.changed", () => {
    const next = applyStreamEvent(baseSnapshot, {
      id: "e3",
      seq: 3,
      ts: "2026-01-01T00:00:00Z",
      level: "info",
      event_type: "state.changed",
      message: "review",
      payload: { status: "review_and_submit", step: "review" },
    });
    expect(next?.status).toBe("review_and_submit");
    expect(next?.current_step).toBe("review");
  });

  it("returns null when snapshot is missing", () => {
    expect(
      applyStreamEvent(null, {
        id: "e1",
        seq: 1,
        ts: "",
        level: "info",
        event_type: "browser.screenshot",
        message: "x",
      }),
    ).toBeNull();
  });
});
