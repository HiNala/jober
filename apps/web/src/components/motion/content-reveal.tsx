"use client";

import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

/** Skeleton → content cross-fade when async data resolves. */
export function ContentReveal({
  ready,
  skeleton,
  children,
  className,
}: {
  ready: boolean;
  skeleton: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  if (!ready) {
    return <>{skeleton}</>;
  }

  return (
    <div key="content" className={cn(motionFadeIn, className)}>
      {children}
    </div>
  );
}
