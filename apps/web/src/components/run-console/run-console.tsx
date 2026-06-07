"use client";

import { RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useRunStream } from "@/hooks/useRunStream";

import { ArtifactLinks } from "./artifact-links";
import { CheckpointCard } from "./checkpoint-card";
import { EventTerminal } from "./event-terminal";
import { StateTimeline } from "./state-timeline";

export interface RunConsoleProps {
  runId: string;
}

export function RunConsole({ runId }: RunConsoleProps) {
  const {
    status,
    events,
    snapshot,
    reconnect,
    selectedTimelineSeq,
    setSelectedTimelineSeq,
    displayScreenshotUrl,
  } = useRunStream(runId);

  if (!snapshot) {
    return (
      <p className="text-sm text-muted-foreground">
        {status === "error" ? "Could not load run console." : "Loading run console…"}
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold">
            {snapshot.company} — {snapshot.role}
          </h2>
          <p className="text-sm text-muted-foreground">Run {snapshot.run_id}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{snapshot.status}</Badge>
          <Badge variant="outline">{status}</Badge>
          <Button size="sm" variant="outline" onClick={() => void reconnect()}>
            <RefreshCw className="mr-1 size-3.5" aria-hidden />
            Reconnect
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <div className="overflow-hidden rounded-lg border border-border/60 bg-muted/20">
            {displayScreenshotUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={displayScreenshotUrl}
                alt="Latest browser frame"
                className="aspect-video w-full object-contain bg-zinc-900"
              />
            ) : (
              <div className="flex aspect-video items-center justify-center text-sm text-muted-foreground">
                No screenshot yet
              </div>
            )}
          </div>
          <StateTimeline
            snapshot={snapshot}
            selectedSeq={selectedTimelineSeq}
            onSelectSeq={setSelectedTimelineSeq}
          />
          <CheckpointCard runId={runId} snapshot={snapshot} />
          <ArtifactLinks artifacts={snapshot.artifacts} />
        </div>
        <EventTerminal events={events} company={snapshot.company} role={snapshot.role} />
      </div>
    </div>
  );
}
