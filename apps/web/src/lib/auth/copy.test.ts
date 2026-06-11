import { describe, expect, it } from "vitest";

import {
  FORGOT_PASSWORD_SUCCESS,
  FORGOT_PASSWORD_SUBTITLE,
  SIGNUP_VALUE_BULLETS,
} from "@/lib/auth/copy";

const FALSE_EMAIL_PROMISE = /\b(we sent|check your inbox|email(ed)? you)\b/i;

describe("auth copy honesty", () => {
  it("does not promise outbound email on forgot-password", () => {
    expect(FORGOT_PASSWORD_SUBTITLE).not.toMatch(FALSE_EMAIL_PROMISE);
    expect(FORGOT_PASSWORD_SUCCESS.body).not.toMatch(FALSE_EMAIL_PROMISE);
    expect(FORGOT_PASSWORD_SUCCESS.body.toLowerCase()).toContain("not live");
  });

  it("signup bullets reinforce product value", () => {
    expect(SIGNUP_VALUE_BULLETS.length).toBeGreaterThanOrEqual(3);
    expect(SIGNUP_VALUE_BULLETS.join(" ").toLowerCase()).toContain("review");
  });
});
