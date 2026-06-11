import type { RunConsoleSnapshot, RunStreamEvent } from "@/lib/api/run-console";

function resolveStatus(current: string, parsed: RunStreamEvent): string {
  if (parsed.event_type === "state.changed") {
    return String(parsed.payload?.status ?? current);
  }
  if (parsed.event_type === "run.succeeded") {
    return "succeeded";
  }
  if (parsed.event_type === "run.failed") {
    return String(parsed.payload?.status ?? "failed_final");
  }
  return current;
}

function clearsOpenCheckpoint(parsed: RunStreamEvent): boolean {
  if (parsed.event_type === "human.required") {
    const action = parsed.payload?.action;
    return action === "approve" || action === "deny" || action === "skip";
  }
  if (parsed.event_type === "state.changed" && parsed.payload?.action === "approve") {
    return true;
  }
  return false;
}

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
    status: resolveStatus(prev.status, parsed),
    open_checkpoint: clearsOpenCheckpoint(parsed) ? null : prev.open_checkpoint,
    current_step:
      parsed.event_type === "state.changed"
        ? String(parsed.payload?.step ?? prev.current_step ?? "")
        : prev.current_step,
  };
}
