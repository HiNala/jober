"use client";

import Link from "next/link";
import dynamic from "next/dynamic";

import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const ProductVisual = dynamic(
  () => import("@/components/marketing/product-visual").then((m) => m.ProductVisual),
  { ssr: false },
);

type AuthBrandPanelProps = {
  compact?: boolean;
  className?: string;
};

export function AuthBrandPanel({ compact = false, className }: AuthBrandPanelProps) {
  if (compact) {
    return (
      <div className={cn("flex items-center gap-2 px-6 py-4 border-b border-border/25", className)}>
        <Link href="/" className="text-sm font-semibold tracking-tight">
          Jober
        </Link>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative flex h-full flex-col justify-between overflow-hidden p-10 xl:p-14",
        "bg-[oklch(0.16_0.025_250)]",
        className,
      )}
    >
      {/* Background orbs */}
      <div
        className="pointer-events-none absolute -left-1/3 -top-1/4 size-[80%] rounded-full bg-[oklch(0.42_0.14_250)]/25 blur-3xl"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -bottom-1/4 -right-1/4 size-[60%] rounded-full bg-[oklch(0.52_0.16_165)]/15 blur-3xl"
        aria-hidden
      />

      {/* Top — logo */}
      <div className="relative">
        <Link
          href="/"
          className="text-sm font-semibold tracking-tight text-white/50 hover:text-white/80 transition-colors"
        >
          Jober
        </Link>
      </div>

      {/* Center — headline + product visual */}
      <div className={cn("relative mx-auto w-full max-w-lg space-y-6", motionFadeIn)}>
        <div className="space-y-3">
          <p className="text-[0.7rem] font-medium uppercase tracking-[0.14em] text-white/35">
            Human-in-the-loop
          </p>
          <h2 className="text-2xl font-semibold leading-snug tracking-tight text-white xl:text-3xl">
            Apply to every job on your list.{" "}
            <span className="text-white/50">You review and submit.</span>
          </h2>
          <p className="text-sm leading-relaxed text-white/40">
            AI fills the form, you read the diff and approve. Your applications, your standard.
          </p>
        </div>

        <div className="overflow-hidden rounded-xl border border-white/10 shadow-2xl shadow-black/40">
          <ProductVisual />
        </div>
      </div>

      {/* Bottom — trust items */}
      <div className="relative flex flex-wrap gap-x-5 gap-y-1.5">
        {["Review before submit", "No CAPTCHA bypass", "Your data, your control"].map((item) => (
          <p key={item} className="flex items-center gap-1.5 text-xs text-white/30">
            <span className="size-1 rounded-full bg-[oklch(0.52_0.16_165)]/60" aria-hidden />
            {item}
          </p>
        ))}
      </div>
    </div>
  );
}
