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
            surface.card,
            "rounded-xl p-8 text-center md:p-10",
            motionFadeIn,
          )}
        >
          <p className="text-sm font-medium uppercase tracking-widest text-accent">Pricing</p>
          <h2 id="pricing-teaser-heading" className="mt-3 text-2xl font-semibold md:text-3xl">
            Start free, scale when your pipeline does
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-muted-foreground">
            A generous free tier for solo searchers. Pro adds batch runs, priority support, and
            higher limits — full comparison on the pricing page.
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
