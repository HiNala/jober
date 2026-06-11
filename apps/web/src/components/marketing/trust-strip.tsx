import { Check } from "lucide-react";

import { AUTH_TRUST_ITEMS } from "@/lib/auth/copy";
import { cn } from "@/lib/utils";

export function TrustStrip({ className }: { className?: string }) {
  return (
    <ul
      className={cn(
        "flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-xs text-muted-foreground",
        className,
      )}
      aria-label="Trust and privacy commitments"
    >
      {AUTH_TRUST_ITEMS.map((item) => (
        <li key={item} className="inline-flex items-center gap-1.5">
          <Check className="size-3.5 shrink-0 text-accent" aria-hidden />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
