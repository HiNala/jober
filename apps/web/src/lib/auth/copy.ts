/** User-facing auth copy — honest about email delivery when SMTP is not configured. */

export const AUTH_TRUST_ITEMS = [
  "Review before submit",
  "No third-party trackers",
  "Your data encrypted",
] as const;

export function forgotPasswordSubtitle(inboxDelivery: boolean): string {
  if (inboxDelivery) {
    return "Enter the email on your account. If it exists, we'll send a reset link.";
  }
  return "Enter the email on your account. Reset links are not emailed on this deployment yet.";
}

export function forgotPasswordSuccess(inboxDelivery: boolean): {
  title: string;
  body: string;
} {
  if (inboxDelivery) {
    return {
      title: "Check your email",
      body: "If an account exists for that address, we sent password reset instructions. The link expires in one hour.",
    };
  }
  return {
    title: "Request received",
    body: "Password reset email is not live on this server yet. If you still have access, sign in — otherwise contact support for help.",
  };
}

export function signupSubtitle(inboxDelivery: boolean): string {
  if (inboxDelivery) {
    return "Create your workspace — we'll email a verification link before your first session.";
  }
  return "Your workspace is ready to use immediately — inbox verification is not enabled on this server.";
}

export const VERIFY_PENDING = {
  title: "Check your email",
  body: "We sent a verification link. It expires in 24 hours.",
  resendLabel: "Resend verification email",
  cooldownLabel: "Resend available in",
} as const;

export const VERIFY_UNAVAILABLE = {
  title: "Verification unavailable",
  body: "This server cannot send email yet. You can use the workspace, but verify your address once email is enabled.",
} as const;

export const VERIFY_EMAIL_SUCCESS = {
  title: "Email verified",
  body: "Your address is confirmed. You can continue in your workspace.",
} as const;

export const VERIFY_EMAIL_INVALID = {
  title: "Link invalid or expired",
  body: "This verification link is missing, expired, or already used. Request a new one from your account settings or sign up again.",
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
