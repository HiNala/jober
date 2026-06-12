import dynamic from "next/dynamic";
import { ArrowRight, Play } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { AnimatedBackground } from "@/components/marketing/animated-background";
import { motionHeroStagger } from "@/lib/design/motion";
import { POSITIONING_ONE_LINER, POSITIONING_SUBHEAD } from "@/lib/marketing/content";
import { cn } from "@/lib/utils";

const HeroRunPreview = dynamic(
  () =>
    import("@/components/marketing/hero-run-preview").then((mod) => ({
      default: mod.HeroRunPreview,
    })),
  {
    loading: () => (
      <div
        className="mx-auto aspect-[4/3] w-full max-w-3xl animate-pulse rounded-xl border border-border/60 bg-muted/25"
        aria-hidden
      />
    ),
  },
);

export function MarketingHero() {
  return (
    <section
      className="relative overflow-hidden px-6 pb-12 pt-16 md:pb-20 md:pt-20"
      aria-labelledby="hero-heading"
    >
      <AnimatedBackground />
      <div className="relative mx-auto flex max-w-4xl flex-col items-center text-center">
        <p
          className={cn(
            "font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent",
            motionHeroStagger(0),
          )}
        >
          You-in-the-loop applications
        </p>
        <h1
          id="hero-heading"
          className={cn(
            "mt-5 max-w-3xl text-4xl font-semibold tracking-[-0.02em] md:text-6xl md:leading-[1.08]",
            motionHeroStagger(1),
          )}
        >
          {POSITIONING_ONE_LINER}
        </h1>
        <p
          className={cn(
            "mt-5 max-w-2xl text-lg text-muted-foreground md:text-xl",
            motionHeroStagger(2),
          )}
        >
          {POSITIONING_SUBHEAD}
        </p>
        <div
          className={cn(
            "mt-8 flex flex-wrap items-center justify-center gap-3",
            motionHeroStagger(3),
          )}
        >
          <MarketingCtaLink href="/signup" feature="landing_hero_signup" size="lg">
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
          <MarketingCtaLink
            href="#differentiator"
            feature="landing_hero_watch_run"
            variant="outline"
            size="lg"
          >
            <Play className="size-4" aria-hidden />
            Watch a run
          </MarketingCtaLink>
        </div>
        <div className={cn("mt-12 w-full", motionHeroStagger(4))}>
          <HeroRunPreview />
        </div>
      </div>
    </section>
  );
}
