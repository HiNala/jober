import { ArrowRight, CheckCircle2, Shield, UserCheck } from "lucide-react";

import { AnimatedBackground } from "@/components/marketing/animated-background";
import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { ProductVisual } from "@/components/marketing/product-visual";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const pillars = [
  {
    icon: UserCheck,
    title: "You choose every job",
    body: "Jober assists applications you select — never spray-and-pray volume.",
  },
  {
    icon: Shield,
    title: "Review before submit",
    body: "Forms fill with your consent; you approve the final submit.",
  },
  {
    icon: CheckCircle2,
    title: "Honest handoffs",
    body: "CAPTCHA, login, and sensitive fields pause for you — no bypass.",
  },
] as const;

export function MarketingHero() {
  return (
    <section className="relative overflow-hidden px-6 py-16 md:py-24" aria-labelledby="hero-heading">
      <AnimatedBackground />
      <div className="relative mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
        <div className={cn("text-center lg:text-left", motionFadeIn)}>
          <p className="text-sm font-medium uppercase tracking-widest text-accent">
            You-in-the-loop applications
          </p>
          <h1
            id="hero-heading"
            className="mt-4 text-4xl font-semibold tracking-tight md:text-5xl md:leading-tight"
          >
            Tailored job applications with clarity at every step
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground lg:mx-0">
            Jober prepares materials, fills forms with your consent, and pauses for your review
            before anything submits. Quality and tracking — not automation in hiding.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3 lg:justify-start">
            <MarketingCtaLink href="/signup" feature="landing_hero_signup" size="lg">
              Start free
              <ArrowRight className="size-4" aria-hidden />
            </MarketingCtaLink>
            <MarketingCtaLink
              href="/how-it-works"
              feature="landing_hero_how_it_works"
              variant="outline"
              size="lg"
            >
              See how it works
            </MarketingCtaLink>
          </div>
        </div>

        <ProductVisual />
      </div>

      <ul className="relative mx-auto mt-16 grid max-w-6xl gap-4 md:grid-cols-3">
        {pillars.map(({ icon: Icon, title, body }) => (
          <li
            key={title}
            className="rounded-lg border border-border/60 bg-card/60 p-4 text-left backdrop-blur-sm"
          >
            <Icon className="mb-2 size-5 text-accent" aria-hidden />
            <h2 className="text-sm font-semibold">{title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">{body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
