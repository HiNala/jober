import Link from "next/link";

import { BrandSignature } from "@/components/marketing/brand-signature";
import { ProductVisual } from "@/components/marketing/product-visual";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

type AuthBrandPanelProps = {
  compact?: boolean;
  className?: string;
};

export function AuthBrandPanel({ compact = false, className }: AuthBrandPanelProps) {
  return (
    <div
      className={cn(
        "relative flex flex-col justify-center overflow-hidden border-border/60 bg-muted/15",
        compact ? "border-b px-6 py-5" : "border-r p-10 xl:p-14",
        className,
      )}
    >
      <BrandSignature />
      <div className={cn("relative mx-auto w-full max-w-lg", motionFadeIn)}>
        <Link href="/" className="text-sm font-semibold tracking-tight text-primary">
          Jober
        </Link>
        <p className="mt-3 text-xl font-semibold tracking-tight md:text-2xl">
          Assisted applications you control
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          Import your tracker, generate tailored letters, and review every submit before it leaves
          your hands.
        </p>
        {!compact ? (
          <div className="mt-8">
            <ProductVisual />
          </div>
        ) : null}
      </div>
    </div>
  );
}
