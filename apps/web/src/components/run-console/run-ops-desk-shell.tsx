"use client";

import { WorkspaceCanvasPanel } from "@/components/workspace/workspace-canvas";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useMediaQuery } from "@/hooks/use-media-query";
import { WORKSPACE_NARROW_QUERY } from "@/lib/workspace/breakpoints";
import { useWorkspaceStore } from "@/stores/workspace-store";

/** Below desktop width, stack run work vs workspace canvas as tabs (tablet/phone). */
export function RunOpsDeskShell({ children }: { children: React.ReactNode }) {
  const isNarrow = useMediaQuery(WORKSPACE_NARROW_QUERY);
  const { runMobileTab, setRunMobileTab } = useWorkspaceStore();

  if (!isNarrow) {
    return <>{children}</>;
  }

  return (
    <Tabs
      value={runMobileTab}
      onValueChange={(value) => setRunMobileTab(value as "work" | "canvas")}
      className="flex min-h-0 flex-1 flex-col gap-3"
    >
      <TabsList className="grid w-full shrink-0 grid-cols-2" aria-label="Run console views">
        <TabsTrigger value="work" className="min-h-11">
          Work
        </TabsTrigger>
        <TabsTrigger value="canvas" className="min-h-11">
          Canvas
        </TabsTrigger>
      </TabsList>
      <TabsContent value="work" className="min-h-0 flex-1 outline-none">
        {children}
      </TabsContent>
      <TabsContent
        value="canvas"
        className="min-h-[min(70vh,32rem)] flex-1 overflow-hidden rounded-lg border border-border/60 outline-none"
      >
        <WorkspaceCanvasPanel />
      </TabsContent>
    </Tabs>
  );
}
