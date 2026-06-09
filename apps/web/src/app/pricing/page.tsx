import type { Metadata } from "next";
import { ArrowRight, Check } from "lucide-react";

import { FaqList } from "@/components/marketing/faq-list";
import { JsonLd } from "@/components/marketing/json-ld";
import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { MarketingCtaBand } from "@/components/marketing/marketing-cta-band";
import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { motionFadeIn } from "@/lib/design/motion";
import { PRICING_FAQ } from "@/lib/marketing/content";
import { marketingMetadata } from "@/lib/marketing/metadata";
import { MARKETING_PLANS } from "@/lib/marketing/plans";
import { getSiteUrl } from "@/lib/site";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export const metadata: Metadata = marketingMetadata({
  title: "Pricing",
  description:
    "Free and Pro plans with real run, batch, and LLM limits. BYOK optional. Review-before-submit on every tier.",
  path: "/pricing",
});

export default function PricingPage() {
  const free = MARKETING_PLANS[0];
  const pro = MARKETING_PLANS[1];

  return (
    <MarketingShell signupFeature="pricing_header_signup">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "Product",
          name: "Jober",
          url: `${getSiteUrl()}/pricing`,
          description:
            "Free and Pro plans with run, batch, and LLM limits. BYOK optional. Review-before-submit on every tier.",
          offers: MARKETING_PLANS.map((plan) => ({
            "@type": "Offer",
            name: plan.name,
            price: plan.id === "free" ? "0" : undefined,
            priceCurrency: "USD",
            description: plan.description,
          })),
        }}
      />
      <div className={cn("px-6 py-16", motionFadeIn)}>
        <MarketingPageHeader
          eyebrow="Pricing"
          title="Plans that match how you search"
          lead="Limits mirror what Settings shows today. Pro checkout via Stripe is coming soon."
        />

        <ul className="mx-auto mt-12 grid max-w-5xl gap-4 md:grid-cols-2">
          {MARKETING_PLANS.map((plan) => (
            <li
              key={plan.id}
              className={cn(
                surface.card,
                "flex flex-col rounded-xl p-6",
                plan.id === "pro" && "border-primary/30",
              )}
            >
              <h2 className="text-lg font-semibold">{plan.name}</h2>
              <p className="mt-2 text-3xl font-semibold tabular-nums">{plan.priceLabel}</p>
              {plan.priceNote ? (
                <p className="text-xs text-muted-foreground">{plan.priceNote}</p>
              ) : null}
              <p className="mt-3 text-sm text-muted-foreground">{plan.description}</p>
              <dl className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between gap-4 border-b border-border/40 pb-2">
                  <dt className="text-muted-foreground">Monthly runs</dt>
                  <dd className="font-medium tabular-nums">{plan.entitlements.maxMonthlyRuns}</dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/40 pb-2">
                  <dt className="text-muted-foreground">Batch size</dt>
                  <dd className="font-medium tabular-nums">{plan.entitlements.maxBatchItems}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted-foreground">Managed LLM budget</dt>
                  <dd className="font-medium tabular-nums">
                    ${plan.entitlements.maxLlmBudgetUsd}/mo
                  </dd>
                </div>
              </dl>
              <ul className="mt-4 flex-1 space-y-2 text-sm text-muted-foreground">
                {plan.highlights.map((item) => (
                  <li key={item} className="flex gap-2">
                    <Check className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                    {item}
                  </li>
                ))}
              </ul>
              {plan.id === "free" ? (
                <MarketingCtaLink
                  href="/signup"
                  feature="pricing_free_signup"
                  size="lg"
                  className="mt-6 w-full"
                >
                  Start free
                  <ArrowRight className="size-4" aria-hidden />
                </MarketingCtaLink>
              ) : (
                <p className="mt-6 text-center text-xs text-muted-foreground">
                  Stripe checkout opens when Pro billing launches.
                </p>
              )}
            </li>
          ))}
        </ul>

        <section
          className="mx-auto mt-12 max-w-3xl rounded-lg border border-border/60 bg-muted/20 p-6 text-sm text-muted-foreground"
          aria-labelledby="llm-costs-heading"
        >
          <h2 id="llm-costs-heading" className="text-base font-semibold text-foreground">
            Managed LLM vs. bring your own key (BYOK)
          </h2>
          <p className="mt-2">
            Each plan includes a monthly managed budget for cover letters and form assistance
            (${free.entitlements.maxLlmBudgetUsd} Free / ${pro.entitlements.maxLlmBudgetUsd}{" "}
            Pro). Usage appears in Settings → usage.
          </p>
          <p className="mt-2">
            Optionally add your own OpenAI or Anthropic key in Settings. When BYOK is active, your
            provider bills you directly — spend does not count against the managed pool, but keys
            never leave our encrypted storage or appear in the browser.
          </p>
        </section>

        <section className="mx-auto mt-16 max-w-3xl" aria-labelledby="pricing-faq-heading">
          <h2 id="pricing-faq-heading" className="text-xl font-semibold">
            Billing FAQ
          </h2>
          <div className="mt-6">
            <FaqList items={PRICING_FAQ} />
          </div>
        </section>
      </div>
      <MarketingCtaBand signupFeature="pricing_cta_signup" secondaryFeature="pricing_cta_faq" secondaryHref="/faq" secondaryLabel="Read FAQ" />
    </MarketingShell>
  );
}
