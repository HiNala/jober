"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

import { joinProWaitlist } from "@/lib/api/waitlist";
import { ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

type FormState = "idle" | "loading" | "success" | "duplicate" | "error";

export function ProWaitlistForm({ className }: { className?: string }) {
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [state, setState] = useState<FormState>("idle");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!consent) {
      setError("Please confirm we can email you when Pro launches.");
      return;
    }
    setState("loading");
    try {
      const result = await joinProWaitlist({ email, consentContact: consent });
      setState(result.status === "already_registered" ? "duplicate" : "success");
    } catch (err) {
      setState("error");
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong. Try again in a moment.");
      }
    }
  }

  if (state === "success" || state === "duplicate") {
    return (
      <div
        className={cn("rounded-lg border border-primary/30 bg-primary/5 p-4 text-sm", className)}
        role="status"
      >
        <p className="font-medium text-foreground">
          {state === "duplicate" ? "You're already on the list." : "You're on the Pro waitlist."}
        </p>
        <p className="mt-1 text-muted-foreground">
          We will email you at <span className="font-medium text-foreground">{email}</span> when
          Stripe checkout opens. No spam — one launch note.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className={cn("space-y-3", className)} noValidate>
      <div className="space-y-2">
        <Label htmlFor="pro-waitlist-email" className="text-sm">
          Email for early access
        </Label>
        <Input
          id="pro-waitlist-email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          disabled={state === "loading"}
        />
      </div>
      <label className="flex items-start gap-2 text-xs text-muted-foreground">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          disabled={state === "loading"}
          className="mt-0.5"
        />
        <span>
          I agree Jober may email me about Pro billing launch. See our{" "}
          <a href="/privacy" className="font-medium text-foreground underline underline-offset-2">
            privacy policy
          </a>
          .
        </span>
      </label>
      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
      <Button type="submit" className="w-full" disabled={state === "loading"}>
        {state === "loading" ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden />
            Joining…
          </>
        ) : (
          "Join Pro waitlist"
        )}
      </Button>
    </form>
  );
}
