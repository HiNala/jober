import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/api/client";
import { locToFieldPath, mapApiErrors, remapFieldErrors } from "@/lib/forms/map-api-errors";

describe("locToFieldPath", () => {
  it("drops body prefix", () => {
    expect(locToFieldPath(["body", "password"])).toBe("password");
  });

  it("joins nested paths", () => {
    expect(locToFieldPath(["body", "profile", "email"])).toBe("profile.email");
  });
});

describe("mapApiErrors", () => {
  it("maps pydantic field errors", () => {
    const body = JSON.stringify({
      detail: [
        { loc: ["body", "password"], msg: "String should have at least 10 characters" },
        { loc: ["body", "email"], msg: "value is not a valid email address" },
      ],
    });
    const mapped = mapApiErrors(new ApiError("API 422", 422, body), "fallback");
    expect(mapped.fieldErrors.password).toContain("10 characters");
    expect(mapped.fieldErrors.email).toContain("email");
  });

  it("maps string detail to form error", () => {
    const body = JSON.stringify({ detail: "Invalid email or password" });
    expect(mapApiErrors(new ApiError("API 401", 401, body), "fallback").formError).toBe(
      "Invalid email or password",
    );
  });

  it("maps 503 dependency_unavailable detail object", () => {
    const body = JSON.stringify({
      detail: {
        message: "A required service is temporarily unavailable. Try again shortly.",
        code: "dependency_unavailable",
      },
      correlation_id: "abc",
      code: "dependency_unavailable",
    });
    const mapped = mapApiErrors(new ApiError("API 503", 503, body), "fallback");
    expect(mapped.formError).toContain("temporarily unavailable");
  });

  it("remaps field aliases", () => {
    const mapped = remapFieldErrors({ display_name: "too long" }, { display_name: "name" });
    expect(mapped.name).toBe("too long");
    expect(mapped.display_name).toBeUndefined();
  });

  it("maps 402 budget errors to honest generation copy", () => {
    const mapped = mapApiErrors(new ApiError("API 402", 402, ""), "fallback");
    expect(mapped.formError).toContain("budget exceeded");
    expect(mapped.fieldErrors).toEqual({});
  });

  it("maps auth lockout strings from network errors", () => {
    const mapped = mapApiErrors(new Error("Account locked after too many attempts"), "fallback");
    expect(mapped.formError).toContain("locked");
  });
});
