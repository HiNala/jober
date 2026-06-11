import { describe, expect, it } from "vitest";

import {
  forgotPasswordSubtitle,
  forgotPasswordSuccess,
  SIGNUP_VALUE_BULLETS,
  signupSubtitle,
} from "@/lib/auth/copy";

const FALSE_EMAIL_PROMISE = /\b(we sent|check your inbox|email(ed)? you)\b/i;

describe("auth copy honesty", () => {
  it("does not promise outbound email when delivery is disabled", () => {
    expect(forgotPasswordSubtitle(false)).not.toMatch(FALSE_EMAIL_PROMISE);
    expect(forgotPasswordSuccess(false).body).not.toMatch(FALSE_EMAIL_PROMISE);
    expect(forgotPasswordSuccess(false).body.toLowerCase()).toContain("not live");
    expect(signupSubtitle(false).toLowerCase()).toContain("not enabled");
  });

  it("may promise inbox delivery when SMTP is configured", () => {
    expect(forgotPasswordSubtitle(true).toLowerCase()).toContain("send");
    expect(forgotPasswordSuccess(true).title.toLowerCase()).toContain("check your email");
  });

  it("signup bullets reinforce product value", () => {
    expect(SIGNUP_VALUE_BULLETS.length).toBeGreaterThanOrEqual(3);
    expect(SIGNUP_VALUE_BULLETS.join(" ").toLowerCase()).toContain("review");
  });
});
