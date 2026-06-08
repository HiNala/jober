"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { PasswordField } from "@/components/auth/password-field";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { login } from "@/lib/api/auth";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

type ReAuthDialogProps = {
  open: boolean;
  emailHint?: string | null;
  onSuccess: () => void;
};

export function ReAuthDialog({ open, emailHint, onSuccess }: ReAuthDialogProps) {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState(emailHint ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  return (
    <Dialog open={open}>
      <DialogContent className="sm:max-w-md" showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>Session expired</DialogTitle>
          <DialogDescription>
            Sign in again to continue. Your page data is still here.
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            setPending(true);
            setError(null);
            void login(email, password)
              .then(async () => {
                await queryClient.invalidateQueries({ queryKey: ["auth"] });
                onSuccess();
              })
              .catch(() => setError("Invalid email or password."))
              .finally(() => setPending(false));
          }}
        >
          <div className="space-y-2">
            <label htmlFor="reauth-email" className="text-sm font-medium">
              Email
            </label>
            <Input
              id="reauth-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <PasswordField
            id="reauth-password"
            value={password}
            onChange={setPassword}
            showMeter={false}
            autoComplete="current-password"
          />
          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
          <Button type="submit" className={cn(motionPress, "w-full")} disabled={pending}>
            {pending ? "Signing in…" : "Continue"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
