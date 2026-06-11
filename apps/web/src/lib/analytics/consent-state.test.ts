import { afterEach, describe, expect, it, vi } from "vitest";

describe("consent decision helpers", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shouldPromptConsent is true when cookie absent", async () => {
    vi.stubGlobal("document", { cookie: "" });
    const { shouldPromptConsent, hasConsentDecision } = await import("@/lib/analytics/consent");
    expect(hasConsentDecision()).toBe(false);
    expect(shouldPromptConsent()).toBe(true);
  });

  it("shouldPromptConsent is false after decline cookie", async () => {
    vi.stubGlobal("document", { cookie: "jober_analytics_consent=0" });
    const { shouldPromptConsent } = await import("@/lib/analytics/consent");
    expect(shouldPromptConsent()).toBe(false);
  });
});

describe("trackEvent consent gating", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.resetModules();
  });

  it("does not enqueue events without consent", async () => {
    vi.stubGlobal("document", { cookie: "" });
    vi.stubGlobal("navigator", { doNotTrack: "0" });
    vi.stubGlobal("window", { location: { pathname: "/" } });
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const { trackEvent, flushAnalytics } = await import("@/lib/analytics/sdk");
    trackEvent("feature.use", { feature: "test" });
    await flushAnalytics();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("does not enqueue events when DNT is enabled even with consent cookie", async () => {
    vi.stubGlobal("document", { cookie: "jober_analytics_consent=1" });
    vi.stubGlobal("navigator", { doNotTrack: "1" });
    vi.stubGlobal("window", { location: { pathname: "/" } });
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const { trackEvent, flushAnalytics } = await import("@/lib/analytics/sdk");
    trackEvent("page.view", { path: "/" });
    await flushAnalytics();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
