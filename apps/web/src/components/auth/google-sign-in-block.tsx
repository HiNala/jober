"use client";

import { AuthDivider } from "@/components/auth/auth-divider";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { isGoogleOAuthEnabled } from "@/lib/auth/google-oauth";

type GoogleSignInBlockProps = {
  label?: string;
  nextPath?: string;
};

export function GoogleSignInBlock({ label, nextPath }: GoogleSignInBlockProps) {
  const enabled = isGoogleOAuthEnabled();

  if (enabled) {
    return (
      <>
        <GoogleSignInButton label={label} nextPath={nextPath} />
        <AuthDivider />
      </>
    );
  }

  return (
    <>
      <Tooltip>
        <TooltipTrigger render={<span className="block w-full" />}>
          <GoogleSignInButton
            label={label ?? "Continue with Google"}
            nextPath={nextPath}
            className="pointer-events-none opacity-50 w-full"
            aria-disabled="true"
          />
        </TooltipTrigger>
        <TooltipContent>Google sign-in coming soon</TooltipContent>
      </Tooltip>
      <AuthDivider />
    </>
  );
}
