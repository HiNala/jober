"use client";

import { Copy } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { ReasoningShimmer } from "@/components/motion/reasoning-shimmer";
import { StreamingText } from "@/components/motion/streaming-text";
import { Button } from "@/components/ui/button";
import type { RunStreamEvent } from "@/lib/api/run-console";
import { motionShimmer } from "@/lib/design/motion";
import { shouldRevealStreamLine } from "@/lib/motion/event-stream-reveal";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export interface EventTerminalProps {
  events: RunStreamEvent[];
  streamKey: string;
  company?: string;
  role?: string;
  isConnecting?: boolean;
  isReconnecting?: boolean;
}

function formatLine(event: RunStreamEvent): string {
  const time = new Date(event.ts).toLocaleTimeString();
  const prefix = `[${time}]`;
  if (event.event_type === "field.filled") {
    const field = String(event.payload?.field_key ?? event.message);
    return `${prefix} filled ${field}`;
  }
  if (event.event_type === "human.required") {
    return `${prefix} checkpoint: ${event.message}`;
  }
  return `${prefix} ${event.event_type.replace(/\./g, " ")} — ${event.message}`;
}

function eventPayloadText(event: RunStreamEvent): string {
  const payload =
    event.payload && Object.keys(event.payload).length > 0
      ? `\n${JSON.stringify(event.payload, null, 2)}`
      : "";
  return `${formatLine(event)}${payload}`;
}

const SCROLL_LOCK_THRESHOLD_PX = 48;

export function EventTerminal({
  events,
  streamKey,
  company,
  role,
  isConnecting,
  isReconnecting,
}: EventTerminalProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const scrollToBottom = useCallback(() => {
    const node = scrollRef.current;
    if (!node) {
      return;
    }
    node.scrollTop = node.scrollHeight;
  }, []);

  useEffect(() => {
    if (autoScroll) {
      scrollToBottom();
    }
  }, [autoScroll, events, scrollToBottom]);

  const handleScroll = () => {
    const node = scrollRef.current;
    if (!node) {
      return;
    }
    const atBottom =
      node.scrollHeight - node.scrollTop - node.clientHeight <= SCROLL_LOCK_THRESHOLD_PX;
    setAutoScroll(atBottom);
  };

  const copyEvent = async (event: RunStreamEvent) => {
    try {
      await navigator.clipboard.writeText(eventPayloadText(event));
      toast.message("Event copied");
    } catch {
      toast.error("Could not copy to clipboard");
    }
  };

  return (
    <section aria-labelledby="run-event-stream-heading" data-testid="run-event-stream">
      <div className="mb-2 flex items-center justify-between gap-2">
        <h2 id="run-event-stream-heading" className="text-sm font-medium">
          Event stream
        </h2>
        {!autoScroll && events.length > 0 ? (
          <Button type="button" size="xs" variant="ghost" onClick={() => setAutoScroll(true)}>
            Resume auto-scroll
          </Button>
        ) : null}
      </div>
      {isReconnecting ? (
        <p
          className={cn(
            "mb-2 rounded-md border border-amber-500/30 bg-amber-500/10 px-2 py-1 text-xs text-amber-900 dark:text-amber-100",
            motionShimmer,
          )}
          role="status"
        >
          Reconnecting to live stream…
        </p>
      ) : null}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className={cn(
          "min-h-[280px] max-h-[min(70vh,520px)] overflow-y-auto rounded-lg border p-3 font-mono text-xs",
          surface.terminal,
        )}
        role="log"
        aria-relevant="additions"
        aria-busy={isConnecting || isReconnecting}
      >
        {company && role && (
          <p className={cn("mb-2", surface.terminalMuted)}>
            {company} / {role}
          </p>
        )}
        {events.length === 0 ? (
          isConnecting ? (
            <ReasoningShimmer label="Connecting to stream…" />
          ) : (
            <ReasoningShimmer label="Waiting for run events…" />
          )
        ) : (
          <ol className="space-y-1">
            {events.map((event) => (
              <li key={event.seq} className="group flex gap-1 whitespace-pre-wrap break-words">
                <span className="min-w-0 flex-1">
                  <StreamingText
                    text={formatLine(event)}
                    reveal={shouldRevealStreamLine(streamKey, events, event.seq)}
                  />
                </span>
                <Button
                  type="button"
                  size="icon-xs"
                  variant="ghost"
                  className="shrink-0 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
                  onClick={() => void copyEvent(event)}
                  aria-label={`Copy event ${event.seq}`}
                >
                  <Copy className="size-3" aria-hidden />
                </Button>
              </li>
            ))}
          </ol>
        )}
      </div>
    </section>
  );
}
