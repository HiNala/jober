"use client";

import { Check, Sparkles } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const PRO_PERKS = [
  "Higher batch size and monthly run limits",
  "Priority support as we grow billing",
  "Full analytics and workspace insights",
] as const;

/**
 * Post-checkout celebration when returning from Stripe with ?checkout=success.
 */
export function UnlockModal() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const open = searchParams.get("checkout") === "success";

  function dismiss() {
    const params = new URLSearchParams(searchParams.toString());
    params.delete("checkout");
    const next = params.toString();
    router.replace(next ? `/pricing?${next}` : "/pricing");
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) dismiss();
      }}
    >
      <DialogContent className="sm:max-w-md" data-testid="unlock-modal">
        <DialogHeader>
          <div className="mb-1 flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Sparkles className="size-5" aria-hidden />
          </div>
          <DialogTitle>Pro is unlocked</DialogTitle>
          <DialogDescription>
            Welcome to Pro. Your workspace limits are raised as soon as Stripe confirms the
            subscription (usually seconds).
          </DialogDescription>
        </DialogHeader>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {PRO_PERKS.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
              {item}
            </li>
          ))}
        </ul>
        <DialogFooter className="sm:justify-stretch">
          <Button
            type="button"
            className={cn(motionPress, "w-full")}
            data-testid="unlock-open-dashboard"
            onClick={() => {
              router.push("/dashboard");
            }}
          >
            Open dashboard
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
