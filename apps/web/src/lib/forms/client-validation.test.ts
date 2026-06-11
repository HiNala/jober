import { describe, expect, it } from "vitest";

import { validateResetPassword, validateSignup } from "@/lib/forms/client-validation";

describe("validateSignup", () => {
  it("requires email and minimum password length", () => {
    const errors = validateSignup({ email: "", password: "short" });
    expect(errors.email).toBeTruthy();
    expect(errors.password).toContain("10");
  });

  it("passes valid signup fields", () => {
    expect(
      validateSignup({
        email: "user@example.com",
        password: "Str0ng!Pass",
      }),
    ).toEqual({});
  });
});

describe("validateResetPassword", () => {
  it("enforces password length", () => {
    expect(validateResetPassword("tiny").password).toContain("10");
  });
});
