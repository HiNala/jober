"use client";

import Link from "next/link";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { NavLinks } from "@/components/app-shell/nav-links";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/stores/ui-store";

export function AppSidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUiStore();

  return (
    <aside
      className={cn(
        "hidden h-full flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] motion-safe:duration-[var(--motion-fast)] md:flex",
        motionView,
        sidebarCollapsed ? "w-16" : "w-56",
      )}
      aria-label="Main navigation"
    >
      <div className="flex h-14 items-center justify-between px-3">
        {!sidebarCollapsed ? (
          <Link href="/dashboard" className="text-sm font-semibold tracking-tight">
            Jober
          </Link>
        ) : (
          <span className="sr-only">Jober</span>
        )}
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={toggleSidebar}
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {sidebarCollapsed ? (
            <PanelLeftOpen className="size-4" />
          ) : (
            <PanelLeftClose className="size-4" />
          )}
        </Button>
      </div>
      <Separator />
      <ScrollArea className="flex-1 px-2 py-3">
        <nav className="flex flex-col gap-1">
          <NavLinks collapsed={sidebarCollapsed} />
        </nav>
      </ScrollArea>
    </aside>
  );
}
