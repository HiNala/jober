"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { buttonVariants } from "@/components/ui/button";
import { fetchLibraryRuns } from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LibraryRuns() {
  const runsQuery = useQuery({
    queryKey: ["library", "runs"],
    queryFn: async () => (await fetchLibraryRuns()).items,
  });

  return (
    <section aria-labelledby="library-runs-heading" className="space-y-4">
      <h2 id="library-runs-heading" className="text-sm font-medium">
        Run history
      </h2>

      {runsQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading runs…</p>
      ) : null}
      {runsQuery.data?.length === 0 ? (
        <p className={cn(surface.card, "rounded-lg p-4 text-sm text-muted-foreground")}>
          Past application runs appear here with status and outcomes. Start from the queue to create one.
        </p>
      ) : null}

      <ul className="space-y-2">
        {runsQuery.data?.map((run) => (
          <li
            key={run.id}
            className={cn(surface.card, "flex flex-wrap items-center justify-between gap-3 rounded-lg p-4")}
          >
            <div>
              <p className="font-medium">
                {run.company} — {run.role}
              </p>
              <p className="text-xs text-muted-foreground">
                {run.status.replace(/_/g, " ")} · {run.policy.replace(/_/g, " ")} ·{" "}
                {new Date(run.updated_at).toLocaleString()}
              </p>
            </div>
            <Link
              href={`/runs/${run.id}`}
              className={buttonVariants({ size: "sm", variant: "outline" })}
            >
              Open in canvas
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
