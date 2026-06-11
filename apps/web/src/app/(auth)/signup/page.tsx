"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { GoogleSignInBlock } from "@/components/auth/google-sign-in-block";
import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { trackEvent } from "@/lib/analytics/sdk";
import { fetchEmailDelivery, register } from "@/lib/api/auth";
import { SIGNUP_VALUE_BULLETS, signupSubtitle } from "@/lib/auth/copy";
import { parseAuthError } from "@/lib/auth/parse-auth-error";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [inboxDelivery, setInboxDelivery] = useState(false);

  useEffect(() => {
    trackEvent("signup.start");
    void fetchEmailDelivery()
      .then((status) => setInboxDelivery(status.inbox_delivery))
      .catch(() => setInboxDelivery(false));
  }, []);

  return (
    <AuthFormShell
      title="Create account"
      subtitle={signupSubtitle(inboxDelivery)}
      bullets={SIGNUP_VALUE_BULLETS}
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-primary underline underline-offset-4">
            Sign in
          </Link>
        </>
      }
    >
      <GoogleSignInBlock label="Sign up with Google" />
      <form
        className="space-y-4"
        onSubmit={(event) => {
          event.preventDefault();
          setPending(true);
          setError(null);
          void register(email, password, displayName || undefined)
            .then((user) => {
              if (inboxDelivery && !user.email_verified) {
                router.push("/verify-pending");
                return;
              }
              router.push("/dashboard");
            })
            .catch((err: unknown) =>
              setError(parseAuthError(err, "Could not create account. Try a different email.")),
            )
            .finally(() => setPending(false));
        }}
      >
        <div className="space-y-2">
          <label htmlFor="name" className="text-sm font-medium">
            Display name
          </label>
          <Input
            id="name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            autoComplete="name"
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">
            Email
          </label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <PasswordField id="password" value={password} onChange={setPassword} autoComplete="new-password" />
        {error ? <AuthFormError message={error} /> : null}
        <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
          {pending ? "Creating…" : "Create account"}
        </Button>
      </form>
    </AuthFormShell>
  );
}
