"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthOAuthAlert } from "@/components/auth/auth-oauth-alert";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { GoogleSignInBlock } from "@/components/auth/google-sign-in-block";
import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { login } from "@/lib/api/auth";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  return (
    <AuthFormShell
      title="Sign in"
      subtitle="Access your workspace and runs."
      footer={
        <>
          No account?{" "}
          <Link href="/signup" className="text-primary underline-offset-4 hover:underline">
            Create one
          </Link>
        </>
      }
    >
      <AuthOAuthAlert />
      <GoogleSignInBlock />
      <form
        className="space-y-4"
        onSubmit={(event) => {
          event.preventDefault();
          setPending(true);
          setError(null);
          void login(email, password)
            .then(() => router.push("/dashboard"))
            .catch(() => setError("Invalid email or password."))
            .finally(() => setPending(false));
        }}
      >
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
        <PasswordField
          id="password"
          value={password}
          onChange={setPassword}
          showMeter={false}
          autoComplete="current-password"
        />
        <div className="text-right text-sm">
          <Link href="/forgot-password" className="text-muted-foreground hover:text-foreground">
            Forgot password?
          </Link>
        </div>
        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}
        <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
          {pending ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </AuthFormShell>
  );
}
