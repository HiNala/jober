"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, ArchiveRestore, ChevronDown, ChevronUp, Plus } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createJobList,
  fetchJobLists,
  reorderJobList,
  updateJobList,
  type JobListItem,
} from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function moveItem(items: JobListItem["items"], index: number, direction: -1 | 1) {
  const next = index + direction;
  if (next < 0 || next >= items.length) return items;
  const copy = [...items];
  const [removed] = copy.splice(index, 1);
  copy.splice(next, 0, removed);
  return copy;
}

export function LibraryJobLists() {
  const [name, setName] = useState("");
  const [showArchived, setShowArchived] = useState(false);
  const queryClient = useQueryClient();
  const listsQuery = useQuery({
    queryKey: ["library", "job-lists", showArchived],
    queryFn: async () => (await fetchJobLists(showArchived)).items,
  });

  const createMutation = useMutation({
    mutationFn: () => createJobList(name.trim()),
    onSuccess: async () => {
      setName("");
      await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
    },
  });

  const archiveMutation = useMutation({
    mutationFn: ({ listId, archived }: { listId: string; archived: boolean }) =>
      updateJobList(listId, { archived }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
    },
  });

  const reorderMutation = useMutation({
    mutationFn: ({ listId, itemIds }: { listId: string; itemIds: string[] }) =>
      reorderJobList(listId, itemIds),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
    },
  });

  const visibleLists = listsQuery.data?.filter((list) => showArchived || !list.archived) ?? [];

  return (
    <section aria-labelledby="library-jobs-heading" className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="library-jobs-heading" className="text-sm font-medium">
          Saved job lists
        </h2>
        <div className="flex items-center gap-2">
          <input
            id="show-archived-lists"
            type="checkbox"
            checked={showArchived}
            onChange={(e) => setShowArchived(e.target.checked)}
            className="size-4 rounded border-border"
          />
          <Label htmlFor="show-archived-lists" className="text-xs text-muted-foreground">
            Show archived
          </Label>
        </div>
      </div>

      <form
        className="flex flex-wrap gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          if (name.trim()) void createMutation.mutate();
        }}
      >
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder='e.g. "Priority A — AI eng"'
          className="max-w-sm"
          aria-label="New list name"
        />
        <Button type="submit" size="sm" disabled={!name.trim() || createMutation.isPending}>
          <Plus className="mr-1 size-4" aria-hidden />
          Create list
        </Button>
      </form>

      {listsQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading lists…</p>
      ) : null}
      {visibleLists.length === 0 ? (
        <p className={cn(surface.card, "rounded-lg p-4 text-sm text-muted-foreground")}>
          {showArchived
            ? "No lists yet. Create one to group targets from discovery or import."
            : "No active lists. Create one or enable “Show archived”."}
        </p>
      ) : null}

      <ul className="space-y-3">
        {visibleLists.map((list) => (
          <li key={list.id} className={cn(surface.card, "rounded-lg p-4")}>
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="font-medium">
                  {list.name}
                  {list.archived ? (
                    <span className="ml-2 text-xs font-normal text-muted-foreground">(archived)</span>
                  ) : null}
                </p>
                {list.description ? (
                  <p className="text-sm text-muted-foreground">{list.description}</p>
                ) : null}
                <p className="mt-1 text-xs text-muted-foreground">
                  {list.items.length} job{list.items.length === 1 ? "" : "s"}
                </p>
              </div>
              <Button
                type="button"
                size="sm"
                variant="ghost"
                disabled={archiveMutation.isPending}
                onClick={() =>
                  archiveMutation.mutate({ listId: list.id, archived: !list.archived })
                }
              >
                {list.archived ? (
                  <>
                    <ArchiveRestore className="mr-1 size-4" aria-hidden />
                    Restore
                  </>
                ) : (
                  <>
                    <Archive className="mr-1 size-4" aria-hidden />
                    Archive
                  </>
                )}
              </Button>
            </div>
            {list.items.length > 0 ? (
              <ul className="mt-2 space-y-1 text-sm">
                {list.items.map((item, index) => (
                  <li
                    key={item.id}
                    className="flex flex-wrap items-center justify-between gap-2 text-muted-foreground"
                  >
                    <span>
                      {item.company} — {item.role}
                      {item.status ? ` (${item.status})` : ""}
                    </span>
                    <div className="flex items-center gap-1">
                      <Button
                        type="button"
                        size="icon-xs"
                        variant="ghost"
                        aria-label="Move job up"
                        disabled={index === 0 || reorderMutation.isPending}
                        onClick={() => {
                          const reordered = moveItem(list.items, index, -1);
                          reorderMutation.mutate({
                            listId: list.id,
                            itemIds: reordered.map((row) => row.id),
                          });
                        }}
                      >
                        <ChevronUp className="size-3.5" />
                      </Button>
                      <Button
                        type="button"
                        size="icon-xs"
                        variant="ghost"
                        aria-label="Move job down"
                        disabled={
                          index === list.items.length - 1 || reorderMutation.isPending
                        }
                        onClick={() => {
                          const reordered = moveItem(list.items, index, 1);
                          reorderMutation.mutate({
                            listId: list.id,
                            itemIds: reordered.map((row) => row.id),
                          });
                        }}
                      >
                        <ChevronDown className="size-3.5" />
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
