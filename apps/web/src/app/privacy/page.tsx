import type { Metadata } from "next";
import Link from "next/link";

import { LegalDocument } from "@/components/marketing/legal-document";
import { marketingMetadata } from "@/lib/marketing/metadata";

export const metadata: Metadata = marketingMetadata({
  title: "Privacy Policy",
  description:
    "How Jober collects, stores, and protects your data — including vault encryption, run artifacts, and consent-gated analytics.",
  path: "/privacy",
});

export default function PrivacyPage() {
  return (
    <LegalDocument title="Privacy Policy">
      <p>
        <strong>Last updated:</strong> June 2026 (draft). This policy describes how Jober (“we”,
        “us”) handles information when you use our assisted job application service.
      </p>

      <section>
        <h2 className="text-lg font-semibold text-foreground">What we collect</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Account information (email, display name, authentication identifiers)</li>
          <li>Job queue data, run logs, screenshots, and artifacts from assisted applications</li>
          <li>Profile vault fields you provide, including encrypted sensitive values</li>
          <li>Documents you generate (e.g. cover letters) and application materials</li>
          <li>
            Optional first-party analytics events if you explicitly allow analytics on this device
          </li>
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">How we use data</h2>
        <p>
          We use your data to operate the service: filling forms you approve, generating documents
          from your vault, showing run consoles, enforcing plan limits, and providing support.
          We do not sell your personal information. We do not use third-party advertising trackers.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Vault &amp; sensitive fields</h2>
        <p>
          Sensitive profile fields (for example EEO-related answers) are stored with encryption and
          require explicit field consent before autofill. Masked values are shown by default in the
          UI. Admin support tooling is designed to exclude raw vault secrets.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Retention</h2>
        <p>
          We retain workspace data while your account is active. Run artifacts and audit logs are
          kept to support review, recovery, and billing reconciliation. You may request export or
          deletion subject to legal and operational requirements — contact{" "}
          <Link href="mailto:privacy@jober.app" className="underline underline-offset-2">
            privacy@jober.app
          </Link>
          .
        </p>
      </section>

      <section id="cookies-and-analytics">
        <h2 className="text-lg font-semibold text-foreground">Cookies &amp; analytics</h2>
        <p>
          <strong>Authentication:</strong> session cookies keep you signed in. These are necessary
          for the product to function.
        </p>
        <p className="mt-2">
          <strong>Analytics consent:</strong> we set{" "}
          <code className="rounded bg-muted px-1">jober_analytics_consent</code> only after you
          choose Allow or Decline on the consent banner. If you decline, or if your browser sends
          Do Not Track, our client SDK does not enqueue events and our API rejects tracking for that
          request. No third-party analytics scripts are loaded.
        </p>
        <p className="mt-2">
          Allowed analytics include anonymous page views and product feature usage — never passwords,
          vault contents, or application answers.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Your rights</h2>
        <p>
          Depending on your jurisdiction you may have rights to access, correct, delete, or port
          your data. Contact us to exercise these rights. If you are in the EU/UK, you may also
          lodge a complaint with your supervisory authority.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground">Contact</h2>
        <p>
          Questions:{" "}
          <Link href="mailto:privacy@jober.app" className="underline underline-offset-2">
            privacy@jober.app
          </Link>
          . See also our{" "}
          <Link href="/terms" className="underline underline-offset-2">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link href="/acceptable-use" className="underline underline-offset-2">
            Acceptable Use Policy
          </Link>
          .
        </p>
      </section>
    </LegalDocument>
  );
}
