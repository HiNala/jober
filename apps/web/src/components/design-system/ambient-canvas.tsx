import { motionAmbientDrift } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface AmbientCanvasProps {
  className?: string;
  /** Slow multi-hue drift; disabled under prefers-reduced-motion via motion-safe. */
  drift?: boolean;
  children?: React.ReactNode;
}

/**
 * Full-bleed soft multi-hue ambient gradient (lavender → peach → cool blue).
 * Brand signature for live canvas idle/loading and empty command center.
 */
export function AmbientCanvas({
  className,
  drift = true,
  children,
}: AmbientCanvasProps) {
  return (
    <div
      className={cn("relative isolate overflow-hidden", className)}
      data-slot="ambient-canvas"
    >
      <div
        aria-hidden
        className={cn(
          "pointer-events-none absolute inset-0 jober-ambient-canvas",
          drift && motionAmbientDrift,
        )}
      />
      {children ? <div className="relative z-10 h-full w-full">{children}</div> : null}
    </div>
  );
}
