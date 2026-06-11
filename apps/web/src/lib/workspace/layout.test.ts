import { describe, expect, it } from "vitest";

import { isOpsDeskPath, layoutModeForPath } from "@/lib/workspace/layout";

describe("layoutModeForPath", () => {
  it("uses ops-desk only for run console routes", () => {
    expect(layoutModeForPath("/runs/abc-123")).toBe("ops-desk");
    expect(isOpsDeskPath("/runs/abc-123")).toBe(true);
  });

  it("uses editorial for standard workspace routes", () => {
    for (const path of [
      "/dashboard",
      "/queue",
      "/discover",
      "/library",
      "/search",
      "/analytics",
      "/settings",
      "/admin",
    ]) {
      expect(layoutModeForPath(path)).toBe("editorial");
    }
  });
});
