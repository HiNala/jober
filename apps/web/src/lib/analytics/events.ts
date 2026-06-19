/**
 * Typed analytics event registry — all valid event names and their property shapes.
 *
 * Rules:
 * - Event names use dot-notation: `domain.action` (past tense where possible)
 * - Properties must never include passwords, tokens, API keys, raw prompts, or PII
 * - All events are consent-gated via the SDK — do not call trackEvent without consent
 * - See docs/analytics/event-taxonomy.md for full documentation
 */

import { trackEvent } from "@/lib/analytics/sdk";

/** Safe property value type — excludes objects/arrays to prevent accidental PII leakage. */
type SafeProp = string | number | boolean | null;

export type AnalyticsEventMap = {
  /** Page view — fired automatically by AnalyticsProvider. */
  "page.view": { path: string; title: string };

  /** Marketing CTA click — button/link with a named feature flag. */
  "cta.click": { feature: string; href?: string };

  /* ── Auth ─────────────────────────────────────────────────────────── */
  /** User starts filling out the signup form. */
  "auth.signup_started": { method: "native" | "google" };
  /** Signup completed and user account created. */
  "auth.signup_completed": { method: "native" | "google" };
  /** Signup form submission failed (validation or server error). */
  "auth.signup_failed": { reason: "validation" | "server" | "duplicate" };
  /** User completed a signin. */
  "auth.signin_completed": { method: "native" | "google" };
  /** Signin failed (wrong credentials, account not found, etc.). */
  "auth.signin_failed": { reason: "credentials" | "server" | "not_found" };

  /* ── Batch / Run ────────────────────────────────────────────────────── */
  /** User launched a batch of applications. */
  "batch.launched": { item_count: number; policy: string };
  /** User paused the worker queue. */
  "batch.paused": Record<string, never>;
  /** User resumed the worker queue. */
  "batch.resumed": Record<string, never>;
  /** A single application run was viewed in the run console. */
  "run.viewed": { run_id: string };
  /** A checkpoint was reviewed (approved or sent back) by the user. */
  "checkpoint.reviewed": { action: "approve" | "reject" | "skip" };

  /* ── Vault ─────────────────────────────────────────────────────────── */
  /** User saved a change to their profile vault. */
  "vault.updated": { section: string };

  /* ── Discover ───────────────────────────────────────────────────────── */
  /** User performed a job board search. */
  "discover.search": { board: string; result_count: number };
  /** User created a new job target list. */
  "library.list_created": Record<string, never>;
  /** User accepted candidates into a list. */
  "library.candidates_accepted": { count: number };

  /* ── Documents ──────────────────────────────────────────────────────── */
  /** User generated a cover letter or document. */
  "document.generated": { doc_type: string };

  /* ── Feature generic ────────────────────────────────────────────────── */
  /** Generic feature usage — use specific events above when possible. */
  "feature.use": { feature: string };

  /* ── Observability ─────────────────────────────────────────────────── */
  /** Web Vital metric recorded. */
  "web.vital": { name: string; value: number; rating: string };
  /** Unhandled client-side error caught. */
  "client.error": { message: string; path: string };
};

/** Typesafe wrapper around trackEvent. */
export function track<K extends keyof AnalyticsEventMap>(
  event: K,
  props: AnalyticsEventMap[K],
): void {
  trackEvent(event, props as Record<string, SafeProp>);
}
