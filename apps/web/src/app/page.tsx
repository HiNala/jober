import type { Metadata } from "next";

import { JsonLd } from "@/components/marketing/json-ld";
import { LandingPage } from "@/components/marketing/landing-page";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { POSITIONING_ONE_LINER } from "@/lib/marketing/content";
import { getSiteUrl } from "@/lib/site";

const title = "Jober — Assisted job applications you approve";
const description = POSITIONING_ONE_LINER;

export const metadata: Metadata = {
  title: { absolute: title },
  description,
  alternates: { canonical: "/" },
  openGraph: {
    title,
    description,
    url: getSiteUrl(),
    siteName: "Jober",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
  },
};

export default function HomePage() {
  const siteUrl = getSiteUrl();
  return (
    <MarketingShell signupFeature="landing_header_signup">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          name: "Jober",
          applicationCategory: "BusinessApplication",
          operatingSystem: "Web",
          description: POSITIONING_ONE_LINER,
          url: siteUrl,
          offers: {
            "@type": "Offer",
            price: "0",
            priceCurrency: "USD",
          },
        }}
      />
      <LandingPage />
    </MarketingShell>
  );
}
