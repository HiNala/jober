"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  BookOpen,
  Compass,
  ChevronDown,
  ChevronRight,
  FolderKanban,
  Layers,
  ListTodo,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Plus,
  Search,
  Sparkles,
} from "lucide-react";

import { NavLinks } from "@/components/app-shell/nav-links";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { fetchDashboardSummary } from "@/lib/api/batches";
import { useAuth } from "@/contexts/auth-context";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

type NavSectionProps = {
  title: string;
  count?: number;
  collapsed: boolean;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  defaultOpen?: boolean;
};

function NavSection({
  title,
  count,
  collapsed,
  href,
  icon: Icon,
  defaultOpen = true,
}: NavSectionProps) {
  const [open, setOpen] = React.useState(defaultOpen);

  if (collapsed) {
    return (
      <Link
        href={href}
        className="flex items-center justify-center rounded-md p-2 text-sidebar-foreground/80 hover:bg-sidebar-accent/60"
        title={title}
      >
        <Icon className="size-4" aria-hidden />
        <span className="sr-only">{title}</span>
        {count !== undefined && count > 0 ? (
          <span className="sr-only">{count} items</span>
        ) : null}
      </Link>
    );
  }

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="flex flex-1 items-center gap-2 rounded-md px-2 py-1.5 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground hover:bg-sidebar-accent/40"
          aria-expanded={open}
        >
          {open ? (
            <ChevronDown className="size-3.5 shrink-0" aria-hidden />
          ) : (
            <ChevronRight className="size-3.5 shrink-0" aria-hidden />
          )}
          {title}
          {count !== undefined ? (
            <Badge variant="secondary" className="ml-auto tabular-nums">
              {count}
            </Badge>
          ) : null}
        </button>
        <Link
          href={href}
          className={buttonVariants({ variant: "ghost", size: "icon-sm" })}
          aria-label={`Add ${title.toLowerCase()}`}
        >
          <Plus className="size-3.5" />
        </Link>
      </div>
      {open ? (
        <Link
          href={href}
          className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-sidebar-foreground/80 hover:bg-sidebar-accent/60"
        >
          <Icon className="size-4 shrink-0" aria-hidden />
          View all
        </Link>
      ) : null}
    </div>
  );
}

export function WorkspaceNav() {
  const { user, signOut } = useAuth();
  const { navCollapsed, toggleNav } = useWorkspaceStore();
  const initials =
    user?.display_name?.slice(0, 2).toUpperCase() ??
    user?.email?.slice(0, 2).toUpperCase() ??
    "??";
  const summaryQuery = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary,
    staleTime: 30_000,
  });

  const activeRuns = summaryQuery.data?.active_runs ?? 0;
  const batchCount = summaryQuery.data?.batches.length ?? 0;
  const queueDepth = summaryQuery.data?.queue_depth_priority_a ?? 0;

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground",
        motionView,
        navCollapsed ? "w-14" : "w-full",
      )}
      aria-label="Workspace navigation"
    >
      <div className="flex h-12 shrink-0 items-center justify-between px-2">
        {!navCollapsed ? (
          <Link href="/dashboard" className="px-2 text-base font-semibold tracking-tight">
            Jober
          </Link>
        ) : (
          <span className="sr-only">Jober</span>
        )}
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={toggleNav}
          aria-label={navCollapsed ? "Expand navigation" : "Collapse navigation"}
          aria-keyshortcuts="Control+B Meta+B"
        >
          {navCollapsed ? (
            <PanelLeftOpen className="size-4" />
          ) : (
            <PanelLeftClose className="size-4" />
          )}
        </Button>
      </div>

      <Separator />

      <div className={cn("shrink-0 space-y-1 p-2", navCollapsed && "flex flex-col items-center")}>
        <Link
          href="/queue"
          className={cn(
            buttonVariants({ variant: "default", size: navCollapsed ? "icon-sm" : "sm" }),
            !navCollapsed && "w-full justify-start",
          )}
        >
          <Play className="size-4" aria-hidden />
          {!navCollapsed ? <span className="ml-2">New run</span> : null}
          {navCollapsed ? <span className="sr-only">New run</span> : null}
        </Link>
        <Link
          href="/discover"
          className={cn(
            buttonVariants({ variant: "ghost", size: navCollapsed ? "icon-sm" : "sm" }),
            !navCollapsed && "w-full justify-start",
          )}
          title="Find new jobs from boards or spreadsheet"
        >
          <Compass className="size-4" aria-hidden />
          {!navCollapsed ? <span className="ml-2">Discover</span> : null}
          {navCollapsed ? <span className="sr-only">Discover</span> : null}
        </Link>
        <Link
          href="/search"
          className={cn(
            buttonVariants({ variant: "ghost", size: navCollapsed ? "icon-sm" : "sm" }),
            !navCollapsed && "w-full justify-start",
          )}
          title="Search library — jobs, letters, runs you already have"
        >
          <Search className="size-4" aria-hidden />
          {!navCollapsed ? <span className="ml-2">Search library</span> : null}
          {navCollapsed ? <span className="sr-only">Search library</span> : null}
        </Link>
        <Link
          href="/library"
          className={cn(
            buttonVariants({ variant: "ghost", size: navCollapsed ? "icon-sm" : "sm" }),
            !navCollapsed && "w-full justify-start",
          )}
        >
          <BookOpen className="size-4" aria-hidden />
          {!navCollapsed ? <span className="ml-2">Library</span> : null}
          {navCollapsed ? <span className="sr-only">Library</span> : null}
        </Link>
      </div>

      <Separator />

      <ScrollArea className="flex-1 px-2 py-2">
        <nav className="flex flex-col gap-3">
          <NavLinks collapsed={navCollapsed} />
          {!navCollapsed ? (
            <div className="space-y-3 pt-1">
              <NavSection
                title="Runs"
                count={activeRuns}
                collapsed={navCollapsed}
                href="/dashboard"
                icon={Play}
              />
              <NavSection
                title="Batches"
                count={batchCount}
                collapsed={navCollapsed}
                href="/dashboard"
                icon={Layers}
              />
              <NavSection
                title="Jobs"
                count={queueDepth}
                collapsed={navCollapsed}
                href="/queue"
                icon={ListTodo}
              />
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              <NavSection title="Runs" count={activeRuns} collapsed href="/dashboard" icon={Play} />
              <NavSection
                title="Batches"
                count={batchCount}
                collapsed
                href="/dashboard"
                icon={FolderKanban}
              />
              <NavSection title="Jobs" count={queueDepth} collapsed href="/queue" icon={ListTodo} />
            </div>
          )}
        </nav>
      </ScrollArea>

      <Separator />

      <div className={cn("shrink-0 space-y-2 p-2", navCollapsed && "items-center")}>
        {!navCollapsed ? (
          <div className="rounded-lg border border-sidebar-border bg-sidebar-accent/30 p-2.5 text-xs">
            <div className="flex items-center gap-2 font-medium">
              <Sparkles className="size-3.5 text-accent" aria-hidden />
              Upgrade to Pro
            </div>
            <p className="mt-1 text-muted-foreground">Higher run limits and priority support.</p>
            <Link
              href="/settings"
              className={cn(buttonVariants({ variant: "outline", size: "sm" }), "mt-2 w-full")}
            >
              View plans
            </Link>
          </div>
        ) : null}
        <button
          type="button"
          onClick={() => void signOut().then(() => window.location.assign("/login"))}
          className={cn(
            "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left hover:bg-sidebar-accent/50",
            navCollapsed && "justify-center px-0",
          )}
          title="Sign out"
        >
          <Avatar className="size-7">
            <AvatarFallback className="text-xs">{initials}</AvatarFallback>
          </Avatar>
          {!navCollapsed ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{user?.display_name ?? "Signed in"}</p>
              <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
            </div>
          ) : (
            <span className="sr-only">{user?.email}</span>
          )}
        </button>
      </div>
    </aside>
  );
}
