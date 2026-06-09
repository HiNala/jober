"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Save } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import {
  documentDownloadUrl,
  generateCoverLetter,
  patchCoverLetter,
} from "@/lib/api/documents";
import { formatApiError } from "@/lib/api/errors";
import type { ReviewPackage } from "@/lib/api/verification";

type CoverLetter = NonNullable<ReviewPackage["cover_letter"]>;

export function CoverLetterEditor({
  cover,
  jobTargetId,
  runId,
}: {
  cover: CoverLetter;
  jobTargetId: string;
  runId: string;
}) {
  const queryClient = useQueryClient();
  const [letterText, setLetterText] = useState(cover.text);
  const [lockedParagraphs, setLockedParagraphs] = useState<Set<number>>(
    () => new Set(cover.locked_paragraphs ?? []),
  );

  const paragraphs = letterText.split("\n\n").filter((part) => part.trim());
  const coverage = cover.keyword_coverage;

  const saveMutation = useMutation({
    mutationFn: () =>
      patchCoverLetter(cover.id, {
        text: letterText,
        locked_paragraphs: [...lockedParagraphs],
      }),
    onSuccess: async () => {
      toast.success("Letter saved — ATS score updated");
      await queryClient.invalidateQueries({ queryKey: ["review-package-run", runId] });
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not save letter")),
  });

  const regenMutation = useMutation({
    mutationFn: (paragraphIndex: number) =>
      generateCoverLetter(jobTargetId, {
        force: true,
        runId,
        seedText: letterText,
        lockedParagraphs: [...lockedParagraphs],
        regenerateParagraphIndex: paragraphIndex,
        templateStyle: cover.template_style,
        voicePreset: cover.voice_preset,
      }),
    onSuccess: async (doc) => {
      setLetterText(doc.text);
      toast.success("Paragraph regenerated");
      await queryClient.invalidateQueries({ queryKey: ["review-package-run", runId] });
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Regeneration failed")),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <Progress value={cover.ats_score ?? 0} className="max-w-xs flex-1" />
        <span className="text-sm font-medium tabular-nums">{cover.ats_score ?? 0}% ATS</span>
        {cover.template_style ? <Badge variant="secondary">{cover.template_style}</Badge> : null}
        {cover.voice_preset ? (
          <Badge variant="outline">{cover.voice_preset.replace(/_/g, " ")}</Badge>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-1">
        {coverage?.present?.map((kw) => (
          <Badge key={kw} variant="secondary" className="font-normal">
            {kw}
          </Badge>
        ))}
        {coverage?.missing?.map((kw) => (
          <Badge key={kw} variant="outline" className="font-normal text-muted-foreground">
            missing: {kw}
          </Badge>
        ))}
      </div>
      <Textarea
        value={letterText}
        onChange={(e) => setLetterText(e.target.value)}
        rows={14}
        className="font-sans text-sm leading-relaxed"
      />
      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
          <Save className="mr-1.5 size-4" aria-hidden />
          Save edits
        </Button>
        {cover.pdf_download_path ? (
          <a
            href={documentDownloadUrl(cover.pdf_download_path)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-8 items-center rounded-md border border-border px-3 text-xs font-medium hover:bg-muted"
          >
            Open PDF
          </a>
        ) : null}
      </div>
      <div className="space-y-2 border-t border-border pt-3">
        <p className="text-xs font-medium text-muted-foreground">Paragraph controls</p>
        {paragraphs.map((para, index) => (
          <div
            key={index}
            className="flex flex-wrap items-start justify-between gap-2 rounded-md border border-border/50 p-2"
          >
            <p className="line-clamp-2 flex-1 text-xs text-muted-foreground">{para}</p>
            <div className="flex gap-2">
              <Button
                type="button"
                size="sm"
                variant={lockedParagraphs.has(index) ? "default" : "outline"}
                onClick={() => {
                  setLockedParagraphs((prev) => {
                    const next = new Set(prev);
                    if (next.has(index)) next.delete(index);
                    else next.add(index);
                    return next;
                  });
                }}
              >
                {lockedParagraphs.has(index) ? "Locked" : "Lock"}
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={lockedParagraphs.has(index) || regenMutation.isPending}
                onClick={() => regenMutation.mutate(index)}
              >
                <RefreshCw className="mr-1 size-3.5" aria-hidden />
                Regen
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
