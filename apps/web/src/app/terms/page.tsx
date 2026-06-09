import type { Metadata } from "next";

import {
  LegalStubPage,
  legalStubMetadata,
} from "@/components/marketing/legal-stub-page";

export const metadata: Metadata = legalStubMetadata(
  "Terms",
  "Terms of service for Jober. Full terms ship in Mission 30.",
);

export default function TermsPage() {
  return (
    <LegalStubPage
      title="Terms of service"
      lead="By using Jober you remain responsible for reviewing and approving every application submitted through your account."
      body="The complete terms of service — including acceptable use, billing, and liability — will be published in Mission 30. Contact hello@jober.app with questions."
    />
  );
}
