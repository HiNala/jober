"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { oauthErrorMessage } from "@/lib/auth/google-oauth";

function AuthOAuthAlertInner() {
  const params = useSearchParams();
  const message = oauthErrorMessage(params.get("error"));
  if (!message) return null;

  return (
    <p className="mb-4 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">
      {message}
    </p>
  );
}

export function AuthOAuthAlert() {
  return (
    <Suspense fallback={null}>
      <AuthOAuthAlertInner />
    </Suspense>
  );
}
