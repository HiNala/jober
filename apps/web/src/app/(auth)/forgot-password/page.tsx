"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AuthFormError } from "@/components/auth/auth-form-error";
import { AuthFormShell } from "@/components/auth/auth-form-shell";
import { AuthFormSuccess } from "@/components/auth/auth-form-success";
import { fieldDescribedBy, FormField } from "@/components/forms/form-field";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { fetchEmailDelivery, forgotPassword } from "@/lib/api/auth";
import { forgotPasswordSubtitle, forgotPasswordSuccess } from "@/lib/auth/copy";
import { validateEmail } from "@/lib/forms/client-validation";
import { useFormSubmit } from "@/lib/forms/use-form-submit";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [inboxDelivery, setInboxDelivery] = useState(false);
  const { pending, formError, fieldErrors, run, setClientFieldErrors } = useFormSubmit({
    fallbackError: "Could not process request. Try again.",
  });

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
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            const emailError = validateEmail(email);
            if (emailError) {
              setClientFieldErrors({ email: emailError });
              return;
            }
            void run(async () => {
              await forgotPassword(email);
              setSent(true);
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
          {formError ? <AuthFormError message={formError} /> : null}
          <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
            {pending ? "Submitting…" : "Request reset"}
          </Button>
        </form>
      )}
    </AuthFormShell>
  );
}
