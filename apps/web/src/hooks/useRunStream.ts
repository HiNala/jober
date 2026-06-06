"use client";

export type RunStreamStatus = "idle" | "connecting" | "open" | "closed" | "error";

export interface RunStreamEvent {
  id: string;
  ts: string;
  level: string;
  message: string;
}

/**
 * SSE stub for Mission 11 — will connect to `/api/runs/{id}/events`.
 */
export function useRunStream(runId: string | null) {
  if (!runId) {
    return { status: "idle" as const, events: [] as RunStreamEvent[] };
  }

  // Mission 11: subscribe via EventSource and populate events.
  return { status: "closed" as const, events: [] as RunStreamEvent[] };
}
