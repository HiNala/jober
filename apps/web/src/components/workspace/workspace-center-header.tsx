"use client";

import {
  ArrowLeft,
  ChevronDown,
  Maximize2,
  MoreHorizontal,
  PanelRightOpen,
  Radio,
  Search,
} from "lucide-react";

import Link from "next/link";

import { MobileNav } from "@/components/app-shell/mobile-nav";
import { WorkerHealthPill } from "@/components/app-shell/worker-health-pill";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { StatusPill } from "@/components/motion/status-pill";
import { useMediaQuery } from "@/hooks/use-media-query";
import { WORKSPACE_NARROW_QUERY } from "@/lib/workspace/breakpoints";
import type { WorkspaceLayoutMode } from "@/lib/workspace/layout";
import { motionMicro, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function WorkspaceCenterHeader({
  title,
  layoutMode,
}: {
  title: string;
  layoutMode: WorkspaceLayoutMode;
}) {
  const {
    toggleFocusMode,
    focusMode,
    canvasOpen,
    toggleCanvas,
    setCommandPaletteOpen,
    setRunMobileTab,
  } = useWorkspaceStore();
  const isOpsDesk = layoutMode === "ops-desk";
  const isNarrow = useMediaQuery(WORKSPACE_NARROW_QUERY);

  return (
    <header className="flex h-12 shrink-0 items-center justify-between gap-2 border-b border-border/60 bg-background/95 px-3 backdrop-blur-sm md:px-4">
      <div className="flex min-w-0 items-center gap-2">
        <MobileNav />
        {isOpsDesk ? (
          <Link
            href="/queue"
            className={cn(
              "hidden items-center gap-1 rounded-md px-1.5 py-1 text-sm text-muted-foreground hover:bg-muted/60 hover:text-foreground md:flex",
              motionMicro,
            )}
            aria-label="Back to queue"
          >
            <ArrowLeft className="size-3.5 shrink-0" aria-hidden />
            <span>Queue</span>
          </Link>
        ) : null}
        <button
          type="button"
          className={cn(
            "flex min-w-0 items-center gap-1.5 rounded-md px-1 py-0.5 text-left hover:bg-muted/60",
            motionMicro,
          )}
          aria-haspopup="listbox"
          aria-label={`${title} context`}
        >
          <h1 className="truncate text-base font-semibold tracking-tight">{title}</h1>
          <ChevronDown className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
        </button>
        {isOpsDesk ? (
          <StatusPill
            status="in_progress"
            label="Live"
            icon={<Radio className="size-3 fill-current" aria-hidden />}
            className="text-[0.65rem] uppercase tracking-wide"
          />
        ) : null}
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          className={cn("size-11 lg:hidden", motionPress)}
          onClick={() => setCommandPaletteOpen(true)}
          aria-label="Open command palette"
        >
          <Search className="size-5" aria-hidden />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className={cn("hidden text-muted-foreground lg:inline-flex", motionPress)}
          onClick={() => setCommandPaletteOpen(true)}
          aria-label="Open command palette"
          aria-keyshortcuts="Control+K Meta+K"
        >
          Command
          <kbd className="ml-2 rounded border bg-muted px-1.5 py-0.5 font-mono text-[10px]">
            ⌘K
          </kbd>
        </Button>
        <WorkerHealthPill />
        {isOpsDesk && !isNarrow ? (
          <>
            <Button
              variant="ghost"
              size="icon-lg"
              className={motionPress}
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
              className={motionPress}
              onClick={toggleFocusMode}
              aria-label={focusMode ? "Exit focus mode" : "Enter focus mode"}
              aria-pressed={focusMode}
              title="Focus mode"
            >
              <Maximize2 className={cn("size-4", focusMode && "text-primary")} />
            </Button>
          </>
        ) : null}
        {isOpsDesk && isNarrow ? (
          <Button
            variant="ghost"
            className={cn("size-11 lg:hidden", motionPress)}
            onClick={() => setRunMobileTab("canvas")}
            aria-label="Show canvas"
          >
            <PanelRightOpen className="size-5" aria-hidden />
          </Button>
        ) : null}
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <Button variant="ghost" className="size-11" aria-label="Workspace menu">
                <MoreHorizontal className="size-5" aria-hidden />
              </Button>
            }
          />
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setCommandPaletteOpen(true)}>
              Open command palette
            </DropdownMenuItem>
            {isOpsDesk ? (
              <DropdownMenuItem onClick={toggleFocusMode}>
                {focusMode ? "Exit focus mode" : "Focus mode"}
              </DropdownMenuItem>
            ) : null}
            <DropdownMenuItem disabled>Export session</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
