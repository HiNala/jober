import { DifferentiatorBento } from "@/components/marketing/differentiator-bento";
import { FounderProof } from "@/components/marketing/founder-proof";
import { HomeFaqTeaser } from "@/components/marketing/home-faq-teaser";
import { HowItWorks } from "@/components/marketing/how-it-works";
import { MarketingCtaBand } from "@/components/marketing/marketing-cta-band";
import { MarketingHero } from "@/components/marketing/hero";
import { PricingTeaser } from "@/components/marketing/pricing-teaser";
import { TrustStrip } from "@/components/marketing/trust-strip";
import { LANDING_TRUST_ITEMS } from "@/lib/marketing/content";

export function LandingPage() {
  return (
    <>
      <MarketingHero />
      <TrustStrip items={LANDING_TRUST_ITEMS} className="border-y border-border/50 bg-muted/10 px-6 py-5" />
      <DifferentiatorBento />
      <HowItWorks variant="stepper" />
      <FounderProof />
      <PricingTeaser />
      <HomeFaqTeaser />
      <MarketingCtaBand signupFeature="landing_footer_signup" secondaryFeature="landing_footer_pricing" />
    </>
  );
}
