import type { Metadata } from "next";
import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { legalStubMetadata } from "@/components/marketing/legal-stub-page";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export const metadata: Metadata = legalStubMetadata(
  "Pricing",
  "Simple tiers for solo searchers and teams. Full pricing page ships in Mission 30.",
);

const tiers = [
  {
    name: "Free",
    price: "$0",
    detail: "Core queue, vault, and review-before-submit for individual job seekers.",
  },
  {
    name: "Pro",
    price: "Coming soon",
    detail: "Higher run limits, batch scheduling, and priority support.",
  },
] as const;

export default function PricingPage() {
  return (
    <MarketingShell>
      <div className={cn("mx-auto max-w-4xl px-6 py-16", motionFadeIn)}>
        <div className="text-center">
          <h1 className="text-3xl font-semibold tracking-tight">Pricing</h1>
          <p className="mt-3 text-muted-foreground">
            Placeholder tiers — Mission 30 will publish final limits and checkout.
          </p>
        </div>

        <ul className="mt-10 grid gap-4 md:grid-cols-2">
          {tiers.map(({ name, price, detail }) => (
            <li key={name} className={cn(surface.card, "rounded-xl p-6")}>
              <h2 className="text-lg font-semibold">{name}</h2>
              <p className="mt-2 text-2xl font-semibold tabular-nums">{price}</p>
              <p className="mt-3 text-sm text-muted-foreground">{detail}</p>
            </li>
          ))}
        </ul>

        <div className="mt-10 flex justify-center">
          <MarketingCtaLink href="/signup" feature="pricing_stub_signup" size="lg">
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
        </div>
      </div>
    </MarketingShell>
  );
}
