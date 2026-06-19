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
        className={cn(
          "w-full rounded-2xl border border-slate-200 bg-slate-100",
          "aspect-[4/3]",
          motionSkeleton,
        )}
        aria-hidden
      />
    ),
  },
);

export function MarketingHero() {
  return (
    <>
      {/* ── Hero — white bg so nav pill blends seamlessly ─────────── */}
      <section
        aria-labelledby="hero-heading"
        className="relative overflow-hidden bg-white"
      >
        {/* Subtle bottom fade into next section */}
        <div
          aria-hidden
          className="pointer-events-none absolute bottom-0 inset-x-0 h-32"
          style={{
            background: "linear-gradient(to bottom, transparent, oklch(0.98 0.004 240))",
          }}
        />

        {/* Very subtle blue glow top-left behind copy */}
        <div
          aria-hidden
          className="pointer-events-none absolute -left-32 -top-32 size-[600px] rounded-full"
          style={{
            background: "radial-gradient(circle, oklch(0.42 0.14 250 / 0.05) 0%, transparent 70%)",
          }}
        />

        <div className="relative mx-auto max-w-7xl px-6 pb-0 pt-10 lg:pt-14">
          <div className="grid items-center gap-12 lg:grid-cols-2">

            {/* ── Left: copy ───────────────────────────────────────── */}
            <div className="max-w-xl">
              {/* Eyebrow */}
              <div
                className={cn(
                  "inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1",
                  motionHeroStagger(0),
                )}
              >
                <span className="size-1.5 rounded-full bg-primary" aria-hidden />
                <span className="font-mono text-[0.6rem] font-medium uppercase tracking-[0.2em] text-primary">
                  Human-in-the-loop job applications
                </span>
              </div>

              {/* Headline */}
              <h1
                id="hero-heading"
                className={cn(
                  "mt-5 font-bold leading-[1.06] tracking-[-0.025em] text-foreground",
                  motionHeroStagger(1),
                )}
                style={{ fontSize: "clamp(2.2rem, 5.5vw, 4rem)" }}
              >
                Apply to every job
                <br />
                <span className="text-primary">at your quality bar.</span>
              </h1>

              {/* Subhead */}
              <p
                className={cn(
                  "mt-5 max-w-md text-lg leading-relaxed text-muted-foreground",
                  motionHeroStagger(2),
                )}
              >
                AI fills the form. You read the diff and hit submit — your
                applications, your standard, your control.
              </p>

              {/* CTAs */}
              <div
                className={cn(
                  "mt-8 flex flex-wrap items-center gap-3",
                  motionHeroStagger(3),
                )}
              >
                <MarketingCtaLink
                  href="/signup"
                  feature="landing_hero_signup"
                  size="lg"
                  variant="default"
                  className="rounded-full px-7 shadow-sm"
                >
                  Get started free
                  <ArrowRight className="size-4" aria-hidden />
                </MarketingCtaLink>
                <Link
                  href="/how-it-works"
                  className={cn(
                    buttonVariants({ variant: "outline", size: "lg" }),
                    "rounded-full px-7",
                  )}
                >
                  See how it works
                </Link>
              </div>

              {/* Trust stats */}
              <div
                className={cn(
                  "mt-8 flex flex-wrap gap-x-5 gap-y-2 font-mono text-[0.62rem] text-muted-foreground/70",
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
                    <span className="size-1 rounded-full bg-primary/40" aria-hidden />
                    {item}
                  </span>
                ))}
              </div>
            </div>

            {/* ── Right: real product demo ──────────────────────────── */}
            <div
              className={cn(
                "relative hidden lg:block",
                motionHeroStagger(5),
              )}
            >
              {/* Glow behind the card */}
              <div
                aria-hidden
                className="pointer-events-none absolute -inset-8"
                style={{
                  background:
                    "radial-gradient(ellipse 80% 70% at 50% 50%, oklch(0.42 0.14 250 / 0.07) 0%, transparent 70%)",
                }}
              />
              <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-200/80 ring-1 ring-slate-100">
                <div className="flex items-center gap-1.5 border-b border-slate-100 bg-slate-50 px-4 py-3">
                  <span className="size-2.5 rounded-full bg-red-400/70" aria-hidden />
                  <span className="size-2.5 rounded-full bg-amber-400/70" aria-hidden />
                  <span className="size-2.5 rounded-full bg-emerald-400/70" aria-hidden />
                  <span className="ml-3 font-mono text-[10px] text-muted-foreground/60">
                    jober · run console · live
                  </span>
                </div>
                <div className="p-2">
                  <HeroRunPreview />
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Mobile product preview (below copy) */}
        <div className={cn("mt-10 px-6 pb-2 lg:hidden", motionHeroStagger(5))}>
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg shadow-slate-100">
            <div className="flex items-center gap-1.5 border-b border-slate-100 bg-slate-50 px-4 py-3">
              <span className="size-2 rounded-full bg-red-400/70" aria-hidden />
              <span className="size-2 rounded-full bg-amber-400/70" aria-hidden />
              <span className="size-2 rounded-full bg-emerald-400/70" aria-hidden />
            </div>
            <div className="p-2">
              <HeroRunPreview />
            </div>
          </div>
        </div>
      </section>

      {/* ── Subtle separator band ─────────────────────────────────── */}
      <div
        aria-hidden
        className="h-16 bg-gradient-to-b from-slate-50/0 to-slate-50"
      />
    </>
  );
}
