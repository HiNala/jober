"use client";

import Link from "next/link";
import { Wallet } from "lucide-react";

import { Button } from "@/components/ui/button";
import { motionAttentionEnter } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function LlmBudgetExceeded({
  message,
  className,
  onDismiss,
}: {
  message?: string;
  className?: string;
  onDismiss?: () => void;
}) {
  return (
    <div
      className={cn(
        "space-y-3 rounded-lg border border-amber-500/35 bg-amber-500/10 p-4",
        motionAttentionEnter,
        className,
      )}
      role="alert"
    >
      <div className="flex items-start gap-2">
        <Wallet className="mt-0.5 size-4 text-amber-700 dark:text-amber-300" aria-hidden />
        <div className="space-y-1">
          <p className="text-sm font-semibold">Monthly generation budget reached</p>
          <p className="text-sm text-muted-foreground">
            {message ??
              "Cover letter generation is paused until your plan resets or you add your own API key (BYOK)."}
          </p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" render={<Link href="/settings" />}>
          Open AI settings
        </Button>
        {onDismiss ? (
          <Button size="sm" variant="outline" onClick={onDismiss}>
            Dismiss
          </Button>
        ) : null}
      </div>
    </div>
  );
}
