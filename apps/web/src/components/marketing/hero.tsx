"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { buttonVariants } from "@/components/ui/button";
import { motionHeroStagger, motionSkeleton } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const HeroRunPreview = dynamic(
  () =>
    import("@/components/marketing/hero-run-preview").then((mod) => ({
      default: mod.HeroRunPreview,
    })),
  {
    loading: () => (
      <div
        className={cn("w-full rounded-xl border border-slate-100 bg-slate-50 aspect-[4/3]", motionSkeleton)}
        aria-hidden
      />
    ),
  },
);

export function MarketingHero() {
  return (
    <section
      aria-labelledby="hero-heading"
      className="relative bg-white"
    >
      {/* Very subtle top-left glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-40 top-0 size-[700px] rounded-full opacity-60"
        style={{
          background: "radial-gradient(circle, oklch(0.88 0.06 250 / 0.4) 0%, transparent 65%)",
        }}
      />

      <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-6 pb-20 pt-8 lg:grid-cols-[1fr_1.05fr] lg:gap-16 lg:pb-28 lg:pt-12">

        {/* ── Left: copy ───────────────────────────────────────── */}
        <div className={cn("flex flex-col", motionHeroStagger(0))}>

          {/* Eyebrow pill */}
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3.5 py-1.5">
            <span className="size-1.5 rounded-full bg-primary" aria-hidden />
            <span className="font-mono text-[0.6rem] font-semibold uppercase tracking-[0.18em] text-primary">
              Human-in-the-loop job applications
            </span>
          </div>

          {/* Headline */}
          <h1
            id="hero-heading"
            className={cn("mt-6 font-bold leading-[1.08] tracking-[-0.025em] text-slate-900", motionHeroStagger(1))}
            style={{ fontSize: "clamp(2.4rem, 5vw, 3.75rem)" }}
          >
            Apply to every job
            <br />
            <span className="text-primary">at your quality bar.</span>
          </h1>

          {/* Subhead */}
          <p
            className={cn("mt-5 max-w-[440px] text-[1.0625rem] leading-relaxed text-slate-500", motionHeroStagger(2))}
          >
            AI fills the form. You read the diff and approve before anything
            gets sent. Your applications, your standard.
          </p>

          {/* CTAs */}
          <div className={cn("mt-8 flex flex-wrap items-center gap-3", motionHeroStagger(3))}>
            <MarketingCtaLink
              href="/signup"
              feature="landing_hero_signup"
              size="lg"
              variant="default"
              className="rounded-full px-8 font-semibold shadow-md shadow-blue-200"
            >
              Get started free
              <ArrowRight className="size-4" aria-hidden />
            </MarketingCtaLink>
            <Link
              href="/how-it-works"
              className={cn(
                buttonVariants({ variant: "outline", size: "lg" }),
                "rounded-full px-8 font-medium text-slate-600 hover:text-slate-900",
              )}
            >
              See how it works
            </Link>
          </div>

          {/* Trust micro-stats */}
          <div
            className={cn(
              "mt-8 flex flex-wrap gap-x-5 gap-y-2 font-mono text-[0.62rem] text-slate-400",
              motionHeroStagger(4),
            )}
          >
            {[
              "Review before submit",
              "No CAPTCHA bypass",
              "No hidden auto-submit",
              "BYOK supported",
            ].map((item) => (
              <span key={item} className="flex items-center gap-1.5">
                <span className="size-1 rounded-full bg-primary/50" aria-hidden />
                {item}
              </span>
            ))}
          </div>
        </div>

        {/* ── Right: live product demo ──────────────────────────── */}
        <div
          className={cn("relative hidden lg:block", motionHeroStagger(5))}
        >
          {/* Glow behind frame */}
          <div
            aria-hidden
            className="pointer-events-none absolute -inset-6 rounded-3xl opacity-70"
            style={{
              background: "radial-gradient(ellipse 90% 80% at 50% 50%, oklch(0.88 0.06 250 / 0.5) 0%, transparent 70%)",
            }}
          />

          {/* Browser chrome frame */}
          <div className="relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-[0_20px_60px_-12px_rgba(0,0,0,0.12),0_0_0_1px_rgba(0,0,0,0.04)]">
            {/* Title bar */}
            <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50/80 px-4 py-3">
              <span className="size-3 rounded-full bg-red-400/80" aria-hidden />
              <span className="size-3 rounded-full bg-amber-400/80" aria-hidden />
              <span className="size-3 rounded-full bg-emerald-400/80" aria-hidden />
              <div className="mx-3 flex-1 rounded-md border border-slate-200 bg-white px-3 py-1">
                <span className="font-mono text-[10px] text-slate-400">
                  app.jober.app/runs/sr_northwind
                </span>
              </div>
            </div>
            {/* Product */}
            <div className="p-4">
              <HeroRunPreview />
            </div>
          </div>
        </div>

      </div>

      {/* Mobile demo (stacked below copy) */}
      <div className={cn("px-6 pb-10 lg:hidden", motionHeroStagger(5))}>
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg">
          <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-3">
            <span className="size-2.5 rounded-full bg-red-400/80" aria-hidden />
            <span className="size-2.5 rounded-full bg-amber-400/80" aria-hidden />
            <span className="size-2.5 rounded-full bg-emerald-400/80" aria-hidden />
          </div>
          <div className="p-3">
            <HeroRunPreview />
          </div>
        </div>
      </div>

      {/* Smooth bottom transition into trust strip / next section */}
      <div
        aria-hidden
        className="h-px w-full bg-slate-100"
      />
    </section>
  );
}
