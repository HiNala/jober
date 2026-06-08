"use client";

import { AuthDivider } from "@/components/auth/auth-divider";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { isGoogleOAuthEnabled } from "@/lib/auth/google-oauth";

type GoogleSignInBlockProps = {
  label?: string;
  nextPath?: string;
};

export function GoogleSignInBlock({ label, nextPath }: GoogleSignInBlockProps) {
  if (!isGoogleOAuthEnabled()) return null;

  return (
    <>
      <GoogleSignInButton label={label} nextPath={nextPath} />
      <AuthDivider />
    </>
  );
}
