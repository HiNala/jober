import type { Metadata } from "next";

import {
  LegalStubPage,
  legalStubMetadata,
} from "@/components/marketing/legal-stub-page";

export const metadata: Metadata = legalStubMetadata(
  "Privacy",
  "How Jober handles your data. Full policy ships in Mission 30.",
);

export default function PrivacyPage() {
  return (
    <LegalStubPage
      title="Privacy policy"
      lead="Jober is built for assisted applications with you in control. This stub confirms the page route; the complete policy will cover vault data, run artifacts, analytics consent, and data export/deletion."
      body="Contact hello@jober.app for privacy questions while the full policy is being finalized."
    />
  );
}
