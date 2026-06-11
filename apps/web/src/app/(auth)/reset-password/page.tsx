"use client";

import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthEdgeState } from "@/components/auth/auth-edge-state";
import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { PageLoading } from "@/components/states/page-states";
import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import { resetPassword } from "@/lib/api/auth";
import { RESET_TOKEN_MISSING } from "@/lib/auth/copy";
import { validateResetPassword } from "@/lib/forms/client-validation";
import { useFormSubmit } from "@/lib/forms/use-form-submit";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

function ResetForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const { pending, formError, fieldErrors, run, setClientFieldErrors } = useFormSubmit({
    fallbackError: "Reset link expired or invalid.",
  });

  if (!token) {
    return (
      <AuthEdgeState
        title={RESET_TOKEN_MISSING.title}
        description={RESET_TOKEN_MISSING.description}
        actionHref="/forgot-password"
        actionLabel="Request reset"
      />
    );
  }

  return (
    <form
      className="space-y-4"
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        const clientErrors = validateResetPassword(password);
        if (Object.keys(clientErrors).length > 0) {
          setClientFieldErrors(clientErrors);
          return;
        }
        void run(async () => {
          await resetPassword(token, password);
          router.push("/login");
        });
      }}
    >
      <PasswordField
        id="password"
        value={password}
        onChange={setPassword}
        label="New password"
        error={fieldErrors.password}
      />
      {formError ? <AuthFormError message={formError} /> : null}
      <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
        {pending ? "Updating…" : "Update password"}
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <AuthFormShell
      title="Choose a new password"
      subtitle="Use at least 10 characters with mixed case and a number."
      footer={
        <Link href="/login" className="font-medium text-primary underline underline-offset-4">
          Back to sign in
        </Link>
      }
    >
      <Suspense fallback={<PageLoading label="Loading reset form…" />}>
        <ResetForm />
      </Suspense>
    </AuthFormShell>
  );
}
