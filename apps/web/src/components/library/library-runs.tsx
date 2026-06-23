"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { PageEmpty } from "@/components/states/page-states";
import { buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchLibraryRuns } from "@/lib/api/library";
import { formatDateTime } from "@/lib/format/date-time";
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
        <div className="space-y-2" aria-busy="true">
          <Skeleton className="h-16 w-full rounded-lg" />
          <Skeleton className="h-16 w-full rounded-lg" />
        </div>
      ) : null}
      {!runsQuery.isLoading && runsQuery.data?.length === 0 ? (
        <PageEmpty
          title="No runs yet"
          description="Launch a dry-run or review batch from the queue to watch Jober work — outcomes land here."
          action={
            <Link href="/queue" className={buttonVariants({ size: "sm" })}>
              Open queue
            </Link>
          }
        />
      ) : null}

      <ul className="space-y-2">
        {runsQuery.data?.map((run) => (
          <li
            key={run.id}
            className={cn(surface.workspace, "flex flex-wrap items-center justify-between gap-3 rounded-lg p-4")}
          >
            <div>
              <p className="font-medium">
                {run.company} — {run.role}
              </p>
              <p className="text-xs text-muted-foreground">
                {run.status.replace(/_/g, " ")} · {run.policy.replace(/_/g, " ")} ·{" "}
                {formatDateTime(run.updated_at)}
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
