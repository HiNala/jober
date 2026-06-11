import type { RunStreamEvent } from "@/lib/api/run-console";

/** Keep the DOM bounded on long runs — server may emit hundreds of events. */
export const MAX_STREAM_EVENTS = 500;

export function pruneStreamEvents(events: RunStreamEvent[]): RunStreamEvent[] {
  if (events.length <= MAX_STREAM_EVENTS) {
    return events;
  }
  return events.slice(-MAX_STREAM_EVENTS);
}
