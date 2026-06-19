"use client";

import { Play, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { JobListItem } from "@/lib/api/library";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

type Props = {
  lists: JobListItem[];
  activeListId: string | null;
  onSelectList: (id: string) => void;
  newListName: string;
  onNewListNameChange: (value: string) => void;
  onCreateList: () => void;
  priority: string;
  onPriorityChange: (value: string) => void;
  fitLane: string;
  onFitLaneChange: (value: string) => void;
  selectedCount: number;
  onAccept: () => void;
  acceptPending: boolean;
  onRefresh: () => void;
  refreshPending: boolean;
  onLaunchBatch: () => void;
  launchPending: boolean;
};

export function ListBuilderPanel({
  lists,
  activeListId,
  onSelectList,
  newListName,
  onNewListNameChange,
  onCreateList,
  priority,
  onPriorityChange,
  fitLane,
  onFitLaneChange,
  selectedCount,
  onAccept,
  acceptPending,
  onRefresh,
  refreshPending,
  onLaunchBatch,
  launchPending,
}: Props) {
  const activeList = lists.find((list) => list.id === activeListId);

  return (
    <aside className={cn(surface.workspace, "space-y-4 rounded-lg p-4 xl:sticky xl:top-4")}>
      <h2 className="text-sm font-medium">Target list</h2>

      <div className="space-y-1.5">
        <Label>Saved list</Label>
        <Select value={activeListId ?? ""} onValueChange={(v) => { if (v) onSelectList(v); }}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a list…" />
          </SelectTrigger>
          <SelectContent>
            {lists.map((list) => (
              <SelectItem key={list.id} value={list.id}>
                {list.name} ({list.items.length})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex gap-2">
        <Input
          value={newListName}
          onChange={(e) => onNewListNameChange(e.target.value)}
          placeholder="New list name"
          aria-label="New list name"
        />
        <Button type="button" size="sm" variant="outline" onClick={onCreateList}>
          Create
        </Button>
      </div>

      {activeList ? (
        <p className="text-xs text-muted-foreground">
          {activeList.items.length} job{activeList.items.length === 1 ? "" : "s"} in “
          {activeList.name}”
        </p>
      ) : null}

      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1.5">
          <Label htmlFor="list-priority">Priority</Label>
          <Input
            id="list-priority"
            value={priority}
            onChange={(e) => onPriorityChange(e.target.value)}
            placeholder="A"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="list-fit-lane">Fit lane</Label>
          <Input
            id="list-fit-lane"
            value={fitLane}
            onChange={(e) => onFitLaneChange(e.target.value)}
            placeholder="AI eng"
          />
        </div>
      </div>

      <Button
        type="button"
        className="w-full"
        disabled={!activeListId || selectedCount === 0 || acceptPending}
        onClick={onAccept}
      >
        Add {selectedCount || ""} to list
      </Button>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        disabled={!activeListId || refreshPending}
        onClick={onRefresh}
      >
        <RefreshCw className="mr-1.5 size-4" aria-hidden />
        Refresh list
      </Button>

      <Button
        type="button"
        variant="secondary"
        className="w-full"
        disabled={!activeListId || launchPending}
        onClick={onLaunchBatch}
      >
        <Play className="mr-1.5 size-4" aria-hidden />
        Preview batch from list
      </Button>
    </aside>
  );
}
