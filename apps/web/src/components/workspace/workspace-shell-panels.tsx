"use client";

import { useEffect, useMemo } from "react";
import { useDefaultLayout, usePanelRef } from "react-resizable-panels";

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { WorkspaceCanvasDrawer, WorkspaceCanvasPanel } from "@/components/workspace/workspace-canvas";
import { WorkspaceCenterHeader } from "@/components/workspace/workspace-center-header";
import { WorkspaceCommandBar } from "@/components/workspace/workspace-command-bar";
import { WorkspaceNav } from "@/components/workspace/workspace-nav";
import { useMediaQuery } from "@/hooks/use-media-query";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function WorkspaceShellPanels({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  const isNarrow = useMediaQuery("(max-width: 1023px)");
  const {
    navCollapsed,
    canvasOpen,
    focusMode,
    setNavCollapsed,
    setCanvasOpen,
  } = useWorkspaceStore();
  const navPanelRef = usePanelRef();

  const panelIds = useMemo(() => {
    if (focusMode) {
      return ["center"];
    }
    if (canvasOpen && !isNarrow) {
      return ["nav", "center", "canvas"];
    }
    return ["nav", "center"];
  }, [canvasOpen, focusMode, isNarrow]);

  const layoutStorage = useMemo(
    () => ({
      getItem: (name: string) => window.localStorage.getItem(name),
      setItem: (name: string, value: string) => {
        window.localStorage.setItem(name, value);
      },
    }),
    [],
  );

  const { defaultLayout, onLayoutChanged } = useDefaultLayout({
    id: "jober-workspace-panels",
    panelIds,
    storage: layoutStorage,
  });

  useEffect(() => {
    if (isNarrow) {
      setNavCollapsed(true);
    }
  }, [isNarrow, setNavCollapsed]);

  useEffect(() => {
    const panel = navPanelRef.current;
    if (!panel || focusMode) {
      return;
    }
    if (navCollapsed && !panel.isCollapsed()) {
      panel.collapse();
      return;
    }
    if (!navCollapsed && panel.isCollapsed()) {
      panel.expand();
    }
  }, [focusMode, navCollapsed, navPanelRef]);

  const showInlineCanvas = canvasOpen && !isNarrow && !focusMode;

  return (
    <>
      <ResizablePanelGroup
        id="jober-workspace-panels"
        orientation="horizontal"
        defaultLayout={defaultLayout}
        onLayoutChanged={onLayoutChanged}
        className={cn("min-h-0 flex-1", motionView)}
      >
        {!focusMode ? (
          <>
            <ResizablePanel
              id="nav"
              panelRef={navPanelRef}
              defaultSize={14}
              minSize={navCollapsed ? 4 : 10}
              maxSize={22}
              collapsible
              collapsedSize={4}
            >
              <WorkspaceNav />
            </ResizablePanel>
            <ResizableHandle withHandle />
          </>
        ) : null}

        <ResizablePanel id="center" minSize={28} defaultSize={showInlineCanvas ? 38 : 86}>
          <div className="flex h-full min-w-[20rem] flex-col">
            <WorkspaceCenterHeader title={title} />
            <main
              id="main-content"
              tabIndex={-1}
              className="min-h-0 flex-1 overflow-auto focus:outline-none"
            >
              {children}
            </main>
            <WorkspaceCommandBar />
          </div>
        </ResizablePanel>

        {showInlineCanvas ? (
          <>
            <ResizableHandle withHandle />
            <ResizablePanel id="canvas" defaultSize={48} minSize={30}>
              <WorkspaceCanvasPanel />
            </ResizablePanel>
          </>
        ) : null}
      </ResizablePanelGroup>

      {isNarrow ? (
        <WorkspaceCanvasDrawer
          open={canvasOpen && !focusMode}
          onOpenChange={setCanvasOpen}
        />
      ) : null}
    </>
  );
}
