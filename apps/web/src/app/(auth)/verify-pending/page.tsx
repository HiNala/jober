"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { Button, buttonVariants } from "@/components/ui/button";
import { fetchEmailDelivery, resendVerificationEmail } from "@/lib/api/auth";
import { VERIFY_PENDING, VERIFY_UNAVAILABLE } from "@/lib/auth/copy";
import { parseAuthError } from "@/lib/auth/parse-auth-error";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const RESEND_COOLDOWN_SECONDS = 60;

export default function VerifyPendingPage() {
  const [inboxDelivery, setInboxDelivery] = useState<boolean | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    void fetchEmailDelivery()
      .then((status) => setInboxDelivery(status.inbox_delivery))
      .catch(() => setInboxDelivery(false));
  }, []);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = window.setTimeout(() => setCooldown((value) => value - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [cooldown]);

  const onResend = useCallback(() => {
    setPending(true);
    setError(null);
    setMessage(null);
    void resendVerificationEmail()
      .then((result) => {
        setMessage(result.message);
        setCooldown(RESEND_COOLDOWN_SECONDS);
      })
      .catch((err: unknown) => setError(parseAuthError(err, "Could not resend. Try again later.")))
      .finally(() => setPending(false));
  }, []);

  if (inboxDelivery === null) {
    return (
      <AuthFormShell title="Check your email" subtitle="Loading delivery status…">
        <p className="text-sm text-muted-foreground">One moment…</p>
      </AuthFormShell>
    );
  }

  if (!inboxDelivery) {
    return (
      <AuthFormShell
        title={VERIFY_UNAVAILABLE.title}
        subtitle={VERIFY_UNAVAILABLE.body}
        footer={
          <Link href="/dashboard" className="font-medium text-primary underline underline-offset-4">
            Continue to dashboard
          </Link>
        }
      >
        <Link href="/dashboard" className={buttonVariants({ size: "sm" })}>
          Open dashboard
        </Link>
      </AuthFormShell>
    );
  }

  return (
    <AuthFormShell
      title={VERIFY_PENDING.title}
      subtitle={VERIFY_PENDING.body}
      footer={
        <>
          <Link href="/dashboard" className="font-medium text-primary underline underline-offset-4">
            Continue to dashboard
          </Link>
        </>
      }
    >
      <div className="space-y-4">
        {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
        {error ? <AuthFormError message={error} /> : null}
        <Button
          type="button"
          className={cn(motionPress, "w-full")}
          disabled={pending || cooldown > 0}
          onClick={onResend}
        >
          {pending
            ? "Sending…"
            : cooldown > 0
              ? `${VERIFY_PENDING.cooldownLabel} ${cooldown}s`
              : VERIFY_PENDING.resendLabel}
        </Button>
      </div>
    </AuthFormShell>
  );
}
