"use client";

import type { ImportReportRead } from "@jober/schemas";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Download } from "lucide-react";
import Link from "next/link";
import { useCallback, useState } from "react";
import { toast } from "sonner";

import { FileUpload } from "@/components/import/file-upload";
import { surface } from "@/lib/design/tokens";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatApiError } from "@/lib/api/errors";
import {
  commitJobsImport,
  exportJobsXlsxUrl,
  previewJobsImport,
} from "@/lib/api/jobs";

type Step = "upload" | "preview" | "done";

type ImportWizardProps = {
  onCommitted?: (report: ImportReportRead) => void | Promise<void>;
};

export function ImportWizard({ onCommitted }: ImportWizardProps) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState<Step>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportReportRead | null>(null);
  const [result, setResult] = useState<ImportReportRead | null>(null);

  const previewMutation = useMutation({
    mutationFn: previewJobsImport,
    onSuccess: (data) => {
      setPreview(data);
      setStep("preview");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not parse workbook")),
  });

  const importMutation = useMutation({
    mutationFn: commitJobsImport,
    onSuccess: async (data) => {
      setResult(data);
      setStep("done");
      void queryClient.invalidateQueries({ queryKey: ["job-targets"] });
      toast.success("Spreadsheet imported");
      if (onCommitted) await onCommitted(data);
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Import failed")),
  });

  const handleFile = useCallback(
    (picked: File) => {
      setFile(picked);
      setResult(null);
      previewMutation.mutate(picked);
    },
    [previewMutation],
  );

  const report = result ?? preview;

  return (
    <div className="space-y-4">
      {step === "upload" && (
        <FileUpload onFile={handleFile} busy={previewMutation.isPending} />
      )}
      {previewMutation.isPending && (
        <p className="text-sm text-muted-foreground">Parsing workbook…</p>
      )}

      {step === "preview" && preview && file && (
        <Card className={surface.workspace}>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Mapping preview</CardTitle>
            <p className="text-sm text-muted-foreground">{file.name}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(preview.mappings).map(([sheet, cols]) => (
              <div key={sheet} className="space-y-2">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {sheet.replace("_", " ")}
                </p>
                <div className="flex flex-wrap gap-2">
                  {cols.map((col) => (
                    <Badge
                      key={col.field}
                      variant={col.matched_header ? "secondary" : "outline"}
                      className="font-normal"
                    >
                      {col.field}
                      {col.matched_header ? ` → ${col.matched_header}` : " (unmapped)"}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
            <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
              <span>Job targets: {preview.job_targets.created} rows</span>
              <span>·</span>
              <span>Boards: {preview.company_boards.created}</span>
              <span>·</span>
              <span>Angles: {preview.cover_letter_angles.created}</span>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => importMutation.mutate(file)}
                disabled={importMutation.isPending}
              >
                Confirm import
              </Button>
              <Button variant="outline" onClick={() => setStep("upload")}>
                Choose another file
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === "done" && result && (
        <Card className={surface.workspace}>
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <CheckCircle2 className="size-5 text-emerald-500" aria-hidden />
            <CardTitle className="text-base">Import complete</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              Created {result.job_targets.created} · updated {result.job_targets.updated} job
              targets
            </p>
            {result.warnings.length > 0 && (
              <div className="rounded-md border border-amber-500/30 bg-amber-500/5 p-3">
                <div className="mb-2 flex items-center gap-2 font-medium text-amber-700 dark:text-amber-400">
                  <AlertTriangle className="size-4" aria-hidden />
                  {result.warnings.length} warnings
                </div>
                <ul className="max-h-40 space-y-1 overflow-y-auto text-xs text-muted-foreground">
                  {result.warnings.slice(0, 20).map((w, i) => (
                    <li key={`${w.code}-${w.row}-${i}`}>
                      [{w.sheet}
                      {w.row ? ` row ${w.row}` : ""}] {w.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              <Link href="/queue" className={buttonVariants({ size: "sm" })}>
                View queue
              </Link>
              <a
                href={exportJobsXlsxUrl()}
                download
                className={buttonVariants({ size: "sm", variant: "outline" })}
              >
                <Download className="size-3.5" aria-hidden />
                Export workbook
              </a>
            </div>
            <p className="text-xs text-muted-foreground">
              Next: review imported targets, then start a dry-run batch from the dashboard.
            </p>
          </CardContent>
        </Card>
      )}

      {report && report.warnings.length > 0 && step !== "done" && (
        <p className="text-xs text-muted-foreground">
          {report.warnings.length} parse warnings will appear in the final report.
        </p>
      )}
    </div>
  );
}
