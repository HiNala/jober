"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Compass, Upload } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { CandidateReview } from "@/components/discover/candidate-review";
import { DiscoverSearchPanel } from "@/components/discover/discover-search-panel";
import { DiscoverUploadPanel } from "@/components/discover/discover-upload-panel";
import { ListBuilderPanel } from "@/components/discover/list-builder-panel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  acceptDiscoveryCandidates,
  refreshDiscoveryList,
  type DiscoveryCandidate,
  type DiscoverySearchQuery,
} from "@/lib/api/discovery";
import { createJobList, fetchJobLists } from "@/lib/api/library";
import { track } from "@/lib/analytics/events";
import { BatchPreviewDialog } from "@/components/batches/batch-preview-dialog";
import { spacing, surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function DiscoverShell() {
  const queryClient = useQueryClient();
  const [activeListId, setActiveListId] = useState<string | null>(null);
  const [newListName, setNewListName] = useState("Priority A");
  const [priority, setPriority] = useState("A");
  const [fitLane, setFitLane] = useState("");
  const [candidates, setCandidates] = useState<DiscoveryCandidate[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());
  const [lastQuery, setLastQuery] = useState<DiscoverySearchQuery>({});
  const [batchPreviewOpen, setBatchPreviewOpen] = useState(false);

  const listsQuery = useQuery({
    queryKey: ["library", "job-lists"],
    queryFn: async () => (await fetchJobLists()).items,
  });

  const createListMutation = useMutation({
    mutationFn: () => createJobList(newListName.trim()),
    onSuccess: async (list) => {
      track("library.list_created", {});
      setActiveListId(list.id);
      await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
      toast.success(`Created list "${list.name}"`);
    },
  });

  const acceptMutation = useMutation({
    mutationFn: async () => {
      if (!activeListId) throw new Error("Select or create a target list first");
      const selected = candidates.filter((c) => selectedKeys.has(c.candidate_key));
      if (selected.length === 0) throw new Error("Select at least one candidate");
      return acceptDiscoveryCandidates({
        list_id: activeListId,
        candidates: selected,
        priority: priority || undefined,
        fit_lane: fitLane || undefined,
      });
    },
    onSuccess: async (result) => {
      track("library.candidates_accepted", { count: result.accepted });
      toast.success(`Added ${result.accepted} job${result.accepted === 1 ? "" : "s"} to your list`);
      setSelectedKeys(new Set());
      await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
      await queryClient.invalidateQueries({ queryKey: ["job-targets"] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const refreshMutation = useMutation({
    mutationFn: async () => {
      if (!activeListId) throw new Error("Select a list to refresh");
      return refreshDiscoveryList(activeListId);
    },
    onSuccess: (data) => {
      setCandidates(data.candidates);
      setSelectedKeys(new Set(data.candidates.map((c) => c.candidate_key)));
      toast.success(
        data.candidates.length
          ? `Found ${data.candidates.length} new candidate${data.candidates.length === 1 ? "" : "s"}`
          : "No new openings since your last check",
      );
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const batchFilters = activeListId
    ? { job_list_id: activeListId, status: "new", limit: 50 }
    : null;

  const handleSearchResults = (rows: DiscoveryCandidate[], query: DiscoverySearchQuery) => {
    setCandidates(rows);
    setLastQuery(query);
    setSelectedKeys(new Set());
  };

  return (
    <div className={cn(spacing.page, spacing.section)}>
      <header className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight">Discover & build lists</h1>
        <p className="text-sm text-muted-foreground">
          Add new jobs from boards or a spreadsheet — not the same as{" "}
          <Link href="/search" className="underline underline-offset-2">
            Search library
          </Link>{" "}
          (find items you already imported).
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-4">
          <Tabs defaultValue="search">
            <TabsList>
              <TabsTrigger value="search">
                <Compass className="mr-1.5 size-4" aria-hidden />
                Search for jobs
              </TabsTrigger>
              <TabsTrigger value="upload">
                <Upload className="mr-1.5 size-4" aria-hidden />
                Upload a list
              </TabsTrigger>
            </TabsList>
            <TabsContent value="search" className="mt-4">
              <DiscoverSearchPanel
                listId={activeListId}
                onResults={handleSearchResults}
                lastQuery={lastQuery}
              />
            </TabsContent>
            <TabsContent value="upload" className="mt-4">
              <DiscoverUploadPanel listId={activeListId} />
            </TabsContent>
          </Tabs>

          <section aria-labelledby="candidates-section-heading" className={cn(surface.workspace, "rounded-lg p-4")}>
            <CandidateReview
              candidates={candidates}
              selectedKeys={selectedKeys}
              onToggle={(key) => {
                setSelectedKeys((prev) => {
                  const next = new Set(prev);
                  if (next.has(key)) next.delete(key);
                  else next.add(key);
                  return next;
                });
              }}
              onToggleAll={(checked) => {
                setSelectedKeys(
                  checked ? new Set(candidates.map((c) => c.candidate_key)) : new Set(),
                );
              }}
            />
          </section>
        </div>

        <ListBuilderPanel
          lists={listsQuery.data ?? []}
          activeListId={activeListId}
          onSelectList={setActiveListId}
          newListName={newListName}
          onNewListNameChange={setNewListName}
          onCreateList={() => {
            if (newListName.trim()) void createListMutation.mutate();
          }}
          priority={priority}
          onPriorityChange={setPriority}
          fitLane={fitLane}
          onFitLaneChange={setFitLane}
          selectedCount={selectedKeys.size}
          onAccept={() => acceptMutation.mutate()}
          acceptPending={acceptMutation.isPending}
          onRefresh={() => refreshMutation.mutate()}
          refreshPending={refreshMutation.isPending}
          onLaunchBatch={() => {
            if (!activeListId) {
              toast.error("Select a list first");
              return;
            }
            setBatchPreviewOpen(true);
          }}
          launchPending={false}
        />
      </div>

      {batchFilters ? (
        <BatchPreviewDialog
          open={batchPreviewOpen}
          onOpenChange={setBatchPreviewOpen}
          filters={batchFilters}
          batchName={`List batch — ${new Date().toLocaleDateString()}`}
          defaultPolicy="review_before_submit"
        />
      ) : null}
    </div>
  );
}
