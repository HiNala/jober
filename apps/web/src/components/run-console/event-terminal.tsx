"use client";

import { ReasoningShimmer } from "@/components/motion/reasoning-shimmer";
import { StreamingText } from "@/components/motion/streaming-text";
import type { RunStreamEvent } from "@/lib/api/run-console";
import { shouldRevealStreamLine } from "@/lib/motion/event-stream-reveal";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export interface EventTerminalProps {
  events: RunStreamEvent[];
  streamKey: string;
  company?: string;
  role?: string;
  isConnecting?: boolean;
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

export function EventTerminal({
  events,
  streamKey,
  company,
  role,
  isConnecting,
}: EventTerminalProps) {
  return (
    <section aria-labelledby="run-event-stream-heading">
      <h2 id="run-event-stream-heading" className="mb-2 text-sm font-medium">
        Event stream
      </h2>
      <div
        className={cn(
          "min-h-[280px] max-h-[min(70vh,520px)] overflow-y-auto rounded-lg border p-3 font-mono text-xs",
          surface.terminal,
        )}
        role="log"
        aria-relevant="additions"
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
          <ol className="space-y-0.5">
            {events.map((event) => (
              <li key={event.seq} className="whitespace-pre-wrap break-words">
                <StreamingText
                  text={formatLine(event)}
                  reveal={shouldRevealStreamLine(streamKey, events, event.seq)}
                />
              </li>
            ))}
          </ol>
        )}
      </div>
    </section>
  );
}
