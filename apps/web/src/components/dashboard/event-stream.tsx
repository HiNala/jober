"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { fetchRecentRunEvents } from "@/lib/api/run-console";

function formatLine(event: {
  ts: string;
  event_type: string;
  message: string;
  company: string;
  role: string;
}): string {
  const time = new Date(event.ts).toLocaleTimeString();
  return `[${time}] ${event.company} / ${event.role} — ${event.event_type} ${event.message}`;
}

export function EventStream() {
  const eventsQuery = useQuery({
    queryKey: ["recent-run-events"],
    queryFn: () => fetchRecentRunEvents(30),
    refetchInterval: 5000,
  });

  const events = eventsQuery.data ?? [];

  return (
    <div className="rounded-lg border border-border/60 bg-card/80">
      <div className="px-4 py-3">
        <h2 className="text-sm font-medium">Recent events</h2>
        <p className="text-xs text-muted-foreground">
          Live worker + browser telemetry ·{" "}
          <Link href="/queue" className="text-primary underline-offset-4 hover:underline">
            open queue
          </Link>
        </p>
      </div>
      <Separator />
      <ScrollArea className="h-48">
        <ul className="space-y-0 p-2 font-mono text-xs" aria-live="polite">
          {events.length === 0 ? (
            <li className="px-2 py-1.5 text-muted-foreground">
              No activity yet. Submit a batch or open the{" "}
              <Link href="/queue" className="text-primary underline-offset-4 hover:underline">
                run queue
              </Link>
              .
            </li>
          ) : (
            events.map((event) => (
              <li
                key={event.id}
                className="rounded px-2 py-1.5 text-muted-foreground hover:bg-muted/40"
              >
                <Link
                  href={`/runs/${event.run_id}`}
                  className="block text-foreground/90 hover:underline"
                >
                  {formatLine(event)}
                </Link>
              </li>
            ))
          )}
        </ul>
      </ScrollArea>
    </div>
  );
}
