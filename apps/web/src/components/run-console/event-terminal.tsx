"use client";

import { ReasoningShimmer } from "@/components/motion/reasoning-shimmer";
import type { RunStreamEvent } from "@/lib/api/run-console";
import { motionStreamReveal } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export interface EventTerminalProps {
  events: RunStreamEvent[];
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

export function EventTerminal({ events, company, role, isConnecting }: EventTerminalProps) {
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
        aria-live="polite"
        aria-relevant="additions"
      >
        {company && role && (
          <p className="mb-2 text-[var(--terminal-muted)]">
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
              <li
                key={event.seq}
                className={cn("whitespace-pre-wrap break-words", motionStreamReveal)}
              >
                {formatLine(event)}
              </li>
            ))}
          </ol>
        )}
      </div>
    </section>
  );
}
