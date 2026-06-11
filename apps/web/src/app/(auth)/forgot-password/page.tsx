"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { AuthFormSuccess } from "@/components/auth/auth-form-success";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { fetchEmailDelivery, forgotPassword } from "@/lib/api/auth";
import { forgotPasswordSubtitle, forgotPasswordSuccess } from "@/lib/auth/copy";
import { parseAuthError } from "@/lib/auth/parse-auth-error";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inboxDelivery, setInboxDelivery] = useState(false);

  useEffect(() => {
    void fetchEmailDelivery()
      .then((status) => setInboxDelivery(status.inbox_delivery))
      .catch(() => setInboxDelivery(false));
  }, []);

  const successCopy = forgotPasswordSuccess(inboxDelivery);

  return (
    <AuthFormShell
      title="Reset password"
      subtitle={forgotPasswordSubtitle(inboxDelivery)}
      footer={
        <Link href="/login" className="font-medium text-primary underline underline-offset-4">
          Back to sign in
        </Link>
      }
    >
      {sent ? (
        <AuthFormSuccess
          title={successCopy.title}
          description={successCopy.body}
          action={
            <Link href="/login" className={buttonVariants({ size: "sm" })}>
              Return to sign in
            </Link>
          }
        />
      ) : (
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            setPending(true);
            setError(null);
            void forgotPassword(email)
              .then(() => setSent(true))
              .catch((err: unknown) =>
                setError(parseAuthError(err, "Could not process request. Try again.")),
              )
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
          {error ? <AuthFormError message={error} /> : null}
          <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
            {pending ? "Submitting…" : "Request reset"}
          </Button>
        </form>
      )}
    </AuthFormShell>
  );
}
