import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function PricingTeaser() {
  return (
    <section aria-labelledby="pricing-teaser-heading" className="px-6 py-20">
      <div className="mx-auto max-w-3xl">
        <div
          className={cn(
            surface.marketing,
            "rounded-xl p-8 text-center md:p-10",
            motionFadeIn,
          )}
        >
          <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
            Pricing
          </p>
          <h2
            id="pricing-teaser-heading"
            className="mt-3 text-3xl font-semibold tracking-[-0.02em] md:text-4xl"
          >
            Start free, scale when your pipeline does
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-muted-foreground">
            Free includes 20 runs/month, batches up to 5, and a $5 managed LLM budget. Pro raises
            those limits — see the full comparison on pricing.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <MarketingCtaLink href="/signup" feature="landing_pricing_signup" size="lg">
              Create free account
              <ArrowRight className="size-4" aria-hidden />
            </MarketingCtaLink>
            <MarketingCtaLink
              href="/pricing"
              feature="landing_pricing_view"
              variant="outline"
              size="lg"
            >
              View pricing
            </MarketingCtaLink>
          </div>
        </div>
      </div>
    </section>
  );
}
