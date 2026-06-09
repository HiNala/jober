import { afterEach, describe, expect, it, vi } from "vitest";

import { trackMarketingCta } from "@/lib/marketing/cta";

vi.mock("@/lib/analytics/sdk", () => ({
  trackEvent: vi.fn(),
}));

import { trackEvent } from "@/lib/analytics/sdk";

describe("trackMarketingCta", () => {
  afterEach(() => {
    vi.mocked(trackEvent).mockClear();
  });

  it("emits feature.use with the CTA feature key", () => {
    trackMarketingCta("landing_hero_signup");
    expect(trackEvent).toHaveBeenCalledWith("feature.use", {
      feature: "landing_hero_signup",
    });
  });
});
