"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createJobList, fetchJobLists } from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LibraryJobLists() {
  const [name, setName] = useState("");
  const queryClient = useQueryClient();
  const listsQuery = useQuery({
    queryKey: ["library", "job-lists"],
    queryFn: async () => (await fetchJobLists()).items,
  });

  const createMutation = useMutation({
    mutationFn: () => createJobList(name.trim()),
    onSuccess: async () => {
      setName("");
      await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
    },
  });

  return (
    <section aria-labelledby="library-jobs-heading" className="space-y-4">
      <h2 id="library-jobs-heading" className="text-sm font-medium">
        Saved job lists
      </h2>

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
      {listsQuery.data?.length === 0 ? (
        <p className={cn(surface.card, "rounded-lg p-4 text-sm text-muted-foreground")}>
          Named lists help you group targets from discovery or import. Mission 23 adds bulk import.
        </p>
      ) : null}

      <ul className="space-y-3">
        {listsQuery.data?.map((list) => (
          <li key={list.id} className={cn(surface.card, "rounded-lg p-4")}>
            <p className="font-medium">{list.name}</p>
            {list.description ? (
              <p className="text-sm text-muted-foreground">{list.description}</p>
            ) : null}
            <p className="mt-1 text-xs text-muted-foreground">
              {list.items.length} job{list.items.length === 1 ? "" : "s"}
            </p>
            {list.items.length > 0 ? (
              <ul className="mt-2 space-y-1 text-sm">
                {list.items.map((item) => (
                  <li key={item.id} className="text-muted-foreground">
                    {item.company} — {item.role}
                    {item.status ? ` (${item.status})` : ""}
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
