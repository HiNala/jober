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
import { useAuth } from "@/contexts/auth-context";
import { isAdmin } from "@/lib/auth/permissions";
import { exportJobsXlsxUrl } from "@/lib/api/jobs";
import {
  buildPageCommands,
  type PageCommandId,
} from "@/lib/workspace/command-palette-actions";
import { isOpsDeskPath } from "@/lib/workspace/layout";
import { useWorkspaceStore } from "@/stores/workspace-store";
import { Shield } from "lucide-react";

const PAGE_COMMAND_ICONS: Record<
  PageCommandId,
  typeof FileSpreadsheet
> = {
  "import-spreadsheet": FileSpreadsheet,
  "export-queue-xlsx": Download,
  "open-job-queue": Play,
  "toggle-canvas": PanelRightOpen,
  "toggle-focus-mode": Maximize2,
};

export function WorkspaceCommandPalette() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
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
    const handlers: Record<PageCommandId, () => void> = {
      "import-spreadsheet": () => run(() => router.push("/queue?import=1")),
      "export-queue-xlsx": () => run(() => window.open(exportJobsXlsxUrl(), "_blank")),
      "open-job-queue": () => run(() => router.push("/queue")),
      "toggle-canvas": () => run(() => toggleCanvas()),
      "toggle-focus-mode": () => run(() => toggleFocusMode()),
    };
    return buildPageCommands(pathname, { canvasOpen, focusMode }).map((command) => ({
      ...command,
      icon: PAGE_COMMAND_ICONS[command.id],
      onSelect: handlers[command.id],
    }));
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
              {pageActions.map(({ id, label, icon: Icon, onSelect }) => (
                <CommandItem key={id} onSelect={onSelect}>
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
          {isAdmin(user) ? (
            <CommandItem onSelect={() => run(() => router.push("/admin"))}>
              <Shield className="size-4" aria-hidden />
              Admin
            </CommandItem>
          ) : null}
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
