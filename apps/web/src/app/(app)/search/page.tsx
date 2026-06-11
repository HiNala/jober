"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";

import { PageEmpty } from "@/components/states/page-states";
import { Input } from "@/components/ui/input";
import { searchLibrary } from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function SearchResults({ initialQ }: { initialQ: string }) {
  const [query, setQuery] = useState(initialQ);

  const searchQuery = useQuery({
    queryKey: ["library-search", query],
    queryFn: () => searchLibrary(query.trim()),
    enabled: query.trim().length > 0,
  });

  return (
    <div className="space-y-6 p-4 md:p-6">
      <header>
        <h1 className="text-xl font-semibold tracking-tight">Search library</h1>
        <p className="text-sm text-muted-foreground">
          Find jobs, cover letters, runs, and saved lists across your workspace.
        </p>
      </header>

      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search jobs, letters, runs…"
        aria-label="Search library"
        autoFocus
      />

      {searchQuery.isFetching ? <p className="text-sm text-muted-foreground">Searching…</p> : null}

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
                <Link href="/queue" className="hover:underline">
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
    <section className={cn(surface.card, "rounded-lg p-4")}>
      <h2 className="text-sm font-medium">{title}</h2>
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
    <Suspense fallback={<div className="p-6 text-sm text-muted-foreground">Loading search…</div>}>
      <SearchPageInner />
    </Suspense>
  );
}
