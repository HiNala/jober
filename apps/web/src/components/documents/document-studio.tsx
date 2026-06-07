"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Download, Lock, RefreshCw, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { PageError, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  documentDownloadUrl,
  fetchJobsForStudio,
  generateCoverLetter,
  type GeneratedDocumentRead,
} from "@/lib/api/documents";
import { fetchProfile } from "@/lib/api/vault";

export function DocumentStudio() {
  const [jobId, setJobId] = useState<string>("");
  const [locked, setLocked] = useState(false);
  const [draft, setDraft] = useState<GeneratedDocumentRead | null>(null);
  const [letterText, setLetterText] = useState("");

  const jobsQuery = useQuery({ queryKey: ["job-targets"], queryFn: fetchJobsForStudio });
  const profileQuery = useQuery({ queryKey: ["profile"], queryFn: fetchProfile });

  const generateMutation = useMutation({
    mutationFn: ({ force }: { force: boolean }) =>
      generateCoverLetter(jobId, { force, includeDocx: true }),
    onSuccess: (doc) => {
      setDraft(doc);
      setLetterText(doc.text);
      toast.success(doc.cached ? "Loaded cached letter" : "Cover letter generated");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const selectedJob = useMemo(
    () => jobsQuery.data?.find((j) => j.id === jobId),
    [jobsQuery.data, jobId],
  );

  const hasResume = Boolean(profileQuery.data?.active_resume?.has_text);
  const wordCount = letterText.trim() ? letterText.trim().split(/\s+/).length : 0;

  const coverage = draft?.keyword_coverage;

  if (jobsQuery.isLoading) return <PageLoading label="Loading jobs…" />;
  if (jobsQuery.isError) {
    return (
      <PageError
        title="Could not load jobs"
        message="Import the job tracker or seed demo data first."
        onRetry={() => void jobsQuery.refetch()}
      />
    );
  }

  const jobs = jobsQuery.data ?? [];

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <Card className="border-border/60">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Job + resume</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Select value={jobId} onValueChange={(v) => setJobId(v ?? "")}>
            <SelectTrigger aria-label="Select job">
              <SelectValue placeholder="Choose a job target" />
            </SelectTrigger>
            <SelectContent>
              {jobs.map((job) => (
                <SelectItem key={job.id} value={job.id}>
                  {job.company} — {job.role}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedJob && (
            <div className="space-y-1 text-xs text-muted-foreground">
              <p>Lane: {selectedJob.fit_lane ?? "—"}</p>
              <p className="line-clamp-2">Hook: {selectedJob.cover_letter_hook ?? "—"}</p>
            </div>
          )}
          <div className="rounded-md border border-border/50 p-2 text-xs">
            <p className="font-medium">Canonical resume</p>
            <p className="text-muted-foreground">
              {profileQuery.data?.active_resume?.original_filename ?? "Upload in Vault"}
            </p>
            {!hasResume && (
              <p className="mt-1 text-amber-600">Upload a resume in Vault before generating.</p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              disabled={!jobId || !hasResume || locked || generateMutation.isPending}
              onClick={() => generateMutation.mutate({ force: false })}
            >
              <Sparkles className="mr-2 size-4" aria-hidden />
              Generate
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={!jobId || !hasResume || locked || generateMutation.isPending}
              onClick={() => generateMutation.mutate({ force: true })}
            >
              <RefreshCw className="mr-2 size-4" aria-hidden />
              Regenerate
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setLocked((v) => !v)}
              aria-pressed={locked}
            >
              <Lock className="mr-2 size-4" aria-hidden />
              {locked ? "Locked" : "Lock edits"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {draft && (
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="border-border/60">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">ATS score</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-3">
                  <Progress value={draft.ats_score} className="flex-1" />
                  <span className="text-sm font-medium tabular-nums">{draft.ats_score}</span>
                </div>
                {coverage && coverage.stuffing_penalty > 0 && (
                  <p className="text-xs text-amber-600">
                    Stuffing penalty −{coverage.stuffing_penalty} (density {coverage.density})
                  </p>
                )}
              </CardContent>
            </Card>
            <Card className="border-border/60">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Keyword coverage</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-1">
                {coverage?.present.map((kw) => (
                  <Badge key={kw} variant="secondary" className="font-normal">
                    {kw}
                  </Badge>
                ))}
                {coverage?.missing.map((kw) => (
                  <Badge key={kw} variant="outline" className="font-normal text-muted-foreground">
                    missing: {kw}
                  </Badge>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

        <Card className="border-border/60">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-sm">Letter preview</CardTitle>
              {letterText && (
                <p className="text-xs text-muted-foreground tabular-nums">{wordCount} words</p>
              )}
            </div>
            {draft && (
              <div className="flex gap-2">
                <a
                  href={documentDownloadUrl(draft.pdf_download_path)}
                  download
                  className="inline-flex h-7 items-center gap-1 rounded-md border border-border px-2.5 text-xs font-medium hover:bg-muted"
                >
                  <Download className="size-3.5" aria-hidden />
                  PDF
                </a>
                {draft.docx_download_path && (
                  <a
                    href={documentDownloadUrl(draft.docx_download_path)}
                    download
                    className="inline-flex h-7 items-center rounded-md border border-border px-2.5 text-xs font-medium hover:bg-muted"
                  >
                    DOCX
                  </a>
                )}
              </div>
            )}
          </CardHeader>
          <CardContent>
            <Textarea
              value={letterText}
              onChange={(e) => setLetterText(e.target.value)}
              readOnly={locked}
              rows={16}
              className="font-mono text-sm leading-relaxed"
              placeholder="Select a job and generate a cover letter…"
            />
          </CardContent>
        </Card>

        {coverage?.explain && coverage.explain.length > 0 && (
          <Card className="border-border/60">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Explain this letter</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {coverage.explain.map((block) => (
                <div key={block.paragraph_index} className="rounded-md border border-border/40 p-3">
                  <p className="text-xs font-medium text-muted-foreground">
                    Paragraph {block.paragraph_index + 1}
                  </p>
                  <p className="mt-1">
                    <span className="text-muted-foreground">Resume facts: </span>
                    {block.resume_facts.join(" · ")}
                  </p>
                  <p className="mt-1">
                    <span className="text-muted-foreground">Job keywords: </span>
                    {block.job_keywords.join(" · ")}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
