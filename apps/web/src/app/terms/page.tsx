import type { Metadata } from "next";
import Link from "next/link";

import { LegalDocument } from "@/components/marketing/legal-document";
import { marketingMetadata } from "@/lib/marketing/metadata";

export const metadata: Metadata = marketingMetadata({
  title: "Terms of Service",
  description:
    "Terms for using Jober — assisted job applications with human review before submit.",
  path: "/terms",
});

export default function TermsPage() {
  return (
    <LegalDocument title="Terms of Service">
      <p>
        <strong>Last updated:</strong> June 2026 (draft). By creating an account or using Jober,
        you agree to these terms.
      </p>

      <section>
        <h2 className="text-lg font-semibold text-foreground">The service</h2>
        <p>
          Jober helps you prepare and submit job applications you select. The product includes
          queue management, document generation, assisted form filling, and a review surface before
          submit. Jober is not a job board and does not guarantee interviews or offers.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Your responsibilities</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>You review and approve every application before it is submitted.</li>
          <li>You provide accurate information in your vault and materials.</li>
          <li>You comply with our Acceptable Use Policy and each employer site&apos;s terms.</li>
          <li>You complete CAPTCHAs, logins, and verification steps when required.</li>
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Accounts &amp; security</h2>
        <p>
          Keep your credentials secure. You are responsible for activity under your account.
          Notify us promptly of unauthorized access at{" "}
          <Link href="mailto:security@jober.app" className="underline underline-offset-2">
            security@jober.app
          </Link>
          .
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Plans &amp; billing</h2>
        <p>
          Free and Pro plans include usage limits described on the{" "}
          <Link href="/pricing" className="underline underline-offset-2">
            Pricing
          </Link>{" "}
          page. When paid billing is enabled, subscriptions are processed via Stripe; cancellation
          returns you to Free limits at period end unless otherwise stated at checkout.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Disclaimers</h2>
        <p>
          The service is provided “as is” to the extent permitted by law. We do not warrant
          uninterrupted operation of third-party employer sites. Automated assistance may fail when
          sites change; you remain responsible for final submissions.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Limitation of liability</h2>
        <p>
          To the maximum extent permitted by law, Jober is not liable for indirect, incidental, or
          consequential damages arising from your use of the service. Our aggregate liability is
          limited to the fees you paid us in the twelve months before the claim, or $100 if you use
          the Free tier.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Changes</h2>
        <p>
          We may update these terms. Material changes will be posted here with an updated date.
          Continued use after changes constitutes acceptance.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Contact</h2>
        <p>
          <Link href="mailto:legal@jober.app" className="underline underline-offset-2">
            legal@jober.app
          </Link>
        </p>
      </section>
    </LegalDocument>
  );
}
