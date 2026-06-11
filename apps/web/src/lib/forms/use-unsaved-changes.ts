"use client";

import { useEffect } from "react";

const DEFAULT_MESSAGE = "You have unsaved changes. Leave anyway?";

/** Warn before closing or refreshing when a heavy editor has unsaved drafts. */
export function useUnsavedChanges(dirty: boolean, message = DEFAULT_MESSAGE) {
  useEffect(() => {
    if (!dirty) return;
    const onBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = message;
    };
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [dirty, message]);
}
