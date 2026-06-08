import { describe, expect, it } from "vitest";

import {
  clearStreamRevealTrackers,
  EventStreamRevealTracker,
  shouldRevealStreamLine,
} from "@/lib/motion/event-stream-reveal";

describe("EventStreamRevealTracker", () => {
  it("does not reveal the initial historical batch", () => {
    const tracker = new EventStreamRevealTracker();
    tracker.sync([{ seq: 1 }, { seq: 2 }, { seq: 3 }]);

    expect(tracker.shouldReveal(1)).toBe(false);
    expect(tracker.shouldReveal(3)).toBe(false);

    tracker.sync([{ seq: 1 }, { seq: 2 }, { seq: 3 }, { seq: 4 }]);
    expect(tracker.shouldReveal(4)).toBe(true);
  });

  it("reveals only new lines when streaming from empty", () => {
    const tracker = new EventStreamRevealTracker();
    tracker.sync([]);
    tracker.sync([{ seq: 10 }]);
    expect(tracker.shouldReveal(10)).toBe(false);

    tracker.sync([{ seq: 10 }, { seq: 11 }]);
    expect(tracker.shouldReveal(11)).toBe(true);
  });

  it("resets baseline when events clear", () => {
    const tracker = new EventStreamRevealTracker();
    tracker.sync([{ seq: 5 }]);
    tracker.sync([]);
    tracker.sync([{ seq: 1 }, { seq: 2 }]);

    expect(tracker.shouldReveal(1)).toBe(false);
    expect(tracker.shouldReveal(2)).toBe(false);
  });

  it("registry isolates streams by key", () => {
    clearStreamRevealTrackers();
    const batch = [{ seq: 1 }, { seq: 2 }];
    expect(shouldRevealStreamLine("run-a", batch, 1)).toBe(false);
    expect(shouldRevealStreamLine("run-b", batch, 1)).toBe(false);
    expect(shouldRevealStreamLine("run-a", [...batch, { seq: 3 }], 3)).toBe(true);
    clearStreamRevealTrackers();
  });
});
