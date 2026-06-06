import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

export function WorkerStatusPanel() {
  return (
    <div className="rounded-lg border border-border/60 bg-card/80 p-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-medium">Worker pool</h2>
          <p className="text-xs text-muted-foreground">Celery + Playwright</p>
        </div>
        <Badge variant="outline" className="text-xs">
          Idle
        </Badge>
      </div>
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Capacity</span>
          <span>0 / 1 slots</span>
        </div>
        <Progress value={0} aria-label="Worker capacity used" />
      </div>
    </div>
  );
}
