"use client";

import Link from "next/link";
import { useState } from "react";

import { setAnalyticsConsent, trackPageView } from "@/lib/analytics/sdk";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function consentUndecided(): boolean {
  if (typeof document === "undefined") return false;
  return !document.cookie.match(/(?:^|;\s*)jober_analytics_consent=/);
}

export function AnalyticsConsentBanner() {
  const [visible, setVisible] = useState(consentUndecided);

  if (!visible) return null;

  return (
    <div
      className={cn(
        surface.card,
        "fixed bottom-4 left-4 right-4 z-50 mx-auto max-w-lg rounded-lg border p-4 shadow-lg sm:left-auto",
      )}
      role="dialog"
      aria-label="Analytics consent"
    >
      <p className="text-sm text-foreground">
        Jober uses first-party analytics only — no third-party trackers. If you decline, we do
        not record usage events on this device. See{" "}
        <Link href="/privacy#cookies-and-analytics" className="underline underline-offset-2">
          cookies &amp; analytics
        </Link>{" "}
        in our Privacy Policy.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground"
          onClick={() => {
            setAnalyticsConsent(true);
            setVisible(false);
            trackPageView();
          }}
        >
          Allow analytics
        </button>
        <button
          type="button"
          className="rounded-md border px-3 py-1.5 text-xs text-muted-foreground"
          onClick={() => {
            setAnalyticsConsent(false);
            setVisible(false);
          }}
        >
          Decline
        </button>
      </div>
    </div>
  );
}
