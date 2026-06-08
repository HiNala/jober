"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createSavedSearch,
  fetchSavedSearches,
  linkListSavedSearch,
  searchDiscovery,
  type DiscoveryCandidate,
  type DiscoverySearchQuery,
} from "@/lib/api/discovery";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

type Props = {
  listId: string | null;
  lastQuery: DiscoverySearchQuery;
  onResults: (candidates: DiscoveryCandidate[], query: DiscoverySearchQuery) => void;
};

export function DiscoverSearchPanel({ listId, lastQuery, onResults }: Props) {
  const queryClient = useQueryClient();
  const [role, setRole] = useState(lastQuery.role ?? "");
  const [stack, setStack] = useState((lastQuery.stack ?? []).join(", "));
  const [location, setLocation] = useState(lastQuery.location ?? "");
  const [stage, setStage] = useState(lastQuery.stage ?? "");
  const [workStyle, setWorkStyle] = useState(lastQuery.work_style ?? "");
  const [boardUrl, setBoardUrl] = useState((lastQuery.board_urls ?? [])[0] ?? "");
  const [saveName, setSaveName] = useState("");

  const savedQuery = useQuery({
    queryKey: ["discovery", "saved-searches"],
    queryFn: async () => (await fetchSavedSearches()).items,
  });

  const searchMutation = useMutation({
    mutationFn: async () => {
      const query: DiscoverySearchQuery = {
        role: role.trim() || undefined,
        stack: stack
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        location: location.trim() || undefined,
        stage: stage.trim() || undefined,
        work_style: workStyle.trim() || undefined,
        board_urls: boardUrl.trim() ? [boardUrl.trim()] : undefined,
        list_id: listId ?? undefined,
      };
      const result = await searchDiscovery(query);
      return { query, candidates: result.candidates };
    },
    onSuccess: ({ query, candidates }) => {
      onResults(candidates, query);
      toast.success(
        candidates.length
          ? `Found ${candidates.length} candidate${candidates.length === 1 ? "" : "s"}`
          : "No matches — try broader filters",
      );
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const query: DiscoverySearchQuery = {
        role: role.trim() || undefined,
        stack: stack
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        location: location.trim() || undefined,
        stage: stage.trim() || undefined,
        work_style: workStyle.trim() || undefined,
        board_urls: boardUrl.trim() ? [boardUrl.trim()] : undefined,
      };
      const saved = await createSavedSearch(saveName.trim(), query);
      if (listId) await linkListSavedSearch(listId, saved.id);
      return saved;
    },
    onSuccess: async () => {
      setSaveName("");
      await queryClient.invalidateQueries({ queryKey: ["discovery", "saved-searches"] });
      toast.success("Saved search linked to your list");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className={cn(surface.card, "space-y-4 rounded-lg p-4")}>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="discover-role">Role</Label>
          <Input
            id="discover-role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="Staff engineer"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="discover-stack">Stack</Label>
          <Input
            id="discover-stack"
            value={stack}
            onChange={(e) => setStack(e.target.value)}
            placeholder="Python, React, RAG"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="discover-location">Location</Label>
          <Input
            id="discover-location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Remote, SF"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="discover-stage">Stage / size</Label>
          <Input
            id="discover-stage"
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            placeholder="Series B"
          />
        </div>
        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="discover-work-style">Work style</Label>
          <Input
            id="discover-work-style"
            value={workStyle}
            onChange={(e) => setWorkStyle(e.target.value)}
            placeholder="Hybrid"
          />
        </div>
        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="discover-board-url">Board / careers URL (optional)</Label>
          <Input
            id="discover-board-url"
            value={boardUrl}
            onChange={(e) => setBoardUrl(e.target.value)}
            placeholder="https://jobs.lever.co/company"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          size="sm"
          disabled={searchMutation.isPending}
          onClick={() => searchMutation.mutate()}
        >
          <Search className="mr-1.5 size-4" aria-hidden />
          Search boards
        </Button>
        {savedQuery.data?.length ? (
          <select
            className="h-8 rounded-lg border border-border bg-background px-2 text-sm"
            defaultValue=""
            onChange={(e) => {
              const saved = savedQuery.data?.find((row) => row.id === e.target.value);
              if (!saved) return;
              setRole(saved.query.role ?? "");
              setStack((saved.query.stack ?? []).join(", "));
              setLocation(saved.query.location ?? "");
              setStage(saved.query.stage ?? "");
              setWorkStyle(saved.query.work_style ?? "");
              setBoardUrl((saved.query.board_urls ?? [])[0] ?? "");
            }}
          >
            <option value="">Load saved search…</option>
            {savedQuery.data.map((row) => (
              <option key={row.id} value={row.id}>
                {row.name}
              </option>
            ))}
          </select>
        ) : null}
      </div>

      <div className="flex flex-wrap items-end gap-2 border-t border-border pt-3">
        <div className="min-w-[12rem] flex-1 space-y-1.5">
          <Label htmlFor="save-search-name">Save this search</Label>
          <Input
            id="save-search-name"
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            placeholder="AI eng — Series B"
          />
        </div>
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={!saveName.trim() || saveMutation.isPending || !listId}
          onClick={() => saveMutation.mutate()}
        >
          Save & link to list
        </Button>
      </div>
    </div>
  );
}
