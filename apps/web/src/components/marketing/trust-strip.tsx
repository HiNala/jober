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
        "flex flex-wrap items-center justify-center gap-0",
        className,
      )}
      aria-label="Trust and privacy commitments"
    >
      {items.map((item, i) => (
        <div key={item} className="relative flex items-center gap-2.5 px-5 py-3.5">
          {i > 0 && (
            <span
              className="absolute left-0 top-1/2 hidden h-4 w-px -translate-y-1/2 bg-border/50 sm:block"
              aria-hidden
            />
          )}
          <span className="inline-block size-1.5 shrink-0 rounded-full bg-primary/50" aria-hidden />
          <span className="text-[0.8rem] font-medium text-foreground/60">{item}</span>
        </div>
      ))}
    </div>
  );
}
