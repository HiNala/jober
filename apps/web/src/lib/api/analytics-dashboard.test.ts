import { describe, expect, it, vi } from "vitest";

import { rangeFromPreset } from "@/lib/api/analytics-dashboard";

describe("rangeFromPreset", () => {
  it("returns inclusive day spans for each preset", () => {
    const end = new Date("2026-06-10T12:00:00Z");
    vi.setSystemTime(end);

    expect(rangeFromPreset("7d")).toEqual({ start: "2026-06-04", end: "2026-06-10" });
    expect(rangeFromPreset("30d")).toEqual({ start: "2026-05-12", end: "2026-06-10" });
    expect(rangeFromPreset("90d")).toEqual({ start: "2026-03-13", end: "2026-06-10" });

    vi.useRealTimers();
  });
});
