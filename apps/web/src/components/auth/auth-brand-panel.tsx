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
      <div className={cn("flex items-center gap-2 border-b border-border/25 px-6 py-4", className)}>
        <Link href="/" className="text-sm font-semibold tracking-tight text-foreground">
          Jober
        </Link>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative flex h-full flex-col justify-between overflow-hidden p-10 xl:p-14",
        "bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800",
        className,
      )}
    >
      {/* Background atmosphere */}
      <div
        className="pointer-events-none absolute -left-20 -top-20 size-[500px] rounded-full opacity-40 blur-3xl"
        style={{ background: "radial-gradient(circle, oklch(0.75 0.12 245) 0%, transparent 70%)" }}
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -bottom-20 -right-20 size-[400px] rounded-full opacity-30 blur-3xl"
        style={{ background: "radial-gradient(circle, oklch(0.60 0.18 280) 0%, transparent 70%)" }}
        aria-hidden
      />
      {/* Subtle grid overlay */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(white 1px, transparent 1px), linear-gradient(90deg, white 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Top — logo + tagline */}
      <div className="relative flex items-center gap-2.5">
        <div className="flex size-7 items-center justify-center rounded-lg bg-white/20 backdrop-blur-sm">
          <span className="text-xs font-bold text-white">J</span>
        </div>
        <Link
          href="/"
          className="text-sm font-semibold tracking-tight text-white/90 transition-colors hover:text-white"
        >
          Jober
        </Link>
      </div>

      {/* Center — headline + product preview */}
      <div className={cn("relative mx-auto w-full max-w-lg space-y-8", motionFadeIn)}>
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[0.62rem] font-medium uppercase tracking-[0.18em] text-blue-100 backdrop-blur-sm">
            <span className="size-1.5 rounded-full bg-emerald-400" aria-hidden />
            Human-in-the-loop
          </div>
          <h2 className="text-2xl font-bold leading-snug tracking-tight text-white xl:text-3xl">
            Apply to every job on your list.{" "}
            <span className="text-blue-200">You review and submit.</span>
          </h2>
          <p className="text-sm leading-relaxed text-blue-100/70">
            AI fills the form, you read the diff and approve. Your applications,
            your standard.
          </p>
        </div>

        {/* Product preview — glass card on blue */}
        <div className="overflow-hidden rounded-xl border border-white/10 bg-white/[0.06] shadow-2xl shadow-black/30 backdrop-blur-sm">
          <ProductVisual className="!bg-transparent !shadow-none !border-0" />
        </div>
      </div>

      {/* Bottom — trust items */}
      <div className="relative flex flex-wrap gap-x-5 gap-y-2">
        {["Review before submit", "No CAPTCHA bypass", "Your data, your control"].map((item) => (
          <p key={item} className="flex items-center gap-2 text-xs text-blue-100/60">
            <span className="size-1.5 rounded-full bg-emerald-400/70" aria-hidden />
            {item}
          </p>
        ))}
      </div>
    </div>
  );
}
