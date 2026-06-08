/** Tracks which stream line seq values are "historical" vs newly arrived. */
export class EventStreamRevealTracker {
  private baselineSeq: number | undefined;

  sync(events: { seq: number }[]): void {
    if (events.length === 0) {
      this.baselineSeq = undefined;
      return;
    }
    if (this.baselineSeq === undefined) {
      this.baselineSeq = Math.max(...events.map((event) => event.seq));
    }
  }

  shouldReveal(seq: number): boolean {
    return this.baselineSeq !== undefined && seq > this.baselineSeq;
  }
}

const trackers = new Map<string, EventStreamRevealTracker>();

/** Per-stream reveal predicate — baseline frozen on first batch (client-only). */
export function shouldRevealStreamLine(
  streamKey: string,
  events: { seq: number }[],
  seq: number,
): boolean {
  let tracker = trackers.get(streamKey);
  if (!tracker) {
    tracker = new EventStreamRevealTracker();
    trackers.set(streamKey, tracker);
  }
  tracker.sync(events);
  return tracker.shouldReveal(seq);
}

/** Test helper — reset registry between cases. */
export function clearStreamRevealTrackers(): void {
  trackers.clear();
}
