/** User-facing auth copy — honest about email delivery until Mission 11 ships SMTP. */

export const AUTH_TRUST_ITEMS = [
  "Review before submit",
  "No third-party trackers",
  "Your data encrypted",
] as const;

export const FORGOT_PASSWORD_SUBTITLE =
  "Enter the email on your account. Reset links are not emailed on this deployment yet.";

export const FORGOT_PASSWORD_SUCCESS = {
  title: "Request received",
  body: "Password reset email is not live on this server yet. If you still have access, sign in — otherwise contact support for help.",
} as const;

export const SIGNUP_VALUE_BULLETS = [
  "Review every application before submit",
  "Private workspace — your tracker, your rules",
  "No spray-and-apply volume",
] as const;

export const RESET_TOKEN_MISSING = {
  title: "Reset link invalid",
  description: "This link is missing a token or has already been used. Request a new reset from the sign-in page.",
} as const;

export const LINK_GOOGLE_INVALID = {
  title: "Link expired",
  description: "This Google link is invalid or has expired. Start sign-in again from the login page.",
} as const;
