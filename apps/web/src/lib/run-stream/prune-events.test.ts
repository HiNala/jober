import { describe, expect, it } from "vitest";

import type { RunStreamEvent } from "@/lib/api/run-console";

import { MAX_STREAM_EVENTS, pruneStreamEvents } from "@/lib/run-stream/prune-events";

function event(seq: number): RunStreamEvent {
  return {
    id: `e${seq}`,
    seq,
    ts: "2026-01-01T00:00:00Z",
    level: "info",
    event_type: "field.filled",
    message: `event ${seq}`,
  };
}

describe("pruneStreamEvents", () => {
  it("keeps all events under the cap", () => {
    const events = Array.from({ length: 100 }, (_, index) => event(index + 1));
    expect(pruneStreamEvents(events)).toHaveLength(100);
  });

  it("retains the newest events when over the cap", () => {
    const events = Array.from({ length: MAX_STREAM_EVENTS + 50 }, (_, index) => event(index + 1));
    const pruned = pruneStreamEvents(events);
    expect(pruned).toHaveLength(MAX_STREAM_EVENTS);
    expect(pruned[0]?.seq).toBe(51);
    expect(pruned.at(-1)?.seq).toBe(MAX_STREAM_EVENTS + 50);
  });
});
