"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, Lock, LockOpen } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import Link from "next/link";

import { PageEmpty } from "@/components/states/page-states";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import {
  coverLetterPdfUrl,
  duplicateLibraryCoverLetter,
  fetchLibraryCoverLetters,
  lockCoverLetterTemplate,
} from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LibraryCoverLetters() {
  const [filter, setFilter] = useState("");
  const queryClient = useQueryClient();
  const lettersQuery = useQuery({
    queryKey: ["library", "cover-letters", filter],
    queryFn: async () => (await fetchLibraryCoverLetters(filter || undefined)).items,
  });

  const lockMutation = useMutation({
    mutationFn: ({ id, locked }: { id: string; locked: boolean }) =>
      lockCoverLetterTemplate(id, locked),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["library", "cover-letters"] });
    },
  });

  const duplicateMutation = useMutation({
    mutationFn: (id: string) => duplicateLibraryCoverLetter(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["library", "cover-letters"] });
      toast.success("Duplicated letter as a new version");
    },
    onError: () => toast.error("Could not duplicate letter"),
  });

  return (
    <section aria-labelledby="library-letters-heading" className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h2 id="library-letters-heading" className="text-sm font-medium">
          Cover letters
        </h2>
        {(lettersQuery.data?.length ?? 0) > 0 ? (
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by company or role…"
            className="max-w-xs"
            aria-label="Filter cover letters"
          />
        ) : null}
      </div>

      {lettersQuery.isLoading ? (
        <div className="space-y-2" aria-busy="true">
          <Skeleton className="h-24 w-full rounded-lg" />
          <Skeleton className="h-24 w-full rounded-lg" />
        </div>
      ) : null}
      {!lettersQuery.isLoading && lettersQuery.data?.length === 0 ? (
        <PageEmpty
          title="Generate your first cover letter"
          description="Pick a job in Document Studio, tailor the letter to the role, then find every version here."
          action={
            <Link href="/documents" className={buttonVariants({ size: "sm" })}>
              Open Document Studio
            </Link>
          }
        />
      ) : null}

      <ul className="space-y-2">
        {lettersQuery.data?.map((letter) => (
          <li key={letter.id} className={cn(surface.workspace, "rounded-lg p-4")}>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="font-medium">
                  {letter.company} — {letter.role}
                </p>
                <p className="text-xs text-muted-foreground">
                  {letter.generated_at
                    ? new Date(letter.generated_at).toLocaleString()
                    : "Draft"}
                  {letter.ats_score != null ? ` · ATS ${Math.round(letter.ats_score)}%` : ""}
                </p>
              </div>
              <div className="flex gap-2">
                <a
                  href={coverLetterPdfUrl(letter.id)}
                  target="_blank"
                  rel="noreferrer"
                  className={buttonVariants({ size: "sm", variant: "outline" })}
                >
                  Open PDF
                </a>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={duplicateMutation.isPending}
                  onClick={() => duplicateMutation.mutate(letter.id)}
                >
                  <Copy className="mr-1 size-3.5" aria-hidden />
                  Duplicate
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  disabled={lockMutation.isPending}
                  onClick={() =>
                    lockMutation.mutate({ id: letter.id, locked: !letter.is_template })
                  }
                >
                  {letter.is_template ? (
                    <>
                      <Lock className="mr-1 size-3.5" aria-hidden />
                      Template
                    </>
                  ) : (
                    <>
                      <LockOpen className="mr-1 size-3.5" aria-hidden />
                      Lock template
                    </>
                  )}
                </Button>
              </div>
            </div>
            <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{letter.preview}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
