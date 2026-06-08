"use client";

import { Radio, SkipForward } from "lucide-react";

import { ReasoningShimmer } from "@/components/motion/reasoning-shimmer";
import { PageEmpty, PageError, PageLoading } from "@/components/states/page-states";
import { Button } from "@/components/ui/button";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { motionFadeIn, motionMicro, motionPress } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LiveBrowserView() {
  const runCanvas = useRunCanvas();

  if (!runCanvas?.runId) {
    return (
      <PageEmpty
        title="No active run"
        description="Open a run from the queue or dashboard to watch the browser live."
      />
    );
  }

  if (runCanvas.status === "connecting") {
    return <PageLoading label="Connecting to run stream…" />;
  }

  if (runCanvas.status === "error" && !runCanvas.snapshot) {
    return (
      <PageError
        title="Run stream unavailable"
        message="Could not load the live browser feed."
        onRetry={() => void runCanvas.reconnect()}
      />
    );
  }

  const { snapshot, displayScreenshotUrl, latestUrl, latestAction, liveFollow, catchUpToLive } =
    runCanvas;

  return (
    <div className={cn("flex h-full min-h-[min(480px,60vh)] flex-col", motionFadeIn)}>
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b px-3 py-2 text-xs">
        <div className="min-w-0 space-y-0.5">
          <p className="truncate font-medium">
            {snapshot?.company} — {snapshot?.role}
          </p>
          <p className="truncate text-muted-foreground">
            {latestUrl ?? "Waiting for navigation…"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-medium uppercase tracking-wide",
              motionMicro,
              liveFollow
                ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                : "bg-muted text-muted-foreground",
            )}
          >
            <Radio className="size-3" aria-hidden />
            {liveFollow ? "Live" : "Scrubbing"}
          </span>
          {!liveFollow ? (
            <Button type="button" size="xs" variant="secondary" className={motionPress} onClick={catchUpToLive}>
              <SkipForward className="mr-1 size-3" aria-hidden />
              Catch up to live
            </Button>
          ) : null}
        </div>
      </div>

      {snapshot && snapshot.timeline.length > 1 ? (
        <div className="shrink-0 border-b px-3 py-2">
          <label className="sr-only" htmlFor="canvas-timeline-scrub">
            Scrub run timeline
          </label>
          <input
            id="canvas-timeline-scrub"
            type="range"
            min={0}
            max={snapshot.timeline.length - 1}
            value={
              runCanvas.selectedTimelineSeq === null
                ? snapshot.timeline.length - 1
                : Math.max(
                    0,
                    snapshot.timeline.findIndex(
                      (item) => item.seq === runCanvas.selectedTimelineSeq,
                    ),
                  )
            }
            onChange={(event) => {
              const index = Number(event.target.value);
              const item = snapshot.timeline[index];
              runCanvas.setSelectedTimelineSeq(item?.seq ?? null);
            }}
            className="w-full accent-primary"
          />
          <p className="mt-1 text-[0.65rem] text-muted-foreground">
            {latestAction ?? snapshot.current_step ?? snapshot.status.replace(/_/g, " ")}
          </p>
        </div>
      ) : null}

      <figure className={cn("relative min-h-0 flex-1 overflow-hidden", surface.inset)}>
        {displayScreenshotUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            key={displayScreenshotUrl}
            src={displayScreenshotUrl}
            alt={`Browser frame for ${snapshot?.company ?? "run"}`}
            className="jober-screenshot-frame h-full w-full bg-[var(--terminal-bg)] object-contain"
            data-testid="workspace-browser-canvas"
          />
        ) : (
          <figcaption className="flex h-full flex-col items-center justify-center gap-2 p-6 text-sm text-muted-foreground">
            <ReasoningShimmer label="Waiting for browser frame…" />
          </figcaption>
        )}
      </figure>
    </div>
  );
}
