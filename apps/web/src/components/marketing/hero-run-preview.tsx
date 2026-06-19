"use client";

import { ProductVisual } from "@/components/marketing/product-visual";
import { motionHeroFloat } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

/** Centered hero product loop with brand glow and reduced-motion-safe float. */
export function HeroRunPreview({ className }: { className?: string }) {
  return (
    <div className={cn("relative mx-auto w-full max-w-3xl", className)}>
      <div
        className="pointer-events-none absolute inset-0 -z-10 scale-110 bg-[radial-gradient(ellipse_at_center,var(--primary)_0%,transparent_68%)] opacity-10"
        aria-hidden
      />
      <div className={cn("relative", motionHeroFloat)}>
        <ProductVisual className="shadow-lg" />
      </div>
    </div>
  );
}
