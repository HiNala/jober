import type { Metadata } from "next";

import { FaqList } from "@/components/marketing/faq-list";
import { HowItWorks } from "@/components/marketing/how-it-works";
import { MarketingCtaBand } from "@/components/marketing/marketing-cta-band";
import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { FAQ_ITEMS } from "@/lib/marketing/content";
import { marketingMetadata } from "@/lib/marketing/metadata";

export const metadata: Metadata = marketingMetadata({
  title: "How it works",
  description:
    "Pick roles, prepare materials, watch the run console, and approve every submit. CAPTCHAs and logins always hand off to you.",
  path: "/how-it-works",
});

const workflowFaq = FAQ_ITEMS.slice(0, 4);

export default function HowItWorksPage() {
  return (
    <MarketingShell signupFeature="how_it_works_header_signup">
      <div className="px-6 pt-16">
        <MarketingPageHeader
          eyebrow="How it works"
          title="The application loop, end to end"
          lead="Four steps — each with a human checkpoint before anything irreversible happens."
        />
      </div>
      <HowItWorks showIntro={false} />
      <section className="mx-auto max-w-3xl px-6 pb-16" aria-labelledby="workflow-faq-heading">
        <h2 id="workflow-faq-heading" className="text-xl font-semibold">
          Common questions
        </h2>
        <div className="mt-6">
          <FaqList items={workflowFaq} />
        </div>
      </section>
      <MarketingCtaBand
        signupFeature="how_it_works_cta_signup"
        secondaryHref="/features"
        secondaryFeature="how_it_works_cta_features"
        secondaryLabel="Explore features"
      />
    </MarketingShell>
  );
}
