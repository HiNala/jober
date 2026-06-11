"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { AuthFormSuccess } from "@/components/auth/auth-form-success";
import { PageLoading } from "@/components/states/page-states";
import { Button, buttonVariants } from "@/components/ui/button";
import { verifyEmail } from "@/lib/api/auth";
import { VERIFY_EMAIL_INVALID, VERIFY_EMAIL_SUCCESS } from "@/lib/auth/copy";
import { parseAuthError } from "@/lib/auth/parse-auth-error";

function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [state, setState] = useState<"loading" | "success" | "error">(token ? "loading" : "error");
  const [error, setError] = useState<string | null>(token ? null : VERIFY_EMAIL_INVALID.body);

  useEffect(() => {
    if (!token) {
      return;
    }
    void verifyEmail(token)
      .then(() => setState("success"))
      .catch((err: unknown) => {
        setState("error");
        setError(parseAuthError(err, VERIFY_EMAIL_INVALID.body));
      });
  }, [token]);

  if (state === "loading") {
    return (
      <AuthFormShell title="Verifying email" subtitle="Confirming your link…">
        <PageLoading label="Verifying…" />
      </AuthFormShell>
    );
  }

  if (state === "success") {
    return (
      <AuthFormShell title={VERIFY_EMAIL_SUCCESS.title} subtitle={VERIFY_EMAIL_SUCCESS.body}>
        <AuthFormSuccess
          title={VERIFY_EMAIL_SUCCESS.title}
          description={VERIFY_EMAIL_SUCCESS.body}
          action={
            <Button type="button" onClick={() => router.push("/dashboard")}>
              Go to dashboard
            </Button>
          }
        />
      </AuthFormShell>
    );
  }

  return (
    <AuthFormShell title={VERIFY_EMAIL_INVALID.title} subtitle={error ?? VERIFY_EMAIL_INVALID.body}>
      <Link href="/login" className={buttonVariants({ size: "sm" })}>
        Back to sign in
      </Link>
    </AuthFormShell>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <AuthFormShell title="Verifying email" subtitle="Loading…">
          <PageLoading label="Loading…" />
        </AuthFormShell>
      }
    >
      <VerifyEmailForm />
    </Suspense>
  );
}
