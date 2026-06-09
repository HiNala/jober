import { trackEvent } from "@/lib/analytics/sdk";

/** Consent-gated landing CTA click — `feature` must match event registry allowlist usage. */
export function trackMarketingCta(feature: string): void {
  trackEvent("feature.use", { feature });
}
