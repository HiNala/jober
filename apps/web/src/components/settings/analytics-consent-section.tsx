"use client";

import { BarChart3 } from "lucide-react";
import { useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { hasConsentDecision } from "@/lib/analytics/consent";
import {
  flushAnalytics,
  hasAnalyticsConsent,
  setAnalyticsConsent,
  trackPageView,
} from "@/lib/analytics/sdk";
import { surface } from "@/lib/design/tokens";

export function AnalyticsConsentSection() {
  const [enabled, setEnabled] = useState(() =>
    typeof document !== "undefined" ? hasAnalyticsConsent() : false,
  );
  const [decided, setDecided] = useState(() =>
    typeof document !== "undefined" ? hasConsentDecision() : false,
  );

  return (
    <section aria-labelledby="analytics-consent-heading">
      <div className="mb-3 flex items-center gap-2">
        <BarChart3 className="size-4 text-primary" aria-hidden />
        <h2 id="analytics-consent-heading" className="text-sm font-medium">
          Analytics consent
        </h2>
      </div>
      <Card className={surface.workspace}>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">First-party usage analytics</CardTitle>
          <CardDescription className="text-sm">
            Optional same-origin events help improve Jober. No third-party trackers. Honors Do Not
            Track when enabled in your browser.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-start gap-3">
          <Checkbox
            id="analytics-consent-toggle"
            checked={enabled}
            onCheckedChange={(checked) => {
              const allowed = checked === true;
              setAnalyticsConsent(allowed);
              setEnabled(allowed);
              setDecided(true);
              if (allowed) {
                trackPageView();
                void flushAnalytics();
              }
            }}
            aria-label="Allow first-party analytics"
          />
          <div className="space-y-1">
            <Label htmlFor="analytics-consent-toggle" className="text-sm font-medium">
              Allow usage analytics on this device
            </Label>
            <p className="text-xs text-muted-foreground">
              {enabled
                ? "Events are sent to Jober’s first-party collector only."
                : "No usage events are recorded until you enable this."}
            </p>
          </div>
        </CardContent>
        {!decided ? (
          <p className="px-6 pb-4 text-xs text-muted-foreground">
            You have not chosen yet — the consent prompt appears on your next visit to a public
            page.
          </p>
        ) : null}
      </Card>
    </section>
  );
}
