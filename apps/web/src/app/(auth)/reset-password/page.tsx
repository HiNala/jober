"use client";

import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import { resetPassword } from "@/lib/api/auth";
import { motionPress } from "@/lib/design/motion";

function ResetForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  if (!token) {
    return (
      <p className="text-sm text-destructive" role="alert">
        Missing reset token. Request a new link from{" "}
        <Link href="/forgot-password" className="underline">
          forgot password
        </Link>
        .
      </p>
    );
  }

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        setPending(true);
        setError(null);
        void resetPassword(token, password)
          .then(() => router.push("/login"))
          .catch(() => setError("Reset link expired or invalid."))
          .finally(() => setPending(false));
      }}
    >
      <PasswordField id="password" value={password} onChange={setPassword} label="New password" />
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="submit" className={`${motionPress} w-full`} disabled={pending}>
        {pending ? "Updating…" : "Update password"}
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <AuthFormShell title="Choose a new password">
      <Suspense fallback={<p className="text-sm text-muted-foreground">Loading…</p>}>
        <ResetForm />
      </Suspense>
    </AuthFormShell>
  );
}
