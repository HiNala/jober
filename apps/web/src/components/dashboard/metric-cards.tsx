import { Activity, CheckCircle2, Clock, ListTodo } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const METRICS = [
  {
    label: "Queue depth",
    value: "—",
    hint: "Priority A targets",
    icon: ListTodo,
  },
  {
    label: "Active runs",
    value: "0",
    hint: "Workers executing",
    icon: Activity,
  },
  {
    label: "Needs review",
    value: "0",
    hint: "Human checkpoints",
    icon: Clock,
  },
  {
    label: "Applied (7d)",
    value: "0",
    hint: "Confirmed submissions",
    icon: CheckCircle2,
  },
] as const;

export function MetricCards() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {METRICS.map(({ label, value, hint, icon: Icon }) => (
        <Card key={label} className="border-border/60 bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {label}
            </CardTitle>
            <Icon className="size-4 text-muted-foreground" aria-hidden />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold tabular-nums">{value}</div>
            <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
