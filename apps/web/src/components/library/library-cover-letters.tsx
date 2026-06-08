"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Lock, LockOpen } from "lucide-react";
import { useState } from "react";

import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  coverLetterPdfUrl,
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

  return (
    <section aria-labelledby="library-letters-heading" className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h2 id="library-letters-heading" className="text-sm font-medium">
          Cover letters
        </h2>
        <Input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter by company or role…"
          className="max-w-xs"
          aria-label="Filter cover letters"
        />
      </div>

      {lettersQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading cover letters…</p>
      ) : null}
      {lettersQuery.data?.length === 0 ? (
        <p className={cn(surface.card, "rounded-lg p-4 text-sm text-muted-foreground")}>
          Generated cover letters appear here after you run document generation on a job.
        </p>
      ) : null}

      <ul className="space-y-2">
        {lettersQuery.data?.map((letter) => (
          <li key={letter.id} className={cn(surface.card, "rounded-lg p-4")}>
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
