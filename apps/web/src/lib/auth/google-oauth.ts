/** True when web should show Google sign-in / link affordances. */
export function isGoogleOAuthEnabled(): boolean {
  return process.env.NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED === "true";
}

const OAUTH_ERROR_MESSAGES: Record<string, string> = {
  oauth_state: "Google sign-in expired or was interrupted. Please try again.",
  oauth_failed: "Google sign-in failed. Please try again or use email and password.",
};

/** Map OAuth callback redirect query params to user-facing copy. */
export function oauthErrorMessage(code: string | null | undefined): string | null {
  if (!code) return null;
  const decoded = decodeURIComponent(code.replace(/\+/g, " "));
  if (OAUTH_ERROR_MESSAGES[decoded]) return OAUTH_ERROR_MESSAGES[decoded];
  if (decoded.toLowerCase().includes("not configured")) {
    return "Google sign-in is not available on this server.";
  }
  if (decoded.toLowerCase().includes("linked to another user")) {
    return "This Google account is already linked to a different user.";
  }
  return "Sign-in could not be completed. Please try again.";
}
