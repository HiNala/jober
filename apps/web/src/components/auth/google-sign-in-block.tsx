"use client";

import { AuthDivider } from "@/components/auth/auth-divider";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { isGoogleOAuthEnabled } from "@/lib/auth/google-oauth";

type GoogleSignInBlockProps = {
  label?: string;
  nextPath?: string;
};

/** Renders Google CTA only when OAuth is enabled — never a disabled/coming-soon button. */
export function GoogleSignInBlock({ label, nextPath }: GoogleSignInBlockProps) {
  if (!isGoogleOAuthEnabled()) {
    return null;
  }

  return (
    <>
      <GoogleSignInButton label={label} nextPath={nextPath} />
      <AuthDivider />
    </>
  );
}
