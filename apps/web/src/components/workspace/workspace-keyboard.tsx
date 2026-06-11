"use client";

import { useEffect } from "react";

import { isOpsDeskPath } from "@/lib/workspace/layout";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function useWorkspaceKeyboard(pathname: string) {
  const { toggleNav, toggleCanvas, toggleFocusMode, setCommandPaletteOpen } = useWorkspaceStore();

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const mod = event.metaKey || event.ctrlKey;
      if (!mod) {
        return;
      }

      if (event.key === "b" || event.key === "B") {
        event.preventDefault();
        toggleNav();
        return;
      }

      if (event.key === "k" || event.key === "K") {
        event.preventDefault();
        setCommandPaletteOpen(true);
        return;
      }

      if (event.key === "\\" || event.key === "|") {
        if (!isOpsDeskPath(pathname)) {
          return;
        }
        event.preventDefault();
        toggleCanvas();
        return;
      }

      if (event.key === "/" && !event.shiftKey) {
        event.preventDefault();
        setCommandPaletteOpen(true);
        return;
      }

      if (event.shiftKey && (event.key === "F" || event.key === "f")) {
        if (!isOpsDeskPath(pathname)) {
          return;
        }
        event.preventDefault();
        toggleFocusMode();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    pathname,
    setCommandPaletteOpen,
    toggleCanvas,
    toggleFocusMode,
    toggleNav,
  ]);
}
