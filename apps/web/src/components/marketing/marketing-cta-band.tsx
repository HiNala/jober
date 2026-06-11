import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function MarketingCtaBand({
  title = "Ready to apply with clarity?",
  lead = "Create a free account — review every submit before it leaves your workspace.",
  signupFeature,
  secondaryHref = "/pricing",
  secondaryFeature,
  secondaryLabel = "View pricing",
}: {
  title?: string;
  lead?: string;
  signupFeature: string;
  secondaryHref?: string;
  secondaryFeature?: string;
  secondaryLabel?: string;
}) {
  return (
    <section
      aria-labelledby="marketing-cta-band-heading"
      className={cn("px-6 py-16", motionFadeIn)}
    >
      <div className={cn(surface.marketing, "mx-auto max-w-3xl rounded-xl p-8 text-center md:p-10")}>
        <h2 id="marketing-cta-band-heading" className="text-2xl font-semibold md:text-3xl">
          {title}
        </h2>
        <p className="mx-auto mt-3 max-w-lg text-muted-foreground">{lead}</p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <MarketingCtaLink href="/signup" feature={signupFeature} size="lg">
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
          {secondaryFeature ? (
            <MarketingCtaLink
              href={secondaryHref}
              feature={secondaryFeature}
              variant="outline"
              size="lg"
            >
              {secondaryLabel}
            </MarketingCtaLink>
          ) : null}
        </div>
      </div>
    </section>
  );
}
