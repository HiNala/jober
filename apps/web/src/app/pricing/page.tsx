import type { Metadata } from "next";
import { Suspense } from "react";

import { UnlockModal } from "@/components/billing/unlock-modal";
import { FaqList } from "@/components/marketing/faq-list";
import { JsonLd } from "@/components/marketing/json-ld";
import { MarketingCtaBand } from "@/components/marketing/marketing-cta-band";
import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { PricingPlans } from "@/components/marketing/pricing-plans";
import { PRICING_FAQ } from "@/lib/marketing/content";
import { marketingMetadata } from "@/lib/marketing/metadata";
import { MARKETING_PLANS } from "@/lib/marketing/plans";
import { getSiteUrl } from "@/lib/site";

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
            price:
              plan.id === "free"
                ? "0"
                : plan.priceLabel.replace(/[^0-9.]/g, "") || undefined,
            priceCurrency: "USD",
            description: plan.description,
          })),
        }}
      />
      <div className="px-6 py-16 md:py-20">
        <MarketingPageHeader
          eyebrow="Pricing"
          title="Plans that match how you search"
          lead="Free is live with real run, batch, and LLM limits that match Settings. Upgrade to Pro via Stripe when billing is enabled — or join the waitlist for early access."
        />

        <Suspense fallback={null}>
          <UnlockModal />
        </Suspense>

        <PricingPlans />

        <section
          className="mx-auto mt-12 max-w-5xl rounded-xl border border-border/40 bg-muted/15 p-6 text-sm text-muted-foreground"
          aria-labelledby="llm-costs-heading"
        >
          <h2 id="llm-costs-heading" className="text-base font-semibold text-foreground">
            Managed LLM vs. bring your own key (BYOK)
          </h2>
          <p className="mt-2">
            Each plan includes a monthly managed budget for cover letters and form assistance (
            ${free.entitlements.maxLlmBudgetUsd} Free / ${pro.entitlements.maxLlmBudgetUsd} Pro).
            Usage appears in Settings → Plan &amp; billing.
          </p>
          <p className="mt-2">
            Optionally add your own OpenAI or Anthropic key in Settings. When BYOK is active, your
            provider bills you directly — spend does not count against the managed pool, but keys
            never leave our encrypted storage or appear in the browser.
          </p>
        </section>

        <section className="mx-auto mt-16 max-w-3xl" aria-labelledby="pricing-faq-heading">
          <h2 id="pricing-faq-heading" className="text-xl font-semibold tracking-[-0.02em]">
            Billing FAQ
          </h2>
          <div className="mt-6">
            <FaqList items={PRICING_FAQ} />
          </div>
        </section>
      </div>
      <MarketingCtaBand
        signupFeature="pricing_cta_signup"
        secondaryFeature="pricing_cta_faq"
        secondaryHref="/faq"
        secondaryLabel="Read FAQ"
      />
    </MarketingShell>
  );
}
