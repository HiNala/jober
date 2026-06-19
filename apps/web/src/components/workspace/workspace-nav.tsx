"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  ListTodo,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
} from "lucide-react";

import { NavLinks } from "@/components/app-shell/nav-links";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button, buttonVariants } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { fetchDashboardSummary } from "@/lib/api/batches";
import { useAuth } from "@/contexts/auth-context";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

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
  const queueDepth = summaryQuery.data?.queue_depth_priority_a ?? 0;

  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground",
        motionView,
      )}
      aria-label="Workspace navigation"
    >
      {/* Header */}
      <div className="flex h-12 shrink-0 items-center justify-between px-2">
        {!navCollapsed ? (
          <Link href="/dashboard" className="px-2 text-base font-semibold tracking-tight text-foreground/90">
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

      {/* Primary CTA */}
      <div className={cn("shrink-0 p-2", navCollapsed && "flex justify-center")}>
        <Link
          href="/queue"
          className={cn(
            buttonVariants({ variant: "default", size: navCollapsed ? "icon-sm" : "sm" }),
            !navCollapsed && "w-full justify-start",
          )}
        >
          <ListTodo className="size-4" aria-hidden />
          {!navCollapsed ? <span className="ml-2">Open queue</span> : <span className="sr-only">Open queue</span>}
        </Link>
      </div>

      <Separator />

      {/* Main navigation */}
      <ScrollArea className="flex-1 px-2 py-2">
        <nav aria-label="Main">
          <NavLinks
            collapsed={navCollapsed}
            counts={{ "/queue": queueDepth, "/dashboard": activeRuns > 0 ? activeRuns : undefined }}
          />
        </nav>
      </ScrollArea>

      <Separator />

      {/* Footer */}
      <div className={cn("shrink-0 space-y-2 p-2", navCollapsed && "items-center")}>
        {!navCollapsed ? (
          <div className="rounded-lg border border-primary/20 bg-gradient-to-br from-primary/10 via-primary/6 to-transparent p-3 text-xs">
            <div className="flex items-center gap-2 font-semibold text-foreground">
              <Sparkles className="size-3.5 text-primary" aria-hidden />
              Upgrade to Pro
            </div>
            <p className="mt-1 leading-relaxed text-muted-foreground">
              Higher run limits and priority support.
            </p>
            <Link
              href="/settings"
              className={cn(buttonVariants({ variant: "outline", size: "sm" }), "mt-2.5 w-full rounded-lg")}
            >
              View plans
            </Link>
          </div>
        ) : null}
        <button
          type="button"
          onClick={() => void signOut().then(() => window.location.assign("/login"))}
          className={cn(
            "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left hover:bg-sidebar-accent/80",
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
