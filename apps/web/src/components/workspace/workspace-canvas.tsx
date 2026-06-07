"use client";

import * as React from "react";
import {
  AlertCircle,
  Eye,
  EyeOff,
  Grid2x2,
  Layers,
  Pencil,
  PanelRightClose,
  Square,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { motionFadeIn, motionView } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import {
  type CanvasViewMode,
  WORKSPACE_DEMO_ARTIFACTS,
  useWorkspaceStore,
} from "@/stores/workspace-store";

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

function CanvasSurface({ mode }: { mode: CanvasViewMode }) {
  if (mode === "grid") {
    return (
      <div className="grid h-full grid-cols-2 gap-2 p-2">
        {Array.from({ length: 4 }).map((_, index) => (
          <div
            key={index}
            className={cn("flex items-center justify-center rounded-md", surface.inset)}
          >
            <span className="text-xs text-muted-foreground">Surface {index + 1}</span>
          </div>
        ))}
      </div>
    );
  }

  if (mode === "layers") {
    return (
      <div className="relative h-full p-4">
        {[0, 1, 2].map((layer) => (
          <div
            key={layer}
            className={cn(
              "absolute inset-4 rounded-lg border",
              surface.card,
              motionFadeIn,
            )}
            style={{
              transform: `translate(${layer * 10}px, ${layer * 10}px)`,
              opacity: 1 - layer * 0.18,
              zIndex: 3 - layer,
            }}
          >
            <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
              Layer {layer + 1}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div
      className="flex h-full min-h-[min(720px,70vh)] flex-col items-center justify-center bg-[var(--terminal-bg)] p-4 text-[var(--terminal-fg)]"
      data-testid="workspace-browser-canvas"
    >
      <p className="text-sm font-medium">Live browser canvas</p>
      <p className="mt-1 max-w-sm text-center text-xs text-muted-foreground">
        Reserved for embedded browser and document preview. Sized for a 1280×720 viewport.
      </p>
      <div className="mt-4 w-full max-w-4xl rounded border border-border/40 bg-black/20 p-2">
        <div className="aspect-video w-full rounded bg-gradient-to-br from-muted/20 to-muted/5" />
      </div>
    </div>
  );
}

function Filmstrip() {
  const { filmstripVisible, selectedArtifactId, setSelectedArtifactId } = useWorkspaceStore();

  if (!filmstripVisible) {
    return null;
  }

  return (
    <div className="shrink-0 border-t bg-muted/20 px-2 py-2">
      <div className="flex gap-2 overflow-x-auto pb-1" aria-label="Artifact versions">
        {WORKSPACE_DEMO_ARTIFACTS.map((artifact) => {
          const selected = selectedArtifactId === artifact.id;
          return (
            <button
              key={artifact.id}
              type="button"
              onClick={() => setSelectedArtifactId(artifact.id)}
              className={cn(
                "flex w-20 shrink-0 flex-col gap-1 rounded-md border p-1.5 text-left",
                motionView,
                selected ? "border-primary bg-primary/5" : "border-border/60 hover:bg-muted/40",
              )}
              aria-pressed={selected}
            >
              <div className="aspect-video w-full rounded bg-[var(--terminal-bg)]" />
              <span className="text-[0.65rem] font-medium tabular-nums">{artifact.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function CanvasChrome({ onClose }: { onClose?: () => void }) {
  const {
    canvasViewMode,
    setCanvasViewMode,
    filmstripVisible,
    setFilmstripVisible,
    selectedArtifactId,
    toggleCanvas,
  } = useWorkspaceStore();

  const versionLabel =
    WORKSPACE_DEMO_ARTIFACTS.find((item) => item.id === selectedArtifactId)?.label ?? "v1";

  return (
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b px-3 py-2">
        <ViewModeToggle mode={canvasViewMode} onChange={setCanvasViewMode} />
        <div className="flex items-center gap-1">
          <Badge variant="outline" className="tabular-nums">
            {versionLabel}
          </Badge>
          <Button variant="ghost" size="icon-sm" aria-label="Edit artifact" disabled title="Coming soon">
            <Pencil className="size-3.5" />
          </Button>
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
        <CanvasSurface mode={canvasViewMode} />
        <div className="absolute right-3 top-3">
          <Badge variant="secondary" className="gap-1 shadow-sm">
            <AlertCircle className="size-3" aria-hidden />
            Preview
          </Badge>
        </div>
      </div>

      <Filmstrip />
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
