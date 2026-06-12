import type { Metadata } from "next";
import Link from "next/link";

import { LegalDocument } from "@/components/marketing/legal-document";
import { marketingMetadata } from "@/lib/marketing/metadata";

export const metadata: Metadata = marketingMetadata({
  title: "Acceptable Use Policy",
  description:
    "Apply only to jobs you choose, respect site terms, and never evade CAPTCHAs or security controls.",
  path: "/acceptable-use",
});

export default function AcceptableUsePage() {
  return (
    <LegalDocument
      title="Acceptable Use Policy"
      summary="Apply only to jobs you explicitly queue. Do not bypass CAPTCHAs, bot detection, or site security. Keep application materials truthful. Abuse may lead to suspension."
    >
      <p>
        <strong>Last updated:</strong> June 2026 (draft). This policy supplements our{" "}
        <Link href="/terms" className="underline underline-offset-2">
          Terms of Service
        </Link>
        .
      </p>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Permitted use</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Assisted applications to job postings you explicitly added to your queue</li>
          <li>Accurate representations of your experience and qualifications</li>
          <li>Respecting rate limits, plan entitlements, and employer site terms</li>
          <li>Completing human checkpoints (CAPTCHA, login, 2FA) yourself when prompted</li>
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Prohibited use</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Spray-and-pray or bulk applications to roles you did not choose</li>
          <li>Bypassing CAPTCHAs, bot detection, paywalls, or authentication controls</li>
          <li>Submitting false credentials, impersonation, or misleading application materials</li>
          <li>Scraping or attacking employer sites beyond normal application flows</li>
          <li>Sharing accounts across unrelated tenants or circumventing plan limits</li>
          <li>Using Jober to harass employers or violate applicable law</li>
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Enforcement</h2>
        <p>
          We may suspend or terminate accounts that violate this policy. Severe abuse may be
          reported to relevant parties. Contact{" "}
          <Link href="mailto:abuse@jober.app" className="underline underline-offset-2">
            abuse@jober.app
          </Link>{" "}
          to report violations.
        </p>
      </section>
    </LegalDocument>
  );
}
