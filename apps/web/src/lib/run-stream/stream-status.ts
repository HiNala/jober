export type RunStreamStatus = "idle" | "connecting" | "open" | "closed" | "error";

export function streamStatusLabel(
  status: RunStreamStatus,
  options?: { hasEvents?: boolean },
): string {
  if (status === "connecting" && options?.hasEvents) {
    return "Reconnecting";
  }
  if (status === "open") {
    return "Live";
  }
  if (status === "connecting") {
    return "Connecting";
  }
  if (status === "error") {
    return "Disconnected";
  }
  return status;
}

export function isStreamReconnecting(status: RunStreamStatus, eventCount: number): boolean {
  return status === "connecting" && eventCount > 0;
}
