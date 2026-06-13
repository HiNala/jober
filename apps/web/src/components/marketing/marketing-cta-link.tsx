"use client";

import Link from "next/link";
import type { ComponentProps } from "react";

import { buttonVariants } from "@/components/ui/button";
import { trackMarketingCta } from "@/lib/marketing/cta";
import { brandBorderBeam, motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

type MarketingCtaLinkProps = ComponentProps<typeof Link> & {
  feature: string;
  variant?: "default" | "outline" | "ghost" | "link";
  size?: "default" | "sm" | "lg";
};

export function MarketingCtaLink({
  feature,
  href,
  className,
  children,
  onClick,
  variant = "default",
  size = "default",
  ...rest
}: MarketingCtaLinkProps) {
  return (
    <Link
      href={href}
      className={cn(
        buttonVariants({ variant, size }),
        motionPress,
        variant === "default" && brandBorderBeam,
        "inline-flex items-center gap-2",
        className,
      )}
      onClick={(event) => {
        trackMarketingCta(feature);
        onClick?.(event);
      }}
      {...rest}
    >
      {children}
    </Link>
  );
}
