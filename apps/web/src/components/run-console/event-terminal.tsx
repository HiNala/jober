"use client";

import type { RunStreamEvent } from "@/lib/api/run-console";

export interface EventTerminalProps {
  events: RunStreamEvent[];
  company?: string;
  role?: string;
}

function formatLine(event: RunStreamEvent): string {
  const time = new Date(event.ts).toLocaleTimeString();
  const prefix = `[${time}]`;
  if (event.event_type === "field.filled") {
    const field = String(event.payload?.field_key ?? event.message);
    return `${prefix} filled field="${field}" status=ok`;
  }
  if (event.event_type === "human.required") {
    return `${prefix} HUMAN CHECKPOINT: ${event.message}`;
  }
  return `${prefix} ${event.event_type} ${event.message}`;
}

export function EventTerminal({ events, company, role }: EventTerminalProps) {
  return (
    <div
      className="h-full min-h-[240px] overflow-y-auto rounded-md border border-border/60 bg-zinc-950 p-3 font-mono text-xs text-zinc-100"
      aria-label="Run event stream"
    >
      {company && role && (
        <p className="mb-2 text-zinc-400">
          job=&quot;{company} / {role}&quot;
        </p>
      )}
      {events.length === 0 ? (
        <p className="text-zinc-500">Waiting for events…</p>
      ) : (
        <ul className="space-y-1">
          {events.map((event) => (
            <li key={event.seq} className="whitespace-pre-wrap break-words">
              {formatLine(event)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
