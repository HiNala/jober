import { ArrowRight, Check } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { PlanComparisonTable } from "@/components/marketing/plan-comparison-table";
import { ProWaitlistForm } from "@/components/marketing/pro-waitlist-form";
import { motionFadeIn } from "@/lib/design/motion";
import { MARKETING_PLANS } from "@/lib/marketing/plans";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function PricingPlans() {
  const free = MARKETING_PLANS[0];
  const pro = MARKETING_PLANS[1];

  return (
    <div className={motionFadeIn}>
      <ul className="mx-auto mt-12 grid max-w-5xl gap-4 md:grid-cols-2">
        <li className={cn(surface.marketing, "pricing-border-beam relative flex flex-col rounded-xl p-6")}>
          <h2 className="text-lg font-semibold">{free.name}</h2>
          <p className="mt-4 flex items-baseline gap-1">
            <span className="text-5xl font-semibold tabular-nums tracking-[-0.03em]">$0</span>
            <span className="text-sm text-muted-foreground">/mo</span>
          </p>
          <p className="mt-3 text-sm text-muted-foreground">{free.description}</p>
          <ul className="mt-4 flex-1 space-y-2 text-sm text-muted-foreground">
            {free.highlights.map((item) => (
              <li key={item} className="flex items-start gap-2">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
                {item}
              </li>
            ))}
          </ul>
          <MarketingCtaLink
            href="/signup"
            feature="pricing_free_signup"
            size="lg"
            className="mt-6 w-full"
          >
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
        </li>

        <li className={cn(surface.marketing, "flex flex-col rounded-xl border-primary/40 bg-primary/[0.02] p-6 ring-1 ring-primary/20")}>
          <h2 className="text-lg font-semibold">{pro.name}</h2>
          <p className="mt-4 flex items-baseline gap-2">
            <span className="text-5xl font-semibold tabular-nums tracking-[-0.03em]">—</span>
            <span className="text-sm text-muted-foreground">paid monthly · launching soon</span>
          </p>
          <p className="mt-3 text-sm text-muted-foreground">{pro.description}</p>
          <ul className="mt-4 flex-1 space-y-2 text-sm text-muted-foreground">
            {pro.highlights.map((item) => (
              <li key={item} className="flex items-start gap-2">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden />
                {item}
              </li>
            ))}
          </ul>
          <div className="mt-6">
            <ProWaitlistForm />
          </div>
        </li>
      </ul>

      <div className="mx-auto mt-10 max-w-5xl">
        <h2 className="text-sm font-medium uppercase tracking-widest text-muted-foreground">
          Compare limits
        </h2>
        <PlanComparisonTable className="mt-4" />
      </div>
    </div>
  );
}
