import { afterEach, describe, expect, it, vi } from "vitest";

describe("analytics consent gating", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.resetModules();
  });

  it("hasAnalyticsConsent is false when cookie is absent", async () => {
    vi.stubGlobal("document", { cookie: "" });
    vi.stubGlobal("navigator", { doNotTrack: "0" });
    const { hasAnalyticsConsent } = await import("@/lib/analytics/sdk");
    expect(hasAnalyticsConsent()).toBe(false);
  });

  it("hasAnalyticsConsent is false when user declined", async () => {
    vi.stubGlobal("document", { cookie: "jober_analytics_consent=0" });
    vi.stubGlobal("navigator", { doNotTrack: "0" });
    const { hasAnalyticsConsent } = await import("@/lib/analytics/sdk");
    expect(hasAnalyticsConsent()).toBe(false);
  });

  it("hasAnalyticsConsent is true only when cookie is 1 and DNT off", async () => {
    vi.stubGlobal("document", { cookie: "jober_analytics_consent=1" });
    vi.stubGlobal("navigator", { doNotTrack: "0" });
    const { hasAnalyticsConsent } = await import("@/lib/analytics/sdk");
    expect(hasAnalyticsConsent()).toBe(true);
  });
});
