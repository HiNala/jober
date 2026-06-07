"use client";

import { useEffect } from "react";

import { useWorkspaceStore } from "@/stores/workspace-store";

export function useWorkspaceKeyboard() {
  const { toggleNav, toggleCanvas, toggleFocusMode } = useWorkspaceStore();

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

      if (event.key === "\\" || event.key === "|") {
        event.preventDefault();
        toggleCanvas();
        return;
      }

      if (event.key === "/" && !event.shiftKey) {
        event.preventDefault();
        document.getElementById("workspace-command-input")?.focus();
        return;
      }

      if (event.shiftKey && (event.key === "F" || event.key === "f")) {
        event.preventDefault();
        toggleFocusMode();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [toggleCanvas, toggleFocusMode, toggleNav]);
}
