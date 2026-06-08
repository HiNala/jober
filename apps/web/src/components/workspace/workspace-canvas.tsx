"use client";

import * as React from "react";
import {
  Eye,
  EyeOff,
  Grid2x2,
  Layers,
  PanelRightClose,
  Square,
} from "lucide-react";

import { ArtifactGridView } from "@/components/canvas/artifact-grid-view";
import { CanvasFilmstrip } from "@/components/canvas/canvas-filmstrip";
import { CanvasStatusBadge } from "@/components/canvas/canvas-status-badge";
import { CanvasSurfaceTabs } from "@/components/canvas/canvas-surface-tabs";
import { DocumentView } from "@/components/canvas/document-view";
import { FillDiffView } from "@/components/canvas/fill-diff-view";
import { LayersView } from "@/components/canvas/layers-view";
import { LiveBrowserView } from "@/components/canvas/live-browser-view";
import { ReviewCanvasView } from "@/components/canvas/review-canvas-view";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { findCanvasArtifact } from "@/lib/canvas/artifacts";
import { MotionCrossfade } from "@/components/motion/motion-crossfade";
import { motionFadeIn, motionPress, motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { type CanvasViewMode, useWorkspaceStore } from "@/stores/workspace-store";

function ViewModeToggle({
  mode,
  onChange,
}: {
  mode: CanvasViewMode;
  onChange: (mode: CanvasViewMode) => void;
}) {
  const modes: { id: CanvasViewMode; label: string; icon: React.ComponentType<{ className?: string }> }[] =
    [
      { id: "single", label: "Single", icon: Square },
      { id: "grid", label: "Grid", icon: Grid2x2 },
      { id: "layers", label: "Layers", icon: Layers },
    ];

  return (
    <div className="inline-flex rounded-md border bg-muted/30 p-0.5" role="tablist" aria-label="Canvas view mode">
      {modes.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          type="button"
          role="tab"
          aria-selected={mode === id}
          onClick={() => onChange(id)}
          className={cn(
            "inline-flex items-center gap-1 rounded px-2 py-1 text-xs",
            motionView,
            motionPress,
            mode === id
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          <Icon className="size-3.5" aria-hidden />
          <span className="hidden sm:inline">{label}</span>
        </button>
      ))}
    </div>
  );
}

function SingleSurface() {
  const runCanvas = useRunCanvas();
  const { canvasSurface } = useWorkspaceStore();

  if (canvasSurface === "review" || runCanvas?.isReviewState) {
    return <ReviewCanvasView />;
  }

  switch (canvasSurface) {
    case "document":
      return <DocumentView />;
    case "fill-diff":
      return <FillDiffView />;
    case "browser":
    default:
      return <LiveBrowserView />;
  }
}

function CanvasSurface({ mode }: { mode: CanvasViewMode }) {
  if (mode === "grid") {
    return <ArtifactGridView />;
  }
  if (mode === "layers") {
    return <LayersView />;
  }
  return <SingleSurface />;
}

function CanvasChrome({ onClose }: { onClose?: () => void }) {
  const runCanvas = useRunCanvas();
  const {
    canvasViewMode,
    setCanvasViewMode,
    canvasSurface,
    setCanvasSurface,
    filmstripVisible,
    setFilmstripVisible,
    selectedArtifactId,
    toggleCanvas,
  } = useWorkspaceStore();

  const versionLabel =
    findCanvasArtifact(runCanvas?.artifacts ?? [], selectedArtifactId)?.label ?? "live";

  return (
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b px-3 py-2">
        <div className="flex flex-wrap items-center gap-2">
          <ViewModeToggle mode={canvasViewMode} onChange={setCanvasViewMode} />
          {canvasViewMode === "single" ? (
            <CanvasSurfaceTabs
              value={canvasSurface}
              onChange={setCanvasSurface}
              showReview={runCanvas?.isReviewState}
            />
          ) : null}
        </div>
        <div className="flex items-center gap-1">
          <Badge variant="outline" className="tabular-nums">
            {versionLabel}
          </Badge>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setFilmstripVisible(!filmstripVisible)}
            aria-label={filmstripVisible ? "Hide filmstrip" : "Show filmstrip"}
            aria-pressed={filmstripVisible}
          >
            {filmstripVisible ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onClose ?? toggleCanvas}
            aria-label="Close canvas"
            aria-keyshortcuts="Control+\\ Meta+\\"
          >
            <PanelRightClose className="size-3.5" />
          </Button>
        </div>
      </div>

      <div className="relative min-h-0 flex-1 overflow-auto">
        <MotionCrossfade motionKey={`${canvasViewMode}-${canvasSurface}`}>
          <CanvasSurface mode={canvasViewMode} />
        </MotionCrossfade>
        <div className="absolute right-3 top-3">
          <CanvasStatusBadge />
        </div>
      </div>

      <CanvasFilmstrip />
    </div>
  );
}

export function WorkspaceCanvasPanel() {
  return (
    <div className={cn("h-full bg-background", motionFadeIn)}>
      <CanvasChrome />
    </div>
  );
}

export function WorkspaceCanvasDrawer({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-[min(100vw,42rem)] p-0 sm:max-w-none">
        <SheetHeader className="sr-only">
          <SheetTitle>Workspace canvas</SheetTitle>
        </SheetHeader>
        <CanvasChrome onClose={() => onOpenChange(false)} />
      </SheetContent>
    </Sheet>
  );
}
