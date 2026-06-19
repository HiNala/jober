"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { GoogleSignInBlock } from "@/components/auth/google-sign-in-block";
import { PasswordField } from "@/components/auth/password-field";
import { fieldDescribedBy, FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { track } from "@/lib/analytics/events";
import { fetchEmailDelivery, register } from "@/lib/api/auth";
import { SIGNUP_VALUE_BULLETS, signupSubtitle } from "@/lib/auth/copy";
import { validateSignup } from "@/lib/forms/client-validation";
import { useFormSubmit } from "@/lib/forms/use-form-submit";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [inboxDelivery, setInboxDelivery] = useState(false);
  const { pending, formError, fieldErrors, run, setClientFieldErrors } = useFormSubmit({
    fallbackError: "Could not create account. Try a different email.",
    fieldAliases: { display_name: "name" },
  });

  useEffect(() => {
    track("auth.signup_started", { method: "native" });
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
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          const clientErrors = validateSignup({ email, password, displayName });
          if (Object.keys(clientErrors).length > 0) {
            setClientFieldErrors(clientErrors);
            return;
          }
          void run(async () => {
            const user = await register(email, password, displayName || undefined);
            track("auth.signup_completed", { method: "native" });
            if (inboxDelivery && !user.email_verified) {
              router.push("/verify-pending");
              return user;
            }
            router.push("/dashboard");
            return user;
          });
        }}
      >
        <FormField id="name" label="Display name" error={fieldErrors.name}>
          <Input
            id="name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            autoComplete="name"
            aria-invalid={fieldErrors.name ? true : undefined}
            aria-describedby={fieldDescribedBy(fieldErrors.name, "name")}
          />
        </FormField>
        <FormField id="email" label="Email" error={fieldErrors.email}>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            aria-invalid={fieldErrors.email ? true : undefined}
            aria-describedby={fieldDescribedBy(fieldErrors.email, "email")}
          />
        </FormField>
        <PasswordField
          id="password"
          value={password}
          onChange={setPassword}
          autoComplete="new-password"
          error={fieldErrors.password}
        />
        {formError ? <AuthFormError message={formError} /> : null}
        <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
          {pending ? "Creating…" : "Create account"}
        </Button>
      </form>
    </AuthFormShell>
  );
}
