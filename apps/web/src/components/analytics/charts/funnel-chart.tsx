"use client";

import { AnalyticsBarChart } from "./bar-chart";

export function FunnelChart({
  steps,
}: {
  steps: Array<{ step: string; unique_sessions: number; drop_off_rate: number }>;
}) {
  const data = steps.map((row) => ({
    step: row.step.replace(/_/g, " "),
    sessions: row.unique_sessions,
    drop_off_pct: Math.round(row.drop_off_rate * 100),
  }));
  return <AnalyticsBarChart data={data} xKey="step" yKey="sessions" label="Sessions" />;
}
