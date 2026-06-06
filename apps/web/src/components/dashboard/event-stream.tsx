import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

const PLACEHOLDER_EVENTS = [
  { ts: "—", level: "info", message: "Event stream connects in Mission 11 (SSE)." },
];

export function EventStream() {
  return (
    <div className="rounded-lg border border-border/60 bg-card/80">
      <div className="px-4 py-3">
        <h2 className="text-sm font-medium">Recent events</h2>
        <p className="text-xs text-muted-foreground">Live worker + browser telemetry</p>
      </div>
      <Separator />
      <ScrollArea className="h-48">
        <ul className="space-y-0 p-2 font-mono text-xs" aria-live="polite">
          {PLACEHOLDER_EVENTS.map((event) => (
            <li
              key={event.message}
              className="rounded px-2 py-1.5 text-muted-foreground hover:bg-muted/40"
            >
              <span className="text-muted-foreground/70">{event.ts}</span>{" "}
              <span className="uppercase text-accent">{event.level}</span>{" "}
              {event.message}
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}
