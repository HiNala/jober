"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import { confirmGoogleLink } from "@/lib/api/auth";
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
      <AuthFormShell title="Link Google account" subtitle="This link is invalid or expired.">
        <p className="text-sm text-muted-foreground">Start sign-in again from the login page.</p>
      </AuthFormShell>
    );
  }

  return (
    <AuthFormShell
      title="Link Google account"
      subtitle="An account with this email already exists. Confirm with your password to link Google sign-in."
    >
      <form
        className="space-y-4"
        onSubmit={(event) => {
          event.preventDefault();
          setPending(true);
          setError(null);
          void confirmGoogleLink(token, password)
            .then(() => router.push("/dashboard"))
            .catch(() => setError("Password incorrect or link expired."))
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
        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}
        <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
          {pending ? "Linking…" : "Link and continue"}
        </Button>
      </form>
    </AuthFormShell>
  );
}

export default function LinkGooglePage() {
  return (
    <Suspense fallback={<div className="p-6 text-center text-sm text-muted-foreground">Loading…</div>}>
      <LinkGoogleForm />
    </Suspense>
  );
}
