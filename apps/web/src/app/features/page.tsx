import type { Metadata } from "next";

import { FeaturesBento } from "@/components/marketing/features-bento";
import { JsonLd } from "@/components/marketing/json-ld";
import { MarketingCtaBand } from "@/components/marketing/marketing-cta-band";
import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { marketingMetadata } from "@/lib/marketing/metadata";
import { getSiteUrl } from "@/lib/site";

export const metadata: Metadata = marketingMetadata({
  title: "Features",
  description:
    "Discovery, tailored letters, live-watch runs, workspace analytics, and a safety posture built on review-before-submit.",
  path: "/features",
});

export default function FeaturesPage() {
  return (
    <MarketingShell signupFeature="features_header_signup">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "WebPage",
          name: "Jober Features",
          url: `${getSiteUrl()}/features`,
          description:
            "Discovery, tailored letters, live-watch runs, workspace analytics, and review-before-submit safety.",
        }}
      />
      <div className="px-6 py-16 md:py-20">
        <MarketingPageHeader
          eyebrow="Features"
          title="Trust features, not hidden automation"
          lead="Every capability is designed so you can see what happened and approve what gets sent."
        />
        <FeaturesBento />
      </div>
      <MarketingCtaBand
        signupFeature="features_cta_signup"
        secondaryFeature="features_cta_pricing"
      />
    </MarketingShell>
  );
}
