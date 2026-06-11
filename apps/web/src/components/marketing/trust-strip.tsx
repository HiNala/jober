import { Check } from "lucide-react";

import { AUTH_TRUST_ITEMS } from "@/lib/auth/copy";
import { cn } from "@/lib/utils";

export function TrustStrip({
  className,
  items = AUTH_TRUST_ITEMS,
}: {
  className?: string;
  items?: readonly string[];
}) {
  return (
    <ul
      className={cn(
        "flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-sm text-muted-foreground",
        className,
      )}
      aria-label="Trust and privacy commitments"
    >
      {items.map((item) => (
        <li key={item} className="inline-flex items-center gap-1.5">
          <Check className="size-3.5 shrink-0 text-accent" aria-hidden />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
