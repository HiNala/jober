import { HowItWorks } from "@/components/marketing/how-it-works";
import { MarketingHero } from "@/components/marketing/hero";
import { PricingTeaser } from "@/components/marketing/pricing-teaser";
import { SocialProof } from "@/components/marketing/social-proof";
import { ValueSections } from "@/components/marketing/value-sections";

export function LandingPage() {
  return (
    <>
      <MarketingHero />
      <HowItWorks />
      <ValueSections />
      <SocialProof />
      <PricingTeaser />
    </>
  );
}
