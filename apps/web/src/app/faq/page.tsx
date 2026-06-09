import type { Metadata } from "next";

import { FaqList } from "@/components/marketing/faq-list";
import { JsonLd } from "@/components/marketing/json-ld";
import { MarketingCtaBand } from "@/components/marketing/marketing-cta-band";
import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { FAQ_ITEMS } from "@/lib/marketing/content";
import { marketingMetadata } from "@/lib/marketing/metadata";
import { getSiteUrl } from "@/lib/site";

export const metadata: Metadata = marketingMetadata({
  title: "FAQ",
  description:
    "Does Jober auto-submit? What about CAPTCHAs? How is my data handled? Straight answers about assisted applications.",
  path: "/faq",
});

export default function FaqPage() {
  return (
    <MarketingShell signupFeature="faq_header_signup">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: FAQ_ITEMS.map(({ question, answer }) => ({
            "@type": "Question",
            name: question,
            acceptedAnswer: { "@type": "Answer", text: answer },
          })),
          url: `${getSiteUrl()}/faq`,
        }}
      />
      <div className="px-6 py-16">
        <MarketingPageHeader
          eyebrow="FAQ"
          title="Straight answers"
          lead="No evasion, no fine-print surprises. If something needs a human, we say so."
        />
        <div className="mx-auto mt-10 max-w-3xl">
          <FaqList items={FAQ_ITEMS} />
        </div>
      </div>
      <MarketingCtaBand signupFeature="faq_cta_signup" secondaryFeature="faq_cta_pricing" />
    </MarketingShell>
  );
}
