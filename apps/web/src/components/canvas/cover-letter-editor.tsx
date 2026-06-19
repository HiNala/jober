"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { KeywordCoveragePanel } from "@/components/documents/keyword-coverage-panel";
import { LlmBudgetExceeded } from "@/components/documents/llm-budget-exceeded";
import { LlmProviderBanner } from "@/components/documents/llm-provider-banner";
import { ParagraphControls } from "@/components/documents/paragraph-controls";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  documentDownloadUrl,
  duplicateCoverLetter,
  generateCoverLetter,
  patchCoverLetter,
} from "@/lib/api/documents";
import { formatApiError, isApiBudgetExceeded } from "@/lib/api/errors";
import { fetchLlmConfig } from "@/lib/api/llm";
import { useUnsavedChanges } from "@/lib/forms/use-unsaved-changes";
import { coverLetterDownloadFilename } from "@/lib/documents/download-filename";
import { splitParagraphs } from "@/lib/documents/merge-paragraphs";
import { motionShimmer, motionStatusEnter } from "@/lib/design/motion";
import type { ReviewPackage } from "@/lib/api/verification";
import { cn } from "@/lib/utils";

type CoverLetter = NonNullable<ReviewPackage["cover_letter"]>;

export function CoverLetterEditor({
  cover,
  jobTargetId,
  runId,
  company,
  role,
}: {
  cover: CoverLetter;
  jobTargetId: string;
  runId: string;
  company?: string;
  role?: string;
}) {
  const queryClient = useQueryClient();
  const [letterText, setLetterText] = useState(cover.text);
  const [lockedParagraphs, setLockedParagraphs] = useState<Set<number>>(
    () => new Set(cover.locked_paragraphs ?? []),
  );
  const [budgetError, setBudgetError] = useState<string | null>(null);
  const [saveFlash, setSaveFlash] = useState(false);
  const [regenIndex, setRegenIndex] = useState<number | null>(null);

  useUnsavedChanges(letterText !== cover.text);

  const llmQuery = useQuery({ queryKey: ["llm-config"], queryFn: fetchLlmConfig });
  const paragraphs = splitParagraphs(letterText);
  const coverage = cover.keyword_coverage;
  const downloadCompany = company ?? "company";
  const downloadRole = role ?? "role";

  useEffect(() => {
    if (!saveFlash) return;
    const timer = setTimeout(() => setSaveFlash(false), 2000);
    return () => clearTimeout(timer);
  }, [saveFlash]);

  const saveMutation = useMutation({
    mutationFn: () =>
      patchCoverLetter(cover.id, {
        text: letterText,
        locked_paragraphs: [...lockedParagraphs],
      }),
    onSuccess: async () => {
      setSaveFlash(true);
      toast.success("Letter saved — ATS score updated");
      await queryClient.invalidateQueries({ queryKey: ["review-package-run", runId] });
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not save letter")),
  });

  const regenMutation = useMutation({
    mutationFn: (paragraphIndex: number) => {
      setRegenIndex(paragraphIndex);
      return generateCoverLetter(jobTargetId, {
        force: true,
        runId,
        seedText: letterText,
        lockedParagraphs: [...lockedParagraphs],
        regenerateParagraphIndex: paragraphIndex,
        templateStyle: cover.template_style,
        voicePreset: cover.voice_preset,
      });
    },
    onSuccess: async (doc) => {
      setLetterText(doc.text);
      setLockedParagraphs(new Set(doc.locked_paragraphs ?? []));
      setBudgetError(null);
      toast.success("Paragraph regenerated");
      await queryClient.invalidateQueries({ queryKey: ["review-package-run", runId] });
    },
    onError: (err: unknown) => {
      if (isApiBudgetExceeded(err)) {
        setBudgetError(formatApiError(err));
        return;
      }
      toast.error(formatApiError(err, "Regeneration failed"));
    },
    onSettled: () => setRegenIndex(null),
  });

  const duplicateMutation = useMutation({
    mutationFn: () => duplicateCoverLetter(cover.id, jobTargetId),
    onSuccess: () => toast.success("Duplicated as a new version"),
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not duplicate")),
  });

  const toggleLock = (index: number) => {
    setLockedParagraphs((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const isGenerating = regenMutation.isPending;

  return (
    <div className="space-y-4">
      <LlmProviderBanner provider={llmQuery.data?.provider} />
      {budgetError ? (
        <LlmBudgetExceeded message={budgetError} onDismiss={() => setBudgetError(null)} />
      ) : null}

      <div className="flex flex-wrap items-center gap-2">
        {cover.template_style ? <Badge variant="secondary">{cover.template_style}</Badge> : null}
        {cover.voice_preset ? (
          <Badge variant="outline">{cover.voice_preset.replace(/_/g, " ")}</Badge>
        ) : null}
        {cover.version ? (
          <Badge variant="outline" className="tabular-nums">
            v{cover.version}
          </Badge>
        ) : null}
      </div>

      <KeywordCoveragePanel atsScore={cover.ats_score ?? 0} coverage={coverage} />

      <Textarea
        value={letterText}
        onChange={(e) => setLetterText(e.target.value)}
        rows={14}
        className={cn(
          "font-sans text-sm leading-relaxed",
          isGenerating && motionShimmer,
        )}
        aria-busy={isGenerating}
      />

      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
          {saveFlash ? (
            <Check className={cn("mr-1.5 size-4 text-emerald-600", motionStatusEnter)} aria-hidden />
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
        {cover.pdf_download_path ? (
          <a
            href={documentDownloadUrl(cover.pdf_download_path)}
            download={coverLetterDownloadFilename(downloadCompany, downloadRole, "pdf")}
            className="inline-flex h-8 items-center rounded-md border border-border px-3 text-xs font-medium hover:bg-muted"
          >
            Download PDF
          </a>
        ) : null}
      </div>

      <ParagraphControls
        paragraphs={paragraphs}
        lockedParagraphs={lockedParagraphs}
        onToggleLock={toggleLock}
        onRegenerate={(index) => regenMutation.mutate(index)}
        regenPendingIndex={regenIndex}
        disabled={isGenerating}
      />
    </div>
  );
}
