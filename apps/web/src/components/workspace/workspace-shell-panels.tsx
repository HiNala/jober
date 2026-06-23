"use client";

import { useEffect, useMemo } from "react";
import { useDefaultLayout, usePanelRef } from "react-resizable-panels";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { WorkspaceCanvasPanel } from "@/components/workspace/workspace-canvas";
import { WorkspaceCenterHeader } from "@/components/workspace/workspace-center-header";
import { WorkspaceNav } from "@/components/workspace/workspace-nav";
import { useMediaQuery } from "@/hooks/use-media-query";
import { RouteTransition } from "@/components/motion/route-transition";
import { WORKSPACE_NARROW_QUERY } from "@/lib/workspace/breakpoints";
import type { WorkspaceLayoutMode } from "@/lib/workspace/layout";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function WorkspaceShellPanels({
  title,
  layoutMode,
  children,
}: {
  title: string;
  layoutMode: WorkspaceLayoutMode;
  children: React.ReactNode;
}) {
  const isNarrow = useMediaQuery(WORKSPACE_NARROW_QUERY);
  const isOpsDesk = layoutMode === "ops-desk";
  const { navCollapsed, canvasOpen, focusMode, setNavCollapsed, setCanvasOpen } =
    useWorkspaceStore();
  const navPanelRef = usePanelRef();

  const effectiveCanvasOpen = isOpsDesk && canvasOpen;

  const panelIds = useMemo(() => {
    if (isNarrow || (focusMode && isOpsDesk)) {
      return ["center"];
    }
    if (effectiveCanvasOpen) {
      return ["nav", "center", "canvas"];
    }
    return ["nav", "center"];
  }, [effectiveCanvasOpen, focusMode, isNarrow, isOpsDesk]);

  const panelStorageId =
    layoutMode === "ops-desk" ? "jober-workspace-panels-ops" : "jober-workspace-panels-editorial";

  const layoutStorage = useMemo(
    () => ({
      getItem: (name: string) => {
        const stored = window.localStorage.getItem(name);
        if (!stored) return null;
        try {
          const layout = JSON.parse(stored) as Record<string, number>;
          // Reject corrupted layouts where nav is below collapsedSize (5%)
          if ("nav" in layout && layout.nav < 5) {
            window.localStorage.removeItem(name);
            return null;
          }
          return stored;
        } catch {
          return null;
        }
      },
      setItem: (name: string, value: string) => {
        window.localStorage.setItem(name, value);
      },
    }),
    [],
  );

  const { defaultLayout, onLayoutChanged } = useDefaultLayout({
    id: panelStorageId,
    panelIds,
    storage: layoutStorage,
  });

  useEffect(() => {
    if (!isOpsDesk) {
      setCanvasOpen(false);
    }
  }, [isOpsDesk, setCanvasOpen]);

  useEffect(() => {
    if (isNarrow) {
      setNavCollapsed(true);
    }
  }, [isNarrow, setNavCollapsed]);

  useEffect(() => {
    const panel = navPanelRef.current;
    if (!panel || (focusMode && isOpsDesk)) {
      return;
    }
    if (navCollapsed && !panel.isCollapsed()) {
      panel.collapse();
      return;
    }
    if (!navCollapsed && panel.isCollapsed()) {
      panel.expand();
    }
  }, [focusMode, isOpsDesk, navCollapsed, navPanelRef]);

  const showInlineCanvas = effectiveCanvasOpen && !isNarrow && !(focusMode && isOpsDesk);

  return (
    <>
      <ResizablePanelGroup
        id={panelStorageId}
        orientation="horizontal"
        defaultLayout={defaultLayout}
        onLayoutChanged={onLayoutChanged}
        className={cn("min-h-0 flex-1", motionView)}
      >
        {!(focusMode && isOpsDesk) && !isNarrow ? (
          <>
            <ResizablePanel
              id="nav"
              panelRef={navPanelRef}
              defaultSize="14"
              minSize={navCollapsed ? "5" : "10"}
              maxSize="22"
              collapsible
              collapsedSize="5"
            >
              <WorkspaceNav />
            </ResizablePanel>
            <ResizableHandle withHandle />
          </>
        ) : null}

        <ResizablePanel
          id="center"
          minSize="28"
          defaultSize={showInlineCanvas ? "38" : "86"}
        >
          <div className="flex h-full min-w-0 flex-col">
            <WorkspaceCenterHeader title={title} layoutMode={layoutMode} />
            <main
              id="main-content"
              tabIndex={-1}
              className="workspace-canvas min-h-0 flex-1 overflow-auto focus:outline-none"
              style={{ paddingBottom: "var(--safe-bottom)" }}
            >
              <RouteTransition>{children}</RouteTransition>
            </main>
          </div>
        </ResizablePanel>

        {showInlineCanvas ? (
          <>
            <ResizableHandle withHandle />
            <ResizablePanel id="canvas" defaultSize="48" minSize="30">
              <WorkspaceCanvasPanel />
            </ResizablePanel>
          </>
        ) : null}
      </ResizablePanelGroup>

    </>
  );
}
