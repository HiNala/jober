"use client";

import { useQuery } from "@tanstack/react-query";

import { PageEmpty, PageLoading } from "@/components/states/page-states";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useRunCanvas } from "@/contexts/run-canvas-context";
import { fetchReviewPackageByRun } from "@/lib/api/verification";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function FillDiffView() {
  const runCanvas = useRunCanvas();
  const runId = runCanvas?.runId;

  const reviewQuery = useQuery({
    queryKey: ["review-package-run", runId],
    queryFn: () => fetchReviewPackageByRun(runId!),
    enabled: Boolean(runId),
  });

  if (!runId) {
    return (
      <PageEmpty
        title="No fill diff"
        description="Field diffs appear after form fill and verification."
      />
    );
  }

  if (reviewQuery.isLoading) {
    return <PageLoading label="Loading fill diff…" />;
  }

  const rows = reviewQuery.data?.fill_diffs ?? [];

  if (rows.length === 0) {
    return (
      <PageEmpty
        title="No field observations"
        description="Fill diff will list proposed vs actual values (masked) once the form is filled."
      />
    );
  }

  return (
    <div className={cn("overflow-auto p-4", motionFadeIn)}>
      <Table>
        <caption className="sr-only">Masked proposed versus actual field values</caption>
        <TableHeader>
          <TableRow>
            <TableHead scope="col">Field</TableHead>
            <TableHead scope="col">Proposed</TableHead>
            <TableHead scope="col">Actual</TableHead>
            <TableHead scope="col" className="w-16">
              Match
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.field_key}>
              <TableCell className="font-medium">{row.label ?? row.field_key}</TableCell>
              <TableCell className="font-mono text-xs">{row.proposed_redacted ?? "—"}</TableCell>
              <TableCell className="font-mono text-xs">{row.actual_redacted ?? "—"}</TableCell>
              <TableCell>{row.matched ? "✓" : "—"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
