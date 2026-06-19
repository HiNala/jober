import type { Metadata } from "next";

import { JsonLd } from "@/components/marketing/json-ld";
import { LandingPage } from "@/components/marketing/landing-page";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { POSITIONING_ONE_LINER } from "@/lib/marketing/content";
import { getSiteUrl } from "@/lib/site";

const title = "Jober — Assisted job applications you approve";
const description =
  "AI-assisted job applications with human review before every submit. Build your queue, watch the fills, approve and send.";

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
    images: [
      {
        url: "/images/hero-light.png",
        width: 1536,
        height: 1024,
        alt: "Jober — AI-assisted job applications",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
    images: ["/images/hero-light.png"],
  },
};

export default function HomePage() {
  const siteUrl = getSiteUrl();
  return (
    <MarketingShell signupFeature="landing_header_signup">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@graph": [
            {
              "@type": "Organization",
              "@id": `${siteUrl}/#organization`,
              name: "Jober",
              url: siteUrl,
            },
            {
              "@type": "SoftwareApplication",
              "@id": `${siteUrl}/#software`,
              name: "Jober",
              url: siteUrl,
              applicationCategory: "BusinessApplication",
              operatingSystem: "Web",
              description: POSITIONING_ONE_LINER,
              offers: {
                "@type": "Offer",
                price: "0",
                priceCurrency: "USD",
                description: "Free tier available — no credit card required.",
              },
              publisher: { "@id": `${siteUrl}/#organization` },
            },
            {
              "@type": "WebSite",
              "@id": `${siteUrl}/#website`,
              url: siteUrl,
              name: "Jober",
              publisher: { "@id": `${siteUrl}/#organization` },
            },
          ],
        }}
      />
      <LandingPage />
    </MarketingShell>
  );
}
