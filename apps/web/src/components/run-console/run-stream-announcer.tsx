"use client";

import { useEffect, useRef, useState } from "react";

import type { RunStreamEvent } from "@/lib/api/run-console";

function isSignificant(event: RunStreamEvent): boolean {
  return (
    event.event_type === "human.required" ||
    event.event_type.includes("checkpoint") ||
    event.event_type.includes("failed") ||
    event.event_type.includes("completed") ||
    event.event_type === "run.status"
  );
}

function formatAnnouncement(event: RunStreamEvent): string {
  if (event.event_type === "human.required") {
    return `Checkpoint: ${event.message}`;
  }
  return `${event.event_type.replace(/\./g, " ")}: ${event.message}`;
}

/** Announce meaningful run transitions without reading every stream line. */
export function RunStreamAnnouncer({ events }: { events: RunStreamEvent[] }) {
  const lastSeq = useRef(0);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const last = events[events.length - 1];
    if (!last || last.seq <= lastSeq.current || !isSignificant(last)) {
      return;
    }
    lastSeq.current = last.seq;
    setMessage(formatAnnouncement(last));
  }, [events]);

  return (
    <div className="sr-only" aria-live="polite" aria-atomic="true">
      {message}
    </div>
  );
}
