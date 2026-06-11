"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthEdgeState } from "@/components/auth/auth-edge-state";
import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { PasswordField } from "@/components/auth/password-field";
import { PageLoading } from "@/components/states/page-states";
import { Button } from "@/components/ui/button";
import { confirmGoogleLink } from "@/lib/api/auth";
import { LINK_GOOGLE_INVALID } from "@/lib/auth/copy";
import { parseAuthError } from "@/lib/auth/parse-auth-error";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

function LinkGoogleForm() {
  const router = useRouter();
  const params = useSearchParams();
  const token = params.get("token");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (!token) {
    return (
      <AuthEdgeState
        title={LINK_GOOGLE_INVALID.title}
        description={LINK_GOOGLE_INVALID.description}
        actionHref="/login"
        actionLabel="Back to sign in"
      />
    );
  }

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        setPending(true);
        setError(null);
        void confirmGoogleLink(token, password)
          .then(() => router.push("/dashboard"))
          .catch((err: unknown) =>
            setError(parseAuthError(err, "Password incorrect or link expired.")),
          )
          .finally(() => setPending(false));
      }}
    >
      <PasswordField
        id="link-password"
        label="Account password"
        value={password}
        onChange={setPassword}
        showMeter={false}
        autoComplete="current-password"
      />
      {error ? <AuthFormError message={error} /> : null}
      <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
        {pending ? "Linking…" : "Link and continue"}
      </Button>
    </form>
  );
}

export default function LinkGooglePage() {
  return (
    <AuthFormShell
      title="Link Google account"
      subtitle="An account with this email already exists. Confirm with your password to link Google sign-in."
      footer={
        <Link href="/login" className="font-medium text-primary underline underline-offset-4">
          Back to sign in
        </Link>
      }
    >
      <Suspense fallback={<PageLoading label="Loading…" />}>
        <LinkGoogleForm />
      </Suspense>
    </AuthFormShell>
  );
}
