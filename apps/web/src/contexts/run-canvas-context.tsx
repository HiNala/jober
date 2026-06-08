"use client";

import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useMemo } from "react";

import { useRunStream } from "@/hooks/useRunStream";
import { buildCanvasArtifacts } from "@/lib/canvas/artifacts";
import { useWorkspaceStore } from "@/stores/workspace-store";

type RunCanvasContextValue = ReturnType<typeof useRunStream> & {
  runId: string | null;
  artifacts: ReturnType<typeof buildCanvasArtifacts>;
};

const RunCanvasContext = createContext<RunCanvasContextValue | null>(null);

export function RunCanvasProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const runId = useMemo(() => {
    const match = pathname.match(/^\/runs\/([^/]+)/);
    return match?.[1] ?? null;
  }, [pathname]);

  const stream = useRunStream(runId);
  const artifacts = useMemo(
    () => buildCanvasArtifacts(stream.snapshot, stream.events),
    [stream.events, stream.snapshot],
  );

  useEffect(() => {
    useWorkspaceStore.setState({ activeRunId: runId });
  }, [runId]);

  useEffect(() => {
    if (stream.isReviewState) {
      useWorkspaceStore.getState().setCanvasSurface("review");
    }
  }, [stream.isReviewState]);

  const value = useMemo(
    () => ({
      runId,
      ...stream,
      artifacts,
    }),
    [artifacts, runId, stream],
  );

  return <RunCanvasContext.Provider value={value}>{children}</RunCanvasContext.Provider>;
}

export function useRunCanvas() {
  return useContext(RunCanvasContext);
}
