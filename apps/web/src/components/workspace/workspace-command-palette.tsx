"use client";

import { useRouter, usePathname } from "next/navigation";
import { useCallback, useMemo } from "react";
import {
  Download,
  FileSpreadsheet,
  Maximize2,
  PanelRightOpen,
  Play,
} from "lucide-react";

import { APP_NAV } from "@/components/app-shell/nav-links";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import { exportJobsXlsxUrl } from "@/lib/api/jobs";
import { isOpsDeskPath } from "@/lib/workspace/layout";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function WorkspaceCommandPalette() {
  const router = useRouter();
  const pathname = usePathname();
  const {
    commandPaletteOpen,
    setCommandPaletteOpen,
    toggleCanvas,
    toggleFocusMode,
    canvasOpen,
    focusMode,
  } = useWorkspaceStore();

  const close = useCallback(() => setCommandPaletteOpen(false), [setCommandPaletteOpen]);

  const run = useCallback(
    (fn: () => void) => {
      close();
      fn();
    },
    [close],
  );

  const pageActions = useMemo(() => {
    if (pathname === "/queue") {
      return [
        {
          label: "Import spreadsheet",
          icon: FileSpreadsheet,
          onSelect: () => run(() => router.push("/queue?import=1")),
        },
        {
          label: "Export queue XLSX",
          icon: Download,
          onSelect: () => run(() => window.open(exportJobsXlsxUrl(), "_blank")),
        },
      ];
    }
    if (pathname === "/dashboard") {
      return [
        {
          label: "Open job queue",
          icon: Play,
          onSelect: () => run(() => router.push("/queue")),
        },
      ];
    }
    if (isOpsDeskPath(pathname)) {
      return [
        {
          label: canvasOpen ? "Hide canvas" : "Show canvas",
          icon: PanelRightOpen,
          onSelect: () => run(() => toggleCanvas()),
        },
        {
          label: focusMode ? "Exit focus mode" : "Enter focus mode",
          icon: Maximize2,
          onSelect: () => run(() => toggleFocusMode()),
        },
      ];
    }
    return [];
  }, [pathname, canvasOpen, focusMode, run, router, toggleCanvas, toggleFocusMode]);

  return (
    <CommandDialog
      open={commandPaletteOpen}
      onOpenChange={setCommandPaletteOpen}
      title="Command palette"
      description="Navigate the workspace or run a contextual action"
    >
      <CommandInput placeholder="Search commands…" />
      <CommandList>
        <CommandEmpty>No matching commands.</CommandEmpty>
        {pageActions.length > 0 ? (
          <>
            <CommandGroup heading="This page">
              {pageActions.map(({ label, icon: Icon, onSelect }) => (
                <CommandItem key={label} onSelect={onSelect}>
                  <Icon className="size-4" aria-hidden />
                  {label}
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        ) : null}
        <CommandGroup heading="Navigate">
          {APP_NAV.map(({ href, label, icon: Icon }) => (
            <CommandItem key={href} onSelect={() => run(() => router.push(href))}>
              <Icon className="size-4" aria-hidden />
              {label}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Shortcuts">
          <CommandItem disabled>
            Open palette
            <CommandShortcut>⌘K</CommandShortcut>
          </CommandItem>
          <CommandItem disabled>
            Toggle navigation
            <CommandShortcut>⌘B</CommandShortcut>
          </CommandItem>
          {isOpsDeskPath(pathname) ? (
            <CommandItem disabled>
              Toggle canvas
              <CommandShortcut>⌘\</CommandShortcut>
            </CommandItem>
          ) : null}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
