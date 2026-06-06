"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

const LANES = [
  { id: "not_started", title: "Not started" },
  { id: "running", title: "Running" },
  { id: "needs_review", title: "Needs review" },
  { id: "ready", title: "Ready to submit" },
  { id: "applied", title: "Applied" },
  { id: "failed", title: "Failed" },
] as const;

export function JobKanban({ className }: { className?: string }) {
  return (
    <ScrollArea className={cn("w-full whitespace-nowrap", className)}>
      <div className="flex gap-4 pb-4" role="list" aria-label="Job pipeline board">
        {LANES.map((lane) => (
          <Card
            key={lane.id}
            className="w-64 shrink-0 border-border/60 bg-card/60"
            role="listitem"
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between gap-2">
                <CardTitle className="text-sm font-medium">{lane.title}</CardTitle>
                <Badge variant="secondary" className="text-xs">
                  0
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="min-h-32 text-xs text-muted-foreground">
              Cards appear when runs are scheduled.
            </CardContent>
          </Card>
        ))}
      </div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  );
}
