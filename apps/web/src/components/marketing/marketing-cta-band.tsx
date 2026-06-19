import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { motionFadeIn } from "@/lib/design/motion";
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
      className={cn(
        "bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-20",
        motionFadeIn,
      )}
    >
      <div className="mx-auto max-w-3xl text-center">
        <h2
          id="marketing-cta-band-heading"
          className="text-2xl font-semibold text-white md:text-3xl"
        >
          {title}
        </h2>
        <p className="mx-auto mt-3 max-w-lg text-blue-100">{lead}</p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <MarketingCtaLink
            href="/signup"
            feature={signupFeature}
            size="lg"
            className="rounded-full bg-white px-8 text-blue-700 shadow-md hover:bg-blue-50"
          >
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
          {secondaryFeature ? (
            <MarketingCtaLink
              href={secondaryHref}
              feature={secondaryFeature}
              variant="outline"
              size="lg"
              className="rounded-full border-white/40 px-8 text-white hover:bg-white/10 hover:text-white"
            >
              {secondaryLabel}
            </MarketingCtaLink>
          ) : null}
        </div>
      </div>
    </section>
  );
}
