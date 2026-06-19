"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Check, Copy, Download, RefreshCw, Save, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import Link from "next/link";

import { KeywordCoveragePanel } from "@/components/documents/keyword-coverage-panel";
import { LlmBudgetExceeded } from "@/components/documents/llm-budget-exceeded";
import { LlmProviderBanner } from "@/components/documents/llm-provider-banner";
import { ParagraphControls } from "@/components/documents/paragraph-controls";
import { PageEmpty, PageError, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  duplicateCoverLetter,
  fetchJobsForStudio,
  fetchLetterOptions,
  generateCoverLetter,
  patchCoverLetter,
  type GeneratedDocumentRead,
} from "@/lib/api/documents";
import { track } from "@/lib/analytics/events";
import { formatApiError, isApiBudgetExceeded } from "@/lib/api/errors";
import { fetchLlmConfig } from "@/lib/api/llm";
import { useUnsavedChanges } from "@/lib/forms/use-unsaved-changes";
import { fetchProfile } from "@/lib/api/vault";
import { coverLetterDownloadFilename } from "@/lib/documents/download-filename";
import { splitParagraphs } from "@/lib/documents/merge-paragraphs";
import { motionShimmer, motionStatusEnter } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import {
  DOCUMENTS_EMPTY_JOBS,
  DOCUMENTS_ERROR_JOBS,
} from "@/lib/states/onboarding-copy";
import { cn } from "@/lib/utils";

export function DocumentStudio() {
  const [jobId, setJobId] = useState<string>("");
  const [draft, setDraft] = useState<GeneratedDocumentRead | null>(null);
  const [letterText, setLetterText] = useState("");
  const [templateStyle, setTemplateStyle] = useState("classic");
  const [voicePreset, setVoicePreset] = useState("direct");
  const [lockedParagraphs, setLockedParagraphs] = useState<Set<number>>(new Set());
  const [budgetError, setBudgetError] = useState<string | null>(null);
  const [saveFlash, setSaveFlash] = useState(false);
  const [regenIndex, setRegenIndex] = useState<number | null>(null);

  const jobsQuery = useQuery({ queryKey: ["job-targets"], queryFn: fetchJobsForStudio });
  const optionsQuery = useQuery({ queryKey: ["letter-options"], queryFn: fetchLetterOptions });
  const profileQuery = useQuery({ queryKey: ["profile"], queryFn: fetchProfile });
  const llmQuery = useQuery({ queryKey: ["llm-config"], queryFn: fetchLlmConfig });

  const paragraphs = splitParagraphs(letterText);
  useUnsavedChanges(Boolean(draft) && letterText !== (draft?.text ?? ""));

  useEffect(() => {
    if (!saveFlash) return;
    const timer = setTimeout(() => setSaveFlash(false), 2000);
    return () => clearTimeout(timer);
  }, [saveFlash]);

  function handleApiError(err: unknown, fallback: string) {
    if (isApiBudgetExceeded(err)) {
      setBudgetError(formatApiError(err, fallback));
      return;
    }
    toast.error(formatApiError(err, fallback));
  }

  const generateMutation = useMutation({
    mutationFn: ({ force }: { force: boolean }) =>
      generateCoverLetter(jobId, {
        force,
        includeDocx: true,
        templateStyle,
        voicePreset,
        seedText: letterText || undefined,
        lockedParagraphs: [...lockedParagraphs],
      }),
    onSuccess: (doc) => {
      setDraft(doc);
      setLetterText(doc.text);
      setLockedParagraphs(new Set(doc.locked_paragraphs ?? []));
      setBudgetError(null);
      if (!doc.cached) track("document.generated", { doc_type: "cover_letter" });
      toast.success(doc.cached ? "Loaded cached letter" : "Cover letter generated");
    },
    onError: (err: unknown) => handleApiError(err, "Cover letter generation failed"),
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      patchCoverLetter(draft!.id, {
        text: letterText,
        locked_paragraphs: [...lockedParagraphs],
        template_style: templateStyle,
        voice_preset: voicePreset,
      }),
    onSuccess: (doc) => {
      setDraft(doc);
      setLetterText(doc.text);
      setBudgetError(null);
      setSaveFlash(true);
      toast.success("Saved — ATS score updated");
    },
    onError: (err: unknown) => handleApiError(err, "Could not save letter"),
  });

  const regenMutation = useMutation({
    mutationFn: (paragraphIndex: number) => {
      setRegenIndex(paragraphIndex);
      return generateCoverLetter(jobId, {
        force: true,
        includeDocx: true,
        templateStyle,
        voicePreset,
        seedText: letterText,
        lockedParagraphs: [...lockedParagraphs],
        regenerateParagraphIndex: paragraphIndex,
      });
    },
    onSuccess: (doc) => {
      setDraft(doc);
      setLetterText(doc.text);
      setLockedParagraphs(new Set(doc.locked_paragraphs ?? []));
      setBudgetError(null);
      toast.success("Paragraph regenerated");
    },
    onError: (err: unknown) => handleApiError(err, "Regeneration failed"),
    onSettled: () => setRegenIndex(null),
  });

  const duplicateMutation = useMutation({
    mutationFn: () => duplicateCoverLetter(draft!.id, jobId),
    onSuccess: (doc) => {
      setDraft(doc);
      setLetterText(doc.text);
      setLockedParagraphs(new Set(doc.locked_paragraphs ?? []));
      toast.success("Duplicated as a new version");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not duplicate")),
  });

  const isGenerating =
    generateMutation.isPending || regenMutation.isPending || regenIndex !== null;

  const selectedJob = useMemo(
    () => jobsQuery.data?.find((j) => j.id === jobId),
    [jobsQuery.data, jobId],
  );

  const hasResume = Boolean(profileQuery.data?.active_resume?.has_text);
  const wordCount = letterText.trim() ? letterText.trim().split(/\s+/).length : 0;
  const coverage = draft?.keyword_coverage;
  const downloadCompany = selectedJob?.company ?? "company";
  const downloadRole = selectedJob?.role ?? "role";

  const toggleLock = (index: number) => {
    setLockedParagraphs((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  if (jobsQuery.isLoading) return <PageLoading label="Loading jobs…" />;
  if (jobsQuery.isError) {
    return (
      <PageError
        title="Could not load jobs"
        message={DOCUMENTS_ERROR_JOBS}
        onRetry={() => void jobsQuery.refetch()}
      />
    );
  }

  const jobs = jobsQuery.data ?? [];

  if (jobs.length === 0) {
    return (
      <PageEmpty
        title={DOCUMENTS_EMPTY_JOBS.title}
        description={DOCUMENTS_EMPTY_JOBS.description}
        action={
          <Link href="/queue" className={buttonVariants({ size: "sm" })}>
            Import job tracker
          </Link>
        }
      />
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <Card className={surface.workspace}>
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
          {selectedJob ? (
            <div className="space-y-1 text-xs text-muted-foreground">
              <p>Lane: {selectedJob.fit_lane ?? "—"}</p>
              <p className="line-clamp-2">Hook: {selectedJob.cover_letter_hook ?? "—"}</p>
            </div>
          ) : null}
          <div className="rounded-md border border-border/50 p-2 text-xs">
            <p className="font-medium">Canonical resume</p>
            <p className="text-muted-foreground">
              {profileQuery.data?.active_resume?.original_filename ?? "Upload in Vault"}
            </p>
            {!hasResume ? (
              <p className="mt-1 text-amber-600">Upload a resume in Vault before generating.</p>
            ) : null}
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            <Select value={templateStyle} onValueChange={(v) => setTemplateStyle(v ?? "classic")}>
              <SelectTrigger aria-label="Letter template">
                <SelectValue placeholder="Template" />
              </SelectTrigger>
              <SelectContent>
                {(optionsQuery.data?.templates ?? ["classic", "modern", "compact"]).map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={voicePreset} onValueChange={(v) => setVoicePreset(v ?? "direct")}>
              <SelectTrigger aria-label="Voice preset">
                <SelectValue placeholder="Voice" />
              </SelectTrigger>
              <SelectContent>
                {(optionsQuery.data?.voice_presets ?? ["direct"]).map((v) => (
                  <SelectItem key={v} value={v}>
                    {v.replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              data-testid="studio-generate"
              disabled={!jobId || !hasResume || isGenerating}
              onClick={() => generateMutation.mutate({ force: false })}
            >
              <Sparkles className="mr-2 size-4" aria-hidden />
              Generate
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={!jobId || !hasResume || isGenerating}
              onClick={() => generateMutation.mutate({ force: true })}
            >
              <RefreshCw className="mr-2 size-4" aria-hidden />
              Regenerate
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <LlmProviderBanner provider={llmQuery.data?.provider} />
        {budgetError ? (
          <LlmBudgetExceeded message={budgetError} onDismiss={() => setBudgetError(null)} />
        ) : null}

        {draft ? (
          <>
            <div className="flex flex-wrap items-center gap-2">
              {draft.template_style ? (
                <Badge variant="secondary">{draft.template_style}</Badge>
              ) : null}
              {draft.voice_preset ? (
                <Badge variant="outline">{draft.voice_preset.replace(/_/g, " ")}</Badge>
              ) : null}
              {draft.version ? (
                <Badge variant="outline" className="tabular-nums">
                  v{draft.version}
                </Badge>
              ) : null}
            </div>
            <KeywordCoveragePanel atsScore={draft.ats_score ?? 0} coverage={coverage} />
          </>
        ) : null}

        <Card className={surface.workspace}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-sm">Letter preview</CardTitle>
              {letterText ? (
                <p className="text-xs text-muted-foreground tabular-nums">{wordCount} words</p>
              ) : null}
            </div>
            {draft ? (
              <div className="flex flex-wrap gap-2">
                {draft.pdf_download_path ? (
                  <a
                    href={documentDownloadUrl(draft.pdf_download_path)}
                    download={coverLetterDownloadFilename(downloadCompany, downloadRole, "pdf")}
                    data-testid="studio-download-pdf"
                    className="inline-flex h-7 items-center gap-1 rounded-md border border-border px-2.5 text-xs font-medium hover:bg-muted"
                  >
                    <Download className="size-3.5" aria-hidden />
                    PDF
                  </a>
                ) : null}
                {draft.docx_download_path ? (
                  <a
                    href={documentDownloadUrl(draft.docx_download_path)}
                    download={coverLetterDownloadFilename(downloadCompany, downloadRole, "docx")}
                    className="inline-flex h-7 items-center rounded-md border border-border px-2.5 text-xs font-medium hover:bg-muted"
                  >
                    DOCX
                  </a>
                ) : null}
              </div>
            ) : null}
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              data-testid="letter-preview"
              value={letterText}
              onChange={(e) => setLetterText(e.target.value)}
              rows={16}
              className={cn(
                "font-sans text-sm leading-relaxed",
                isGenerating && motionShimmer,
              )}
              placeholder="Select a job and generate a cover letter…"
              aria-busy={isGenerating}
            />
            {draft ? (
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  disabled={saveMutation.isPending}
                  onClick={() => saveMutation.mutate()}
                >
                  {saveFlash ? (
                    <Check
                      className={cn("mr-1.5 size-4 text-emerald-600", motionStatusEnter)}
                      aria-hidden
                    />
                  ) : (
                    <Save className="mr-1.5 size-4" aria-hidden />
                  )}
                  {saveMutation.isPending ? "Saving…" : saveFlash ? "Saved" : "Save edits"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={duplicateMutation.isPending}
                  onClick={() => duplicateMutation.mutate()}
                >
                  <Copy className="mr-1.5 size-4" aria-hidden />
                  Duplicate
                </Button>
              </div>
            ) : null}
            {draft && paragraphs.length > 0 ? (
              <ParagraphControls
                paragraphs={paragraphs}
                lockedParagraphs={lockedParagraphs}
                onToggleLock={toggleLock}
                onRegenerate={(index) => regenMutation.mutate(index)}
                regenPendingIndex={regenIndex}
                disabled={isGenerating || !jobId}
              />
            ) : null}
          </CardContent>
        </Card>

        {coverage?.explain && coverage.explain.length > 0 ? (
          <Card className={surface.workspace}>
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
        ) : null}
      </div>
    </div>
  );
}
