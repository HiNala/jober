"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { fetchFailureReportForJob } from "@/lib/api/recovery";

export interface FailureReportPanelProps {
  jobTargetId: string;
}

export function FailureReportPanel({ jobTargetId }: FailureReportPanelProps) {
  const reportQuery = useQuery({
    queryKey: ["failure-report", jobTargetId],
    queryFn: () => fetchFailureReportForJob(jobTargetId),
  });

  const report = reportQuery.data;
  if (!report) {
    return null;
  }

  return (
    <section className="space-y-3 rounded-lg border border-rose-500/30 bg-rose-500/5 p-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="size-4 text-rose-600" aria-hidden />
        <h3 className="text-sm font-semibold">Failure report</h3>
        <Badge variant="destructive">{report.failure_class.replace(/_/g, " ")}</Badge>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span>
          {report.attempt_count} attempt{report.attempt_count === 1 ? "" : "s"}
        </span>
        <Badge variant={report.safe_to_retry ? "secondary" : "outline"}>
          {report.safe_to_retry ? "Safe to retry" : "Needs you"}
        </Badge>
      </div>
      <p className="text-sm text-muted-foreground">{report.inferred_reason}</p>
      <p className="text-sm">
        <span className="font-medium">Recommended action:</span> {report.recommended_manual_action}
      </p>
      {report.self_assessments && report.self_assessments.length > 0 && (
        <ul className="space-y-2 text-xs text-muted-foreground">
          {report.self_assessments.map((item) => (
            <li key={item.attempt_index} className="rounded border border-border/60 p-2">
              <span className="font-medium text-foreground">
                Attempt {item.attempt_index} ({item.strategy_name})
              </span>
              {" — "}
              {item.tried}. {item.happened} Next: {item.next_change}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
