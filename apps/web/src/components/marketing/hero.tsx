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
          "mx-auto aspect-[4/3] w-full max-w-3xl rounded-2xl border border-slate-200 bg-slate-100",
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
      {/* ── Light hero ───────────────────────────────────────────────── */}
      <section
        aria-labelledby="hero-heading"
        className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-slate-50"
      >
        {/* Dot field — uses --primary CSS var (blue) */}
        <ParticleField className="z-0" density="medium" />

        {/* Soft blue radial glow behind copy */}
        <div
          aria-hidden
          className="pointer-events-none absolute left-0 top-0 h-[70%] w-[55%]"
          style={{
            background:
              "radial-gradient(ellipse 60% 55% at 25% 40%, oklch(0.42 0.14 250 / 0.07) 0%, transparent 70%)",
          }}
        />

        {/* Hero illustration — right side, fading into bg */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 hidden w-[50%] lg:block"
        >
          <Image
            src="/images/hero-light.png"
            alt=""
            fill
            priority
            className="object-cover object-left"
            sizes="50vw"
          />
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(to right, white 0%, transparent 35%, transparent 100%)",
            }}
          />
          <div
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(to top, oklch(0.97 0.006 245) 0%, transparent 25%)",
            }}
          />
        </div>

        {/* Copy */}
        <div className="relative z-10 mx-auto max-w-7xl px-6 pb-28 pt-20 lg:pb-36 lg:pt-28">
          <div className="max-w-2xl">
            {/* Eyebrow badge */}
            <p
              className={cn(
                "inline-flex items-center gap-2 font-mono text-[0.65rem] uppercase tracking-[0.22em] text-primary",
                motionHeroStagger(0),
              )}
            >
              <span
                className="inline-block size-1.5 rounded-full bg-primary"
                aria-hidden
              />
              Human-in-the-loop job applications
            </p>

            {/* Display headline */}
            <h1
              id="hero-heading"
              className={cn(
                "mt-6 font-black leading-[1.05] tracking-[-0.03em] break-words text-foreground",
                motionHeroStagger(1),
              )}
              style={{ fontSize: "clamp(2rem, 8vw, 5.5rem)" }}
            >
              <span className="block">Apply to every job</span>
              <span className="block text-primary">at your quality bar.</span>
            </h1>

            {/* Subhead */}
            <p
              className={cn(
                "mt-6 max-w-lg text-lg leading-relaxed text-muted-foreground",
                motionHeroStagger(2),
              )}
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
                variant="default"
                className="brand-cta-shimmer rounded-full px-8 shadow-md"
              >
                Get started free
                <ArrowRight className="size-4" aria-hidden />
              </MarketingCtaLink>
              <Link
                href="/how-it-works"
                className={cn(
                  buttonVariants({ variant: "outline", size: "lg" }),
                  "rounded-full px-8",
                )}
              >
                See how it works
              </Link>
            </div>

            {/* Trust micro-stats */}
            <div
              className={cn(
                "mt-10 flex flex-wrap gap-x-5 gap-y-2.5 font-mono text-[0.65rem] sm:text-xs text-muted-foreground",
                motionHeroStagger(4),
              )}
            >
              {["Review before submit", "No CAPTCHA bypass", "No hidden auto-submit", "BYOK supported"].map(
                (item) => (
                  <span key={item} className="flex items-center gap-1.5">
                    <span className="size-1 rounded-full bg-primary/50" aria-hidden />
                    {item}
                  </span>
                ),
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ── Product preview — light slate bg ─────────────────── */}
      <section
        aria-label="Product preview"
        className="relative overflow-hidden border-t border-slate-100 bg-slate-50"
      >
        <div className="mx-auto max-w-5xl px-6 pb-20 pt-14">
          <p className="mb-8 text-center font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">
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
