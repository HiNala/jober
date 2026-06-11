"use client";

import { Info } from "lucide-react";

import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function LlmProviderBanner({
  provider,
  className,
}: {
  provider: string | undefined;
  className?: string;
}) {
  if (!provider || provider !== "template") {
    return null;
  }

  return (
    <div
      className={cn(
        "flex items-start gap-2 rounded-lg border border-border/60 bg-muted/40 px-3 py-2 text-sm",
        motionFadeIn,
        className,
      )}
      role="status"
    >
      <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
      <p>
        <span className="font-medium">Template draft</span> — no live LLM key is configured. Letters
        use structured templates until you add a provider in Settings → AI &amp; providers.
      </p>
    </div>
  );
}
