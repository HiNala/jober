import type { RunConsoleSnapshot, RunStreamEvent } from "@/lib/api/run-console";

export type CanvasArtifactKind =
  | "screenshot"
  | "trace"
  | "video"
  | "dom"
  | "document"
  | "timeline";

export type CanvasArtifact = {
  id: string;
  label: string;
  kind: CanvasArtifactKind;
  thumbUrl?: string | null;
  openUrl?: string | null;
  timelineSeq?: number;
  attemptIndex?: number;
};

export function buildCanvasArtifacts(
  snapshot: RunConsoleSnapshot | null,
  events: RunStreamEvent[],
): CanvasArtifact[] {
  if (!snapshot) {
    return [];
  }

  const items: CanvasArtifact[] = [];

  for (const item of snapshot.timeline) {
    if (!item.screenshot_url) {
      continue;
    }
    items.push({
      id: `timeline-${item.seq}`,
      label: item.step ?? item.status ?? `t${item.seq}`,
      kind: "timeline",
      thumbUrl: item.screenshot_url,
      openUrl: item.screenshot_url,
      timelineSeq: item.seq,
    });
  }

  for (const artifact of snapshot.artifacts) {
    const idx = artifact.attempt_index;
    if (artifact.screenshot_url) {
      items.push({
        id: `attempt-${idx}-screenshot`,
        label: `A${idx} shot`,
        kind: "screenshot",
        thumbUrl: artifact.screenshot_url,
        openUrl: artifact.screenshot_url,
        attemptIndex: idx,
      });
    }
    if (artifact.trace_url) {
      items.push({
        id: `attempt-${idx}-trace`,
        label: `A${idx} trace`,
        kind: "trace",
        openUrl: artifact.trace_url,
        attemptIndex: idx,
      });
    }
    if (artifact.video_url) {
      items.push({
        id: `attempt-${idx}-video`,
        label: `A${idx} video`,
        kind: "video",
        thumbUrl: artifact.video_url,
        openUrl: artifact.video_url,
        attemptIndex: idx,
      });
    }
    if (artifact.dom_url) {
      items.push({
        id: `attempt-${idx}-dom`,
        label: `A${idx} DOM`,
        kind: "dom",
        openUrl: artifact.dom_url,
        attemptIndex: idx,
      });
    }
  }

  const docEvents = events.filter((event) => event.event_type === "document.generated");
  docEvents.forEach((event) => {
    const filename = String(event.payload?.filename ?? event.payload?.kind ?? "document");
    items.push({
      id: `doc-${event.seq}`,
      label: filename,
      kind: "document",
      timelineSeq: event.seq,
    });
  });

  if (items.length === 0 && snapshot.latest_screenshot_url) {
    items.push({
      id: "live-latest",
      label: "Live",
      kind: "screenshot",
      thumbUrl: snapshot.latest_screenshot_url,
      openUrl: snapshot.latest_screenshot_url,
    });
  }

  return items;
}

export function findCanvasArtifact(
  artifacts: CanvasArtifact[],
  id: string | null,
): CanvasArtifact | undefined {
  if (!id) {
    return undefined;
  }
  return artifacts.find((item) => item.id === id);
}
