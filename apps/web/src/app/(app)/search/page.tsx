"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";

import { PageEmpty, PageError, PageLoading } from "@/components/states/page-states";
import { PageHeader } from "@/components/app-shell/page-header";
import { Input } from "@/components/ui/input";
import { searchLibrary } from "@/lib/api/library";
import { spacing, surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function SearchResults({ initialQ }: { initialQ: string }) {
  const [query, setQuery] = useState(initialQ);

  const searchQuery = useQuery({
    queryKey: ["library-search", query],
    queryFn: () => searchLibrary(query.trim()),
    enabled: query.trim().length > 0,
  });

  return (
    <div className={cn(spacing.page, spacing.section)}>
      <PageHeader
        title="Search library"
        description={
          <>
            Find jobs, cover letters, runs, and saved lists you already have — not the same as{" "}
            <Link href="/discover" className="text-primary underline-offset-4 hover:underline">
              Discover
            </Link>{" "}
            (add new jobs from boards or a spreadsheet).
          </>
        }
      />

      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search jobs, letters, runs…"
        aria-label="Search library"
        autoFocus
      />

      {searchQuery.isFetching ? <p className="text-sm text-muted-foreground">Searching…</p> : null}

      {searchQuery.isError && query.trim() ? (
        <PageError
          title="Search failed"
          message="Could not reach the server. Check your connection and try again."
          onRetry={() => void searchQuery.refetch()}
        />
      ) : null}

      {!query.trim() ? (
        <PageEmpty
          title="Search your workspace"
          description="Find jobs, cover letters, runs, and saved lists. Start typing to search across everything you have imported."
        />
      ) : null}

      {searchQuery.data && query.trim() ? (
        <div className="grid gap-6 md:grid-cols-2">
          <SearchGroup title="Jobs" empty={searchQuery.data.jobs.length === 0}>
            {searchQuery.data.jobs.map((job) => (
              <li key={job.id}>
                <Link href={`/queue?job=${job.id}`} className="hover:underline">
                  {job.company} — {job.role}
                </Link>
              </li>
            ))}
          </SearchGroup>
          <SearchGroup title="Cover letters" empty={searchQuery.data.cover_letters.length === 0}>
            {searchQuery.data.cover_letters.map((letter) => (
              <li key={letter.id}>
                <Link href="/library?tab=letters" className="hover:underline">
                  {letter.company} — {letter.role}
                </Link>
              </li>
            ))}
          </SearchGroup>
          <SearchGroup title="Runs" empty={searchQuery.data.runs.length === 0}>
            {searchQuery.data.runs.map((run) => (
              <li key={run.id}>
                <Link href={`/runs/${run.id}`} className="hover:underline">
                  {run.company} — {run.status}
                </Link>
              </li>
            ))}
          </SearchGroup>
          <SearchGroup title="Lists" empty={searchQuery.data.lists.length === 0}>
            {searchQuery.data.lists.map((list) => (
              <li key={list.id}>
                <Link href="/library?tab=jobs" className="hover:underline">
                  {list.name}
                </Link>
              </li>
            ))}
          </SearchGroup>
        </div>
      ) : null}
    </div>
  );
}

function SearchGroup({
  title,
  empty,
  children,
}: {
  title: string;
  empty: boolean;
  children: ReactNode;
}) {
  return (
    <section className={cn(surface.workspace, "p-4")}>
      <h2 className="text-sm font-semibold tracking-tight">{title}</h2>
      {empty ? (
        <p className="mt-2 text-sm text-muted-foreground">No matches</p>
      ) : (
        <ul className="mt-2 space-y-1 text-sm">{children}</ul>
      )}
    </section>
  );
}

function SearchPageInner() {
  const params = useSearchParams();
  const urlQ = params.get("q") ?? "";
  return <SearchResults key={urlQ} initialQ={urlQ} />;
}

export default function SearchPage() {
  return (
    <Suspense fallback={<PageLoading label="Loading search…" />}>
      <SearchPageInner />
    </Suspense>
  );
}
