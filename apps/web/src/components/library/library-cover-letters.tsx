"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, Lock, LockOpen } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { DocumentStudio } from "@/components/documents/document-studio";
import { PageEmpty } from "@/components/states/page-states";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  coverLetterPdfUrl,
  duplicateLibraryCoverLetter,
  fetchLibraryCoverLetters,
  lockCoverLetterTemplate,
} from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const LETTER_VIEWS = [
  { id: "saved", label: "Saved letters" },
  { id: "studio", label: "Document Studio" },
] as const;

type LetterViewId = (typeof LETTER_VIEWS)[number]["id"];

function SavedCoverLetters() {
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
    <>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h2 id="library-letters-heading" className="text-sm font-medium">
          Saved letters
        </h2>
        {(lettersQuery.data?.length ?? 0) > 0 ? (
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by company or role…"
            aria-label="Filter cover letters"
            className="max-w-xs"
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
          description="Open Document Studio, pick a job, tailor the letter to the role, then find every version here."
          action={
            <Link href="/library?tab=letters&view=studio" className={buttonVariants({ size: "sm" })}>
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
    </>
  );
}

export function LibraryCoverLetters() {
  const params = useSearchParams();
  const view = (params.get("view") as LetterViewId | null) ?? "saved";

  return (
    <section
      aria-labelledby="library-letters-heading"
      aria-label={view === "studio" ? "Document Studio" : "Cover letters"}
      className="space-y-4"
    >
      <nav aria-label="Cover letter views" className="flex flex-wrap gap-2">
        {LETTER_VIEWS.map((item) => (
          <Link
            key={item.id}
            href={`/library?tab=letters&view=${item.id}`}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              view === item.id
                ? "bg-muted text-foreground"
                : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
            )}
            aria-current={view === item.id ? "page" : undefined}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {view === "studio" ? (
        <>
          <h2 id="library-letters-heading" className="sr-only">
            Document Studio
          </h2>
          <DocumentStudio />
        </>
      ) : (
        <SavedCoverLetters />
      )}
    </section>
  );
}
