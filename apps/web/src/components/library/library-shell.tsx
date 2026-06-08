"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { LibraryCoverLetters } from "@/components/library/library-cover-letters";
import { LibraryJobLists } from "@/components/library/library-job-lists";
import { LibraryResumes } from "@/components/library/library-resumes";
import { LibraryRuns } from "@/components/library/library-runs";
import { cn } from "@/lib/utils";

const TABS = [
  { id: "resumes", label: "Resumes" },
  { id: "letters", label: "Cover letters" },
  { id: "jobs", label: "Saved jobs" },
  { id: "runs", label: "Runs" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function LibraryShellInner() {
  const params = useSearchParams();
  const tab = (params.get("tab") as TabId | null) ?? "resumes";

  return (
    <div className="space-y-6 p-4 md:p-6">
      <header>
        <h1 className="text-xl font-semibold tracking-tight">Library</h1>
        <p className="text-sm text-muted-foreground">
          Resumes, cover letters, saved job lists, and run history — your application assets in one place.
        </p>
      </header>

      <nav aria-label="Library sections" className="flex flex-wrap gap-2 border-b pb-2">
        {TABS.map((item) => (
          <Link
            key={item.id}
            href={`/library?tab=${item.id}`}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              tab === item.id
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
            aria-current={tab === item.id ? "page" : undefined}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {tab === "resumes" ? <LibraryResumes /> : null}
      {tab === "letters" ? <LibraryCoverLetters /> : null}
      {tab === "jobs" ? <LibraryJobLists /> : null}
      {tab === "runs" ? <LibraryRuns /> : null}
    </div>
  );
}

export function LibraryShell() {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">Loading library…</div>}>
      <LibraryShellInner />
    </Suspense>
  );
}
