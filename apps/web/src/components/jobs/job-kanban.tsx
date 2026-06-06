"use client";

import type { JobTargetRead } from "@jober/schemas";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

const LANES = [
  { id: "not_started", title: "Not started", statuses: ["new"] as const },
  { id: "running", title: "Running", statuses: ["queued", "in_progress"] as const },
  { id: "applied", title: "Applied", statuses: ["applied"] as const },
  { id: "closed", title: "Closed", statuses: ["rejected", "withdrawn", "skipped"] as const },
] as const;

export interface JobKanbanProps {
  rows?: JobTargetRead[];
  className?: string;
  onSelect?: (job: JobTargetRead) => void;
}

export function JobKanban({ rows = [], className, onSelect }: JobKanbanProps) {
  return (
    <ScrollArea className={cn("w-full whitespace-nowrap", className)}>
      <div className="flex gap-4 pb-4" role="list" aria-label="Job pipeline board">
        {LANES.map((lane) => {
          const cards = rows.filter((row) =>
            (lane.statuses as readonly string[]).includes(row.status),
          );
          return (
            <Card
              key={lane.id}
              className="w-64 shrink-0 border-border/60 bg-card/60"
              role="listitem"
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between gap-2">
                  <CardTitle className="text-sm font-medium">{lane.title}</CardTitle>
                  <Badge variant="secondary" className="text-xs">
                    {cards.length}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {cards.length === 0 ? (
                  <p className="min-h-16 text-xs text-muted-foreground">No cards</p>
                ) : (
                  cards.map((job) => (
                    <button
                      key={job.id}
                      type="button"
                      className="w-full rounded-md border border-border/50 bg-background/60 p-2 text-left text-xs transition-colors hover:bg-muted/50"
                      onClick={() => onSelect?.(job)}
                    >
                      <p className="font-medium leading-snug">{job.company}</p>
                      <p className="text-muted-foreground">{job.role}</p>
                      {job.ats_guess && (
                        <Badge variant="outline" className="mt-1 text-[10px]">
                          {job.ats_guess}
                        </Badge>
                      )}
                    </button>
                  ))
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  );
}
