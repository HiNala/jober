"use client";

import type { JobTargetRead } from "@jober/schemas";
import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ImportWizard } from "@/components/import/import-wizard";
import { QueuePolicyBanner } from "@/components/queue/queue-policy-banner";
import { JobDataTable } from "@/components/jobs/job-data-table";
import { JobDetailDrawer } from "@/components/jobs/job-detail-drawer";
import { JobKanban } from "@/components/jobs/job-kanban";
import { PageError, PageLoading } from "@/components/states/page-states";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { exportJobsXlsxUrl, fetchJobTargets } from "@/lib/api/jobs";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export default function QueuePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const importParam = searchParams.get("import") === "1";
  const openJobId = searchParams.get("job");
  const [importOpen, setImportOpen] = useState(importParam);
  const [prevImportParam, setPrevImportParam] = useState(importParam);
  const [kanbanDetail, setKanbanDetail] = useState<JobTargetRead | null>(null);

  if (importParam !== prevImportParam) {
    setPrevImportParam(importParam);
    if (importParam) {
      setImportOpen(true);
    }
  }

  useEffect(() => {
    if (importParam) {
      router.replace("/queue");
    }
  }, [importParam, router]);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["job-targets"],
    queryFn: () => fetchJobTargets(),
  });

  const rows = data ?? [];

  return (
    <div className={cn(spacing.page, spacing.section)}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Job queue</h1>
          <p className="text-sm text-muted-foreground">
            {rows.length} targets · import here or add jobs via{" "}
            <Link href="/discover" className="underline underline-offset-2">
              Discover
            </Link>
          </p>
        </div>
        <div className="flex gap-2">
          <a
            href={exportJobsXlsxUrl()}
            download
            className="inline-flex h-7 items-center gap-1 rounded-[min(var(--radius-md),12px)] border border-border bg-background px-2.5 text-[0.8rem] font-medium hover:bg-muted"
          >
            <Download className="size-3.5" aria-hidden />
            Export XLSX
          </a>
          <Button size="sm" type="button" onClick={() => setImportOpen(true)}>
            Import spreadsheet
          </Button>
          <Dialog open={importOpen} onOpenChange={setImportOpen}>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Import job tracker</DialogTitle>
              </DialogHeader>
              <ImportWizard />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <QueuePolicyBanner />

      {isLoading && <PageLoading label="Loading job targets…" />}
      {isError && (
        <PageError
          title="Could not load queue"
          message="Check that the API is running and NEXT_PUBLIC_API_URL is set."
          onRetry={() => void refetch()}
        />
      )}

      {!isLoading && !isError && (
        <Tabs defaultValue="table">
          <TabsList>
            <TabsTrigger value="table">Table</TabsTrigger>
            <TabsTrigger value="board">Board</TabsTrigger>
          </TabsList>
          <TabsContent value="table" className="mt-4">
            <JobDataTable
              rows={rows}
              openJobId={openJobId}
              onImportClick={() => setImportOpen(true)}
            />
          </TabsContent>
          <TabsContent value="board" className="mt-4">
            <JobKanban rows={rows} onSelect={setKanbanDetail} />
          </TabsContent>
        </Tabs>
      )}

      <JobDetailDrawer
        job={kanbanDetail}
        open={kanbanDetail !== null}
        onOpenChange={(open) => !open && setKanbanDetail(null)}
      />
    </div>
  );
}
