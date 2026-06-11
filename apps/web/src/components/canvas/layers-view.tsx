"use client";

import { PageEmpty } from "@/components/states/page-states";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { findCanvasArtifact } from "@/lib/canvas/artifacts";
import { motionFadeIn, motionView } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function LayersView() {
  const runCanvas = useRunCanvas();
  const { selectedArtifactId, setSelectedArtifactId } = useWorkspaceStore();
  const artifacts = runCanvas?.artifacts.filter((a) => a.kind === "timeline" || a.kind === "screenshot") ?? [];

  if (artifacts.length === 0) {
    return (
      <PageEmpty
        title="No versions"
        description="Timeline screenshots stack here as the run progresses."
      />
    );
  }

  const selected = findCanvasArtifact(artifacts, selectedArtifactId) ?? artifacts.at(-1);

  return (
    <div className={cn("relative h-full p-4", motionFadeIn)}>
      {artifacts.slice(-4).map((artifact, index, slice) => {
        const layer = slice.length - 1 - index;
        const isTop = artifact.id === selected?.id;
        return (
          <button
            key={artifact.id}
            type="button"
            onClick={() => {
              setSelectedArtifactId(artifact.id);
              if (artifact.timelineSeq !== undefined) {
                runCanvas?.setSelectedTimelineSeq(artifact.timelineSeq);
              }
            }}
            className={cn(
              "absolute inset-4 overflow-hidden rounded-lg border",
              surface.workspace,
              motionView,
              isTop && "ring-2 ring-primary",
            )}
            style={{
              transform: `translate(${layer * 12}px, ${layer * 12}px)`,
              opacity: 1 - layer * 0.15,
              zIndex: 10 - layer,
            }}
          >
            {artifact.thumbUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={artifact.thumbUrl}
                alt={artifact.label}
                className={cn("h-full w-full object-contain", surface.terminalMedia)}
              />
            ) : (
              <span className="flex h-full items-center justify-center text-xs text-muted-foreground">
                {artifact.label}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
