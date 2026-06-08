import { describe, expect, it } from "vitest";

import { isGoogleOAuthEnabled, oauthErrorMessage } from "./google-oauth";

describe("isGoogleOAuthEnabled", () => {
  it("is false unless env flag is true", () => {
    expect(isGoogleOAuthEnabled()).toBe(
      process.env.NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED === "true",
    );
  });
});

describe("oauthErrorMessage", () => {
  it("maps known OAuth error codes", () => {
    expect(oauthErrorMessage("oauth_state")).toMatch(/expired/i);
    expect(oauthErrorMessage("oauth_failed")).toMatch(/failed/i);
  });

  it("handles not-configured server errors", () => {
    expect(oauthErrorMessage("Google sign-in is not configured")).toMatch(/not available/i);
  });

  it("returns null for empty input", () => {
    expect(oauthErrorMessage(null)).toBeNull();
    expect(oauthErrorMessage("")).toBeNull();
  });
});
