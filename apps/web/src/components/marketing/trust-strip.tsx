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
    <div
      className={cn(
        "flex flex-wrap items-center justify-center gap-px",
        className,
      )}
      aria-label="Trust and privacy commitments"
    >
      {items.map((item, i) => (
        <div
          key={item}
          className="flex items-center gap-2 px-5 py-3"
        >
          {i > 0 && (
            <span
              className="absolute -left-px hidden h-4 w-px bg-border/40 sm:block"
              aria-hidden
            />
          )}
          <span
            className="inline-block size-1.5 rounded-full bg-accent/70 shrink-0"
            aria-hidden
          />
          <span className="text-sm font-medium text-foreground/75">{item}</span>
        </div>
      ))}
    </div>
  );
}
