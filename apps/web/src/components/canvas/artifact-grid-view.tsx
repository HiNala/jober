"use client";

import { Download, FileJson, Film, Image as ImageIcon, ScrollText } from "lucide-react";

import { PageEmpty } from "@/components/states/page-states";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { motionFadeIn, motionView } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

function kindIcon(kind: string) {
  switch (kind) {
    case "trace":
      return ScrollText;
    case "video":
      return Film;
    case "dom":
      return FileJson;
    case "document":
      return ScrollText;
    default:
      return ImageIcon;
  }
}

export function ArtifactGridView() {
  const runCanvas = useRunCanvas();
  const setSelectedArtifactId = useWorkspaceStore((s) => s.setSelectedArtifactId);
  const setCanvasViewMode = useWorkspaceStore((s) => s.setCanvasViewMode);
  const setCanvasSurface = useWorkspaceStore((s) => s.setCanvasSurface);

  const artifacts = runCanvas?.artifacts ?? [];

  if (artifacts.length === 0) {
    return (
      <PageEmpty
        title="No artifacts"
        description="Screenshots, traces, and documents will appear here during a run."
      />
    );
  }

  return (
    <div className={cn("grid grid-cols-2 gap-2 p-2 sm:grid-cols-3", motionFadeIn)}>
      {artifacts.map((artifact) => {
        const Icon = kindIcon(artifact.kind);
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
                setCanvasViewMode("single");
              } else if (artifact.openUrl) {
                setCanvasSurface("browser");
                setCanvasViewMode("single");
              }
            }}
            className={cn(
              "flex flex-col overflow-hidden rounded-lg border text-left",
              surface.card,
              motionView,
              "hover:border-primary/40",
            )}
          >
            <div className="flex aspect-video items-center justify-center bg-[var(--terminal-bg)]">
              {artifact.thumbUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={artifact.thumbUrl}
                  alt=""
                  className="size-full object-cover"
                />
              ) : (
                <Icon className="size-6 text-muted-foreground" aria-hidden />
              )}
            </div>
            <div className="flex items-center justify-between gap-1 p-2 text-xs">
              <span className="truncate font-medium">{artifact.label}</span>
              {artifact.openUrl && artifact.kind === "trace" ? (
                <a
                  href={artifact.openUrl}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(event) => event.stopPropagation()}
                  className="text-primary"
                  aria-label={`Download ${artifact.label}`}
                >
                  <Download className="size-3.5" />
                </a>
              ) : null}
            </div>
          </button>
        );
      })}
    </div>
  );
}
