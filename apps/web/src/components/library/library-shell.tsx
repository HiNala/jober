"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { LibraryCoverLetters } from "@/components/library/library-cover-letters";
import { LibraryJobLists } from "@/components/library/library-job-lists";
import { LibraryResumes } from "@/components/library/library-resumes";
import { LibraryRuns } from "@/components/library/library-runs";
import { PageLoading } from "@/components/states/page-states";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const TABS = [
  { id: "resumes", label: "Resumes" },
  { id: "letters", label: "Cover letters" },
  { id: "jobs", label: "Saved jobs" },
  { id: "runs", label: "Runs" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function LibraryShellInner() {
  const router = useRouter();
  const params = useSearchParams();
  const tab = (params.get("tab") as TabId | null) ?? "resumes";

  function handleTabChange(value: string) {
    router.push(`/library?tab=${value}`, { scroll: false });
  }

  return (
    <div className={cn(spacing.page, spacing.section)}>
      <header>
        <h1 className="text-xl font-semibold tracking-tight">Library</h1>
        <p className="text-sm text-muted-foreground">
          Resumes, cover letters, saved job lists, and run history — your application assets in one
          place.
        </p>
      </header>

      <Tabs value={tab} onValueChange={handleTabChange}>
        <TabsList>
          {TABS.map((item) => (
            <TabsTrigger key={item.id} value={item.id}>
              {item.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="resumes" className="mt-4">
          <LibraryResumes />
        </TabsContent>
        <TabsContent value="letters" className="mt-4">
          <LibraryCoverLetters />
        </TabsContent>
        <TabsContent value="jobs" className="mt-4">
          <LibraryJobLists />
        </TabsContent>
        <TabsContent value="runs" className="mt-4">
          <LibraryRuns />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export function LibraryShell() {
  return (
    <Suspense fallback={<PageLoading label="Loading library…" />}>
      <LibraryShellInner />
    </Suspense>
  );
}
