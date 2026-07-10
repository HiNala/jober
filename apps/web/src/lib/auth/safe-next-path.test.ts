import { describe, expect, it } from "vitest";

import { safeNextPath } from "@/lib/auth/safe-next-path";

describe("safeNextPath", () => {
  it("returns fallback for empty or external values", () => {
    expect(safeNextPath(null)).toBe("/dashboard");
    expect(safeNextPath("https://evil.com")).toBe("/dashboard");
    expect(safeNextPath("//evil.com")).toBe("/dashboard");
    expect(safeNextPath("dashboard")).toBe("/dashboard");
  });

  it("allows internal paths", () => {
    expect(safeNextPath("/admin")).toBe("/admin");
    expect(safeNextPath("/queue?job=1")).toBe("/queue?job=1");
  });

  it("blocks auth loops", () => {
    expect(safeNextPath("/login")).toBe("/dashboard");
    expect(safeNextPath("/signup?x=1")).toBe("/dashboard");
  });
});
