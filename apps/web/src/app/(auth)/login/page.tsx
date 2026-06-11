"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { AuthOAuthAlert } from "@/components/auth/auth-oauth-alert";
import { GoogleSignInBlock } from "@/components/auth/google-sign-in-block";
import { PasswordField } from "@/components/auth/password-field";
import { fieldDescribedBy, FormField } from "@/components/forms/form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { login } from "@/lib/api/auth";
import { validateEmail } from "@/lib/forms/client-validation";
import { useFormSubmit } from "@/lib/forms/use-form-submit";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { pending, formError, fieldErrors, run, setClientFieldErrors } = useFormSubmit({
    fallbackError: "Invalid email or password.",
  });

  return (
    <AuthFormShell
      title="Sign in"
      subtitle="Access your workspace and runs."
      footer={
        <>
          No account?{" "}
          <Link href="/signup" className="font-medium text-primary underline underline-offset-4">
            Create one
          </Link>
        </>
      }
    >
      <AuthOAuthAlert />
      <GoogleSignInBlock />
      <form
        className="space-y-4"
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          const emailError = validateEmail(email);
          if (emailError) {
            setClientFieldErrors({ email: emailError });
            return;
          }
          if (!password) {
            setClientFieldErrors({ password: "Password is required" });
            return;
          }
          void run(async () => {
            await login(email, password);
            router.push("/dashboard");
          });
        }}
      >
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
          showMeter={false}
          autoComplete="current-password"
          error={fieldErrors.password}
        />
        <div className="text-right text-sm">
          <Link href="/forgot-password" className="text-muted-foreground hover:text-foreground">
            Forgot password?
          </Link>
        </div>
        {formError ? <AuthFormError message={formError} /> : null}
        <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
          {pending ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </AuthFormShell>
  );
}
