"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { register } from "@/lib/api/auth";
import { motionPress } from "@/lib/design/motion";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  return (
    <AuthFormShell
      title="Create account"
      subtitle="Start applying with a private workspace."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="text-primary underline-offset-4 hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form
        className="space-y-4"
        onSubmit={(event) => {
          event.preventDefault();
          setPending(true);
          setError(null);
          void register(email, password, displayName || undefined)
            .then(() => router.push("/dashboard"))
            .catch(() => setError("Could not create account. Try a different email."))
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
        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}
        <Button type="submit" className={`${motionPress} w-full`} disabled={pending}>
          {pending ? "Creating…" : "Create account"}
        </Button>
      </form>
    </AuthFormShell>
  );
}
