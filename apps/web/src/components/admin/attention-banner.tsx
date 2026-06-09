import { cn } from "@/lib/utils";

import type { AdminAttention } from "@/lib/api/admin-dashboard";

export function AttentionBanner({ items }: { items: AdminAttention[] }) {
  if (!items.length) return null;
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <p
          key={item.message}
          className={cn(
            "rounded-md border px-3 py-2 text-sm",
            item.level === "error"
              ? "border-destructive/40 bg-destructive/10 text-destructive"
              : item.level === "warn"
                ? "border-amber-500/40 bg-amber-500/10 text-amber-900 dark:text-amber-100"
                : "border-border bg-muted/50 text-muted-foreground",
          )}
        >
          {item.message}
        </p>
      ))}
    </div>
  );
}
