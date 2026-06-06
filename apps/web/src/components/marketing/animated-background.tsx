import { cn } from "@/lib/utils";

export function AnimatedBackground({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 overflow-hidden",
        className,
      )}
      aria-hidden
    >
      <div
        className={cn(
          "absolute -left-1/4 top-0 size-[80%] rounded-full bg-primary/20 blur-3xl",
          "motion-safe:animate-[jober-drift_18s_ease-in-out_infinite]",
        )}
      />
      <div
        className={cn(
          "absolute -right-1/4 bottom-0 size-[70%] rounded-full bg-accent/15 blur-3xl",
          "motion-safe:animate-[jober-drift_22s_ease-in-out_infinite_reverse]",
        )}
      />
    </div>
  );
}
