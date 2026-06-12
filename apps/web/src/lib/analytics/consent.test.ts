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

  it("setAnalyticsConsent writes accept or decline cookie", async () => {
    let cookie = "";
    vi.stubGlobal("document", {
      get cookie() {
        return cookie;
      },
      set cookie(value: string) {
        cookie = value;
      },
    });
    vi.stubGlobal("navigator", { doNotTrack: "0" });
    const { setAnalyticsConsent, hasAnalyticsConsent } = await import("@/lib/analytics/sdk");
    setAnalyticsConsent(true);
    expect(cookie).toContain("jober_analytics_consent=1");
    expect(hasAnalyticsConsent()).toBe(true);
    setAnalyticsConsent(false);
    expect(cookie).toContain("jober_analytics_consent=0");
    expect(hasAnalyticsConsent()).toBe(false);
  });
});

describe("consent sheet helpers", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("markConsentPrompted records localStorage flag", async () => {
    const store: Record<string, string> = {};
    vi.stubGlobal("localStorage", {
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      getItem: (key: string) => store[key] ?? null,
    });
    const { markConsentPrompted, CONSENT_PROMPTED_KEY } = await import("@/lib/analytics/consent");
    markConsentPrompted();
    expect(store[CONSENT_PROMPTED_KEY]).toBe("1");
  });
});
