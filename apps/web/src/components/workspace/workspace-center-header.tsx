"use client";

import { ChevronDown, Maximize2, MoreHorizontal, PanelRightOpen, Radio } from "lucide-react";

import { MobileNav } from "@/components/app-shell/mobile-nav";
import { WorkerHealthPill } from "@/components/app-shell/worker-health-pill";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function WorkspaceCenterHeader({ title }: { title: string }) {
  const { toggleFocusMode, focusMode, canvasOpen, toggleCanvas } = useWorkspaceStore();

  return (
    <header className="flex h-12 shrink-0 items-center justify-between gap-2 border-b px-3 md:px-4">
      <div className="flex min-w-0 items-center gap-2">
        <MobileNav />
        <button
          type="button"
          className="flex min-w-0 items-center gap-1.5 rounded-md px-1 py-0.5 text-left hover:bg-muted/60"
          aria-haspopup="listbox"
          aria-label={`${title} context`}
        >
          <h1 className="truncate text-sm font-semibold tracking-tight">{title}</h1>
          <ChevronDown className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
        </button>
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[0.65rem] font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
          <Radio className="size-3 fill-current" aria-hidden />
          Live
        </span>
      </div>
      <div className="flex items-center gap-1">
        <WorkerHealthPill />
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={toggleCanvas}
          aria-label={canvasOpen ? "Hide canvas" : "Show canvas"}
          aria-pressed={canvasOpen}
          aria-keyshortcuts="Control+\\ Meta+\\"
        >
          <PanelRightOpen className={cn("size-4", canvasOpen && "text-primary")} />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={toggleFocusMode}
          aria-label={focusMode ? "Exit focus mode" : "Enter focus mode"}
          aria-pressed={focusMode}
          title="Focus mode"
        >
          <Maximize2 className={cn("size-4", focusMode && "text-primary")} />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <Button variant="ghost" size="icon-sm" aria-label="Workspace menu">
                <MoreHorizontal className="size-4" />
              </Button>
            }
          />
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={toggleFocusMode}>
              {focusMode ? "Exit focus mode" : "Focus mode"}
            </DropdownMenuItem>
            <DropdownMenuItem disabled>Export session</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
