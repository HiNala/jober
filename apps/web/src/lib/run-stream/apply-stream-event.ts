import type { RunConsoleSnapshot, RunStreamEvent } from "@/lib/api/run-console";

/** Apply one SSE event onto a console snapshot (pure — easy to test). */
export function applyStreamEvent(
  prev: RunConsoleSnapshot | null,
  parsed: RunStreamEvent,
): RunConsoleSnapshot | null {
  if (!prev) {
    return prev;
  }
  return {
    ...prev,
    last_event_seq: parsed.seq,
    latest_screenshot_url: parsed.screenshot_url ?? prev.latest_screenshot_url,
    latest_screenshot_key: parsed.screenshot_key ?? prev.latest_screenshot_key,
    status:
      parsed.event_type === "state.changed"
        ? String(parsed.payload?.status ?? prev.status)
        : prev.status,
    current_step:
      parsed.event_type === "state.changed"
        ? String(parsed.payload?.step ?? prev.current_step ?? "")
        : prev.current_step,
  };
}
