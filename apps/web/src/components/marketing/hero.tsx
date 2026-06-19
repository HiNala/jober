import dynamic from "next/dynamic";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { ParticleField } from "@/components/marketing/particle-field";
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
          "mx-auto aspect-[4/3] w-full max-w-3xl rounded-2xl border border-white/10",
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
      {/* ── Dark cinematic hero ───────────────────────────────────────────── */}
      <section
        aria-labelledby="hero-heading"
        style={{ backgroundColor: "#0a0908" }}
        className="relative overflow-hidden"
      >
        {/* Dot field */}
        <ParticleField className="z-0" density="medium" />

        {/* Radial glow behind copy */}
        <div
          aria-hidden
          className="pointer-events-none absolute left-0 top-0 h-[70%] w-[55%]"
          style={{
            background:
              "radial-gradient(ellipse 60% 55% at 25% 40%, oklch(0.42 0.14 250 / 0.12) 0%, transparent 70%)",
          }}
        />

        {/* Hero image — right side, fading left into dark */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 hidden w-[52%] lg:block"
        >
          <Image
            src="/images/hero-dark.png"
            alt=""
            fill
            priority
            className="object-cover object-left"
            sizes="52vw"
          />
          {/* Fade gradient so image bleeds into dark bg */}
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(to right, #0a0908 0%, #0a0908 8%, transparent 45%, transparent 100%)",
            }}
          />
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(to top, #0a0908 0%, transparent 30%)",
            }}
          />
        </div>

        {/* Copy */}
        <div className="relative z-10 mx-auto max-w-7xl px-6 pb-24 pt-20 lg:pb-32 lg:pt-28">
          <div className="max-w-2xl">
            {/* Eyebrow badge */}
            <p
              className={cn(
                "inline-flex items-center gap-2 font-mono text-[0.65rem] uppercase tracking-[0.22em]",
                motionHeroStagger(0),
              )}
              style={{ color: "var(--marketing-gold)" }}
            >
              <span
                className="inline-block size-1.5 rounded-full"
                style={{ backgroundColor: "var(--marketing-gold)" }}
                aria-hidden
              />
              Human-in-the-loop job applications
            </p>

            {/* Display headline — split weight */}
            <h1
              id="hero-heading"
              className={cn("mt-6 font-bold leading-[1.0] tracking-[-0.03em]", motionHeroStagger(1))}
              style={{ fontSize: "clamp(2.8rem, 7vw, 5.5rem)" }}
            >
              <span className="block text-white">Apply to every job</span>
              <span className="block" style={{ color: "oklch(1 0 0 / 0.22)" }}>
                at your quality bar.
              </span>
            </h1>

            {/* Subhead */}
            <p
              className={cn("mt-6 max-w-lg text-lg leading-relaxed", motionHeroStagger(2))}
              style={{ color: "var(--marketing-muted)" }}
            >
              AI fills the form. You read the diff and hit submit. Your
              applications, your standard, your control.
            </p>

            {/* CTAs */}
            <div
              className={cn(
                "mt-9 flex flex-wrap items-center gap-4",
                motionHeroStagger(3),
              )}
            >
              <MarketingCtaLink
                href="/signup"
                feature="landing_hero_signup"
                size="lg"
                variant="ghost"
                className="brand-cta-shimmer rounded-full px-8 shadow-lg bg-[oklch(0.78_0.14_68)] text-[#0a0908] hover:bg-[oklch(0.72_0.14_68)] hover:text-[#0a0908]"
              >
                Get started free
                <ArrowRight className="size-4" aria-hidden />
              </MarketingCtaLink>
              <Link
                href="/how-it-works"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "rounded-full border-white/20 bg-transparent px-8 text-white hover:bg-white/10 hover:text-white",
                )}
              >
                See how it works
              </Link>
            </div>

            {/* Trust micro-stats */}
            <div
              className={cn(
                "mt-10 flex flex-wrap gap-x-6 gap-y-2 font-mono text-xs",
                motionHeroStagger(4),
              )}
              style={{ color: "oklch(1 0 0 / 0.30)" }}
            >
              {["Review before submit", "No CAPTCHA bypass", "No hidden auto-submit", "BYOK supported"].map(
                (item) => (
                  <span key={item} className="flex items-center gap-1.5">
                    <span className="size-1 rounded-full bg-current opacity-60" aria-hidden />
                    {item}
                  </span>
                ),
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── Product preview — slightly elevated from dark ─────────────────── */}
      <section
        aria-label="Product preview"
        style={{ backgroundColor: "#0f0e0d" }}
        className="relative overflow-hidden border-t border-white/[0.05]"
      >
        <div className="mx-auto max-w-5xl px-6 pb-20 pt-14">
          <p
            className="mb-8 text-center font-mono text-xs uppercase tracking-[0.2em]"
            style={{ color: "oklch(1 0 0 / 0.28)" }}
          >
            Live run console
          </p>
          <div className={cn("w-full", motionHeroStagger(5))}>
            <HeroRunPreview />
          </div>
        </div>
      </section>
    </>
  );
}
