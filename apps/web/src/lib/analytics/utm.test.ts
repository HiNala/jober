import { afterEach, describe, expect, it, vi } from "vitest";

import { captureUtmFromUrl } from "@/lib/analytics/sdk";

describe("captureUtmFromUrl", () => {
  const storage = new Map<string, string>();

  afterEach(() => {
    storage.clear();
    vi.unstubAllGlobals();
  });

  it("persists UTM params from the URL into session storage", () => {
    vi.stubGlobal("sessionStorage", {
      setItem: (key: string, value: string) => storage.set(key, value),
      getItem: (key: string) => storage.get(key) ?? null,
    });
    vi.stubGlobal("window", {
      location: { search: "?utm_source=newsletter&utm_campaign=launch" },
    });

    captureUtmFromUrl();

    expect(storage.get("jober_utm")).toContain("newsletter");
    expect(storage.get("jober_utm")).toContain("launch");
  });
});
