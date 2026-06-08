"use client";

import { FileJson, Film, Image as ImageIcon, ScrollText } from "lucide-react";

import { useRunCanvas } from "@/contexts/run-canvas-context";
import { motionLayout, motionPress, motionSpringSettle, motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

function ThumbIcon({ kind }: { kind: string }) {
  const className = "size-4 text-muted-foreground";
  switch (kind) {
    case "trace":
      return <ScrollText className={className} aria-hidden />;
    case "video":
      return <Film className={className} aria-hidden />;
    case "dom":
      return <FileJson className={className} aria-hidden />;
    default:
      return <ImageIcon className={className} aria-hidden />;
  }
}

export function CanvasFilmstrip() {
  const runCanvas = useRunCanvas();
  const {
    filmstripVisible,
    selectedArtifactId,
    setSelectedArtifactId,
    setCanvasViewMode,
    setCanvasSurface,
  } = useWorkspaceStore();

  const artifacts = runCanvas?.artifacts ?? [];

  return (
    <div
      className={cn(
        "shrink-0 overflow-hidden border-t bg-muted/20",
        motionLayout,
        filmstripVisible ? "max-h-40 opacity-100" : "max-h-0 border-t-transparent opacity-0",
      )}
    >
      {!filmstripVisible ? null : artifacts.length === 0 ? (
        <div className="px-3 py-2 text-xs text-muted-foreground">No artifacts yet</div>
      ) : (
    <div className="px-2 py-2">
      <div className="flex gap-2 overflow-x-auto pb-1" aria-label="Artifact versions">
        {artifacts.map((artifact) => {
          const selected = selectedArtifactId === artifact.id;
          return (
            <button
              key={artifact.id}
              type="button"
              onClick={() => {
                setSelectedArtifactId(artifact.id);
                if (artifact.timelineSeq !== undefined) {
                  runCanvas?.setSelectedTimelineSeq(artifact.timelineSeq);
                }
                if (artifact.kind === "document") {
                  setCanvasSurface("document");
                } else if (artifact.kind === "trace" && artifact.openUrl) {
                  window.open(artifact.openUrl, "_blank", "noopener,noreferrer");
                  return;
                } else {
                  setCanvasSurface("browser");
                }
                setCanvasViewMode("single");
              }}
              className={cn(
                "flex w-20 shrink-0 flex-col gap-1 rounded-md border p-1.5 text-left",
                motionView,
                motionPress,
                selected && motionSpringSettle,
                selected ? "border-primary bg-primary/5" : "border-border/60 hover:bg-muted/40",
              )}
              aria-pressed={selected}
            >
              <div className="flex aspect-video w-full items-center justify-center overflow-hidden rounded bg-[var(--terminal-bg)]">
                {artifact.thumbUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={artifact.thumbUrl} alt="" className="size-full object-cover" />
                ) : (
                  <ThumbIcon kind={artifact.kind} />
                )}
              </div>
              <span className="truncate text-[0.65rem] font-medium tabular-nums">
                {artifact.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
      )}
    </div>
  );
}
