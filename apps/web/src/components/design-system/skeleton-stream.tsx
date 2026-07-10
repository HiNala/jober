import { motionSkeleton } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export type SkeletonStreamAlign = "left" | "right" | "mixed";

export interface SkeletonStreamProps {
  /** Number of rounded bars to render. */
  lines?: number;
  /** Left = assistant-style, right = user-style, mixed alternates. */
  align?: SkeletonStreamAlign;
  className?: string;
  /** Accessible label for the loading region. */
  label?: string;
}

const WIDTHS = ["w-[72%]", "w-[88%]", "w-[56%]", "w-[78%]", "w-[64%]", "w-[82%]"] as const;

function lineAlign(index: number, align: SkeletonStreamAlign): "left" | "right" {
  if (align === "left") return "left";
  if (align === "right") return "right";
  return index % 3 === 2 ? "right" : "left";
}

/**
 * Hyperagent-style rounded loading bars for stream / chat skeletons.
 */
export function SkeletonStream({
  lines = 5,
  align = "mixed",
  className,
  label = "Loading",
}: SkeletonStreamProps) {
  const count = Math.max(1, Math.min(lines, 12));

  return (
    <div
      className={cn("flex flex-col gap-2.5", className)}
      role="status"
      aria-busy="true"
      aria-label={label}
      data-slot="skeleton-stream"
    >
      {Array.from({ length: count }, (_, i) => {
        const side = lineAlign(i, align);
        return (
          <div
            key={i}
            className={cn("flex w-full", side === "right" ? "justify-end" : "justify-start")}
          >
            <div
              className={cn(
                "h-3 max-w-full rounded-full",
                motionSkeleton,
                WIDTHS[i % WIDTHS.length],
                side === "right" ? "rounded-br-md" : "rounded-bl-md",
              )}
            />
          </div>
        );
      })}
      <span className="sr-only">{label}</span>
    </div>
  );
}
