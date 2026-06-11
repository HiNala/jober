"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileUp, Star } from "lucide-react";
import { useRef } from "react";

import { PageEmpty } from "@/components/states/page-states";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { activateResume, fetchLibraryResumes, uploadResumeFile } from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LibraryResumes() {
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const resumesQuery = useQuery({
    queryKey: ["library", "resumes"],
    queryFn: async () => (await fetchLibraryResumes()).items,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadResumeFile,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["library", "resumes"] });
    },
  });

  const activateMutation = useMutation({
    mutationFn: activateResume,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["library", "resumes"] });
    },
  });

  return (
    <section aria-labelledby="library-resumes-heading" className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="library-resumes-heading" className="text-sm font-medium">
          Resume versions
        </h2>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={() => inputRef.current?.click()}
          disabled={uploadMutation.isPending}
        >
          <FileUp className="mr-2 size-4" aria-hidden />
          Upload resume
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="sr-only"
          aria-label="Upload resume file"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void uploadMutation.mutate(file);
            event.target.value = "";
          }}
        />
      </div>

      {resumesQuery.isLoading ? (
        <div className="space-y-2" aria-busy="true">
          <Skeleton className="h-20 w-full rounded-lg" />
          <Skeleton className="h-20 w-full rounded-lg" />
        </div>
      ) : null}
      {!resumesQuery.isLoading && resumesQuery.data?.length === 0 ? (
        <PageEmpty
          title="Upload your canonical resume"
          description="PDF or DOCX — parsed skills feed cover letters and claims checks across every job."
          action={
            <Button
              type="button"
              size="sm"
              onClick={() => inputRef.current?.click()}
              disabled={uploadMutation.isPending}
            >
              <FileUp className="mr-2 size-4" aria-hidden />
              Choose file
            </Button>
          }
        />
      ) : null}

      <ul className="space-y-2">
        {resumesQuery.data?.map((resume) => (
          <li
            key={resume.id}
            className={cn(surface.workspace, "flex flex-wrap items-start justify-between gap-3 rounded-lg p-4")}
          >
            <div className="min-w-0">
              <p className="font-medium">{resume.original_filename}</p>
              <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                {resume.extracted_text_preview || "No extracted text"}
              </p>
              {resume.skills.length > 0 ? (
                <p className="mt-2 text-xs text-muted-foreground">
                  {resume.skills.slice(0, 8).join(" · ")}
                </p>
              ) : null}
            </div>
            <div className="flex items-center gap-2">
              {resume.is_active ? (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-primary">
                  <Star className="size-3.5 fill-current" aria-hidden />
                  Active
                </span>
              ) : (
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  disabled={activateMutation.isPending}
                  onClick={() => activateMutation.mutate(resume.id)}
                >
                  Set active
                </Button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
