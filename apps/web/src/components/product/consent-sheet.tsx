"use client";

import Link from "next/link";
import { useCallback, useState } from "react";

import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { markConsentPrompted, shouldPromptConsent } from "@/lib/analytics/consent";
import {
  flushAnalytics,
  setAnalyticsConsent,
  trackPageView,
} from "@/lib/analytics/sdk";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function ConsentSheet() {
  const [open, setOpen] = useState(
    () => typeof document !== "undefined" && shouldPromptConsent(),
  );

  const answer = useCallback((accepted: boolean) => {
    setAnalyticsConsent(accepted);
    markConsentPrompted();
    setOpen(false);
    if (accepted) {
      trackPageView();
      void flushAnalytics();
    }
  }, []);

  const onOpenChange = useCallback((next: boolean) => {
    if (!next && shouldPromptConsent()) {
      setOpen(false);
      return;
    }
    setOpen(next);
  }, []);

  if (!open && !shouldPromptConsent()) {
    return null;
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange} modal shouldScaleBackground={false}>
      <DrawerContent
        className={cn(motionView, "max-h-[min(40vh,320px)]")}
        aria-describedby="consent-sheet-description"
      >
        <DrawerHeader className="pb-2 text-left">
          <DrawerTitle className="text-base font-medium">First-party analytics</DrawerTitle>
          <DrawerDescription id="consent-sheet-description" className="text-sm text-muted-foreground">
            Jober records usage with same-origin analytics only — no third-party trackers. If you
            decline, we do not send events from this browser.{" "}
            <Link
              href="/privacy#cookies-and-analytics"
              className="underline underline-offset-2 hover:text-foreground"
            >
              Privacy policy
            </Link>
            .
          </DrawerDescription>
        </DrawerHeader>
        <DrawerFooter className="flex-row justify-end gap-2 pt-0">
          <button
            type="button"
            className="rounded-md border px-4 py-2 text-sm text-muted-foreground hover:bg-muted/50"
            onClick={() => answer(false)}
          >
            Decline
          </button>
          <button
            type="button"
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
            onClick={() => answer(true)}
          >
            Accept
          </button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
