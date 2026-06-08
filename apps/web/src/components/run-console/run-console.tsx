"use client";

import { RefreshCw } from "lucide-react";

import { ContentReveal } from "@/components/motion/content-reveal";
import { StatusPill } from "@/components/motion/status-pill";
import { PageError, RunConsoleSkeleton } from "@/components/states/page-states";
import { Button } from "@/components/ui/button";
import { motionFadeIn, motionPress } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { useRunStream } from "@/hooks/useRunStream";

import { ArtifactLinks } from "./artifact-links";
import { CheckpointCard } from "./checkpoint-card";
import { EventTerminal } from "./event-terminal";
import { StateTimeline } from "./state-timeline";

export interface RunConsoleProps {
  runId: string;
}

function streamStatusLabel(status: string): string {
  if (status === "open") return "Live";
  if (status === "connecting") return "Connecting";
  if (status === "error") return "Disconnected";
  return status;
}

export function RunConsole({ runId }: RunConsoleProps) {
  const runCanvas = useRunCanvas();
  const useSharedStream = runCanvas?.runId === runId;
  const fallback = useRunStream(useSharedStream ? null : runId);
  const stream = useSharedStream ? runCanvas! : fallback;
  const {
    status,
    events,
    snapshot,
    reconnect,
    selectedTimelineSeq,
    setSelectedTimelineSeq,
    displayScreenshotUrl,
  } = stream;

  if (status === "error" && !snapshot) {
    return (
      <PageError
        title="Run console unavailable"
        message="Could not load this run. Check the API connection and try again."
        onRetry={() => void reconnect()}
      />
    );
  }

  return (
    <ContentReveal
      ready={snapshot != null}
      skeleton={<RunConsoleSkeleton />}
      className="space-y-5"
    >
      {snapshot ? (
    <div className={cn("space-y-5", motionFadeIn)}>
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Application run
          </p>
          <h1 className="text-xl font-semibold tracking-tight">
            {snapshot.company} — {snapshot.role}
          </h1>
          <p className="mt-1 font-mono text-xs text-muted-foreground">
            Run {snapshot.run_id.slice(0, 8)}…
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <StatusPill status={snapshot.status} />
          <StatusPill status={status === "open" ? "in_progress" : status} label={streamStatusLabel(status)} />
          <Button
            size="sm"
            variant="outline"
            className={motionPress}
            onClick={() => void reconnect()}
            aria-label="Reconnect event stream"
          >
            <RefreshCw className="mr-1 size-3.5" aria-hidden />
            Reconnect
          </Button>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-4">
          <figure className={cn("overflow-hidden rounded-lg", surface.card)}>
            {displayScreenshotUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={displayScreenshotUrl}
                src={displayScreenshotUrl}
                alt={`Latest browser frame for ${snapshot.company}`}
                className="jober-screenshot-frame aspect-video w-full bg-[var(--terminal-bg)] object-contain"
              />
            ) : (
              <figcaption className="flex aspect-video items-center justify-center text-sm text-muted-foreground">
                Waiting for browser frame…
              </figcaption>
            )}
          </figure>
          <StateTimeline
            snapshot={snapshot}
            selectedSeq={selectedTimelineSeq}
            onSelectSeq={setSelectedTimelineSeq}
          />
          <CheckpointCard runId={runId} snapshot={snapshot} />
          <ArtifactLinks artifacts={snapshot.artifacts} />
        </div>
        <EventTerminal
          streamKey={runId}
          events={events}
          company={snapshot.company}
          role={snapshot.role}
          isConnecting={status === "connecting"}
        />
      </div>
    </div>
      ) : null}
    </ContentReveal>
  );
}
