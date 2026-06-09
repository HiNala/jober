import type { Metadata } from "next";

import { LandingPage } from "@/components/marketing/landing-page";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { getSiteUrl } from "@/lib/site";

const title = "Jober — Assisted job applications you approve";
const description =
  "High-quality job applications with human review before submit. Pick roles, watch the run console, and approve every submission.";

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
  return (
    <MarketingShell>
      <LandingPage />
    </MarketingShell>
  );
}
