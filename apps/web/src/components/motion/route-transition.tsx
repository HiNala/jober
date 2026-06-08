"use client";

import { usePathname } from "next/navigation";

import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

/** Page/route content enter — keyed by pathname; calm fade under reduced-motion. */
export function RouteTransition({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const pathname = usePathname();

  return (
    <div key={pathname} className={cn(motionFadeIn, className)}>
      {children}
    </div>
  );
}
