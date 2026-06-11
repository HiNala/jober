import { describe, expect, it } from "vitest";

import { parseAuthError } from "@/lib/auth/parse-auth-error";

describe("parseAuthError", () => {
  it("extracts detail from JSON error bodies", () => {
    expect(
      parseAuthError(new Error('{"detail":"Invalid email or password"}'), "fallback"),
    ).toBe("Invalid email or password");
  });

  it("maps rate-limit phrasing", () => {
    expect(
      parseAuthError(new Error("Too many failed attempts. Try again later."), "fallback"),
    ).toBe("Too many failed attempts. Try again later.");
  });

  it("falls back for unknown errors", () => {
    expect(parseAuthError(new Error("network"), "Sign in failed.")).toBe("Sign in failed.");
  });
});
