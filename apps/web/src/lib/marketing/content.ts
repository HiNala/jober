import type { LucideIcon } from "lucide-react";
import {
  Activity,
  ClipboardList,
  Clock3,
  Compass,
  Eye,
  FileCheck2,
  ListChecks,
  Radar,
  Send,
  Shield,
  UserCheck,
} from "lucide-react";

export type ContentBlock = { title: string; body: string };

/** Positioning audit §17 — use verbatim on hero and in metadata where space allows. */
export const POSITIONING_ONE_LINER =
  "Apply to every job on your list, at your quality bar. You review and submit.";

export const POSITIONING_SUBHEAD =
  "AI fills the form, you read the diff and hit submit. Your applications, your standard, your control.";

export const HOW_IT_WORKS_STEPS: {
  icon: LucideIcon;
  slug: string;
  title: string;
  body: string;
  detail: string;
}[] = [
  {
    icon: ListChecks,
    slug: "pick-roles",
    title: "Pick the roles you want",
    body: "Import or add jobs to your queue. Jober never applies on its own — you choose every target.",
    detail:
      "Discover boards, refresh saved searches, or import spreadsheets. Fit signals help you prioritize — you still decide what enters the queue.",
  },
  {
    icon: ClipboardList,
    slug: "vault-materials",
    title: "Vault + tailored materials",
    body: "Your profile vault powers cover letters and form fills. Sensitive fields stay masked until you need them.",
    detail:
      "Resume ingestion seeds skills and history. Cover letters follow your voice presets with claims grounded in vault data — not invented employers or titles.",
  },
  {
    icon: Eye,
    slug: "watch-review",
    title: "Watch, then review",
    body: "Live run console shows each step. CAPTCHA, login, and checkpoints pause for you — no silent bypass.",
    detail:
      "Screenshots and an event stream show fills in progress. When a site needs a human — CAPTCHA, OAuth login, ambiguous fields — the run stops and asks.",
  },
  {
    icon: Send,
    slug: "approve-submit",
    title: "You approve submit",
    body: "Review the filled application and diff. Nothing submits until you explicitly confirm.",
    detail:
      "Auto-submit is never the default. The review surface shows what changed; you confirm or send the run back for edits.",
  },
];

export const VALUE_PROPS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: Clock3,
    title: "Hours back, not hidden automation",
    body: "Batch prep, mapping, and uploads run while you focus on choosing the right roles — not retyping the same answers.",
  },
  {
    icon: FileCheck2,
    title: "ATS-quality materials",
    body: "Cover letters and attachments follow your voice presets and ATS-safe formatting. Claims stay grounded in your vault.",
  },
  {
    icon: Radar,
    title: "Tracking you can trust",
    body: "Every run, checkpoint, and submit is logged in your workspace. Know exactly what was sent and when.",
  },
  {
    icon: Activity,
    title: "Live watch, calm console",
    body: "Stream events and screenshots in the run console. When something needs you, the UI says so — plainly.",
  },
];

export const FEATURE_DEEP_DIVES: {
  icon: LucideIcon;
  title: string;
  specLabel: string;
  howItWorksHref?: string;
  hero?: boolean;
  body: string;
  bullets: string[];
}[] = [
  {
    icon: Compass,
    title: "Unified discovery",
    specLabel: "queues · dedupe · fit signals",
    body: "Search boards and import lists into named target queues with dedupe and fit signals.",
    bullets: [
      "Saved searches you can refresh on demand",
      "Spreadsheet import with platform detection",
      "Batch launch only for jobs you explicitly queued",
    ],
  },
  {
    icon: FileCheck2,
    title: "Tailored letters & documents",
    specLabel: "voice · PDF · regenerate",
    body: "Cover letters and attachments that sound like you — grounded in resume facts, not generic fluff.",
    bullets: [
      "Voice presets and paragraph locks",
      "ATS-safe PDF output",
      "Regenerate sections without rewriting the whole letter",
    ],
  },
  {
    icon: Eye,
    title: "Live-watch canvas",
    specLabel: "SSE · screenshots · checkpoints",
    howItWorksHref: "/how-it-works#step-watch-review",
    hero: true,
    body: "See what the agent sees: screenshots, fill diffs, and checkpoint cards in one run console.",
    bullets: [
      "SSE event stream with calm terminal styling",
      "Human-required states are explicit, not buried in logs",
      "Review-and-submit surface on the same run",
    ],
  },
  {
    icon: Radar,
    title: "Workspace analytics",
    specLabel: "funnel · usage · consent-gated",
    body: "Your own funnel and usage dashboards — first-party, consent-gated, no third-party ad pixels.",
    bullets: [
      "Runs, submits, and letter generation in one place",
      "Plan usage visible in Settings",
      "Anonymous marketing analytics only with explicit opt-in",
    ],
  },
  {
    icon: Shield,
    title: "Safety posture you can verify",
    specLabel: "review-first · CAPTCHA handoff",
    howItWorksHref: "/how-it-works#step-approve-submit",
    body: "Trust features, not trust us blindly. Policy is enforced in code and surfaced in the UI.",
    bullets: [
      "Review before every submit — auto-submit is never the default",
      "CAPTCHA, login, and 2FA always hand off to you",
      "Sensitive vault fields require consent before autofill",
      "Job-page text treated as untrusted input",
    ],
  },
  {
    icon: UserCheck,
    title: "You-in-the-loop by default",
    specLabel: "queue-owned · no spray-and-pray",
    howItWorksHref: "/how-it-works#step-pick-roles",
    body: "Jober assists applications you select. No spray-and-pray volume, no hidden submits.",
    bullets: [
      "Queue ownership stays with you",
      "Checkpoints pause until you act",
      "Acceptable use: only roles you choose, respecting site terms",
    ],
  },
];

/** Homepage trust strip — positioning audit §18. */
export const LANDING_TRUST_ITEMS = [
  "Review before submit",
  "No CAPTCHA bypass",
  "No third-party trackers",
  "BYOK supported",
] as const;

/** Objection-ordered FAQ teaser for `/` (full list on /faq). */
export const HOME_FAQ_TEASER = [
  {
    question: "Is this a bot that sprays applications?",
    answer:
      "No. Jober only works on jobs you queue. Every application pauses for your review — nothing submits until you approve.",
  },
  {
    question: "Will ATSs flag automated fills?",
    answer:
      "Jober fills forms with your real vault data and stops at CAPTCHA, login, and ambiguous fields. You review the diff before submit — same judgment you'd apply manually.",
  },
  {
    question: "Where does my data live?",
    answer:
      "Your queue, runs, and vault stay in your private workspace. Sensitive vault fields are encrypted; you can use your own LLM keys (BYOK) in Settings.",
  },
] as const;

export const FOUNDER_PROOF = {
  eyebrow: "Built in the open",
  title: "Born from a 155-lead job search",
  story:
    "Jober started as tooling for one operator's own pipeline — importing a Direct Job Leads tracker, tailoring letters per role, and refusing to click submit without reading the diff. The product is that workflow, productized.",
  stats: [
    { label: "Tracker rows dogfooded", value: "155" },
    { label: "Submit default", value: "Review first" },
    { label: "Managed LLM on Free", value: "$5/mo cap" },
  ],
} as const;

/** Redacted fill-diff sample for marketing bento (not live API data). */
export const FILL_DIFF_MOCK_ROWS = [
  {
    field: "Work authorization",
    proposed: "Authorized to work in the US",
    actual: "Authorized to work in the US",
    matched: true,
  },
  {
    field: "Resume upload",
    proposed: "[resume.pdf]",
    actual: "[resume.pdf]",
    matched: true,
  },
  {
    field: "Cover letter",
    proposed: "Tailored intro paragraph…",
    actual: "Tailored intro paragraph…",
    matched: true,
  },
  {
    field: "LinkedIn URL",
    proposed: "linkedin.com/in/…",
    actual: "—",
    matched: false,
  },
] as const;

export type FaqCategory = "product" | "trust";

export type FaqItem = {
  question: string;
  answer: string;
  category: FaqCategory;
  learnMore?: { label: string; href: string };
};

export const FAQ_ITEMS: FaqItem[] = [
  {
    category: "product",
    question: "Does Jober auto-submit applications?",
    answer:
      "No. Auto-submit is never the default. Every application pauses for your review; nothing is sent until you explicitly approve the final submit.",
    learnMore: { label: "How review works", href: "/how-it-works#step-approve-submit" },
  },
  {
    category: "product",
    question: "What happens with CAPTCHAs, logins, or 2FA?",
    answer:
      "The run stops at a human checkpoint. Jober does not bypass CAPTCHAs, OAuth walls, or multi-factor prompts — you complete those steps, then the run can continue.",
    learnMore: { label: "Watch step", href: "/how-it-works#step-watch-review" },
  },
  {
    category: "trust",
    question: "Is my vault data private?",
    answer:
      "Your profile vault is tenant-scoped and encrypted for sensitive fields. We do not sell your data. Admin support views exclude raw vault secrets by design.",
    learnMore: { label: "Privacy policy", href: "/privacy" },
  },
  {
    category: "trust",
    question: "What data does Jober store?",
    answer:
      "Account info, your job queue, run artifacts (screenshots, event logs), vault fields you provide, and documents you generate. Marketing analytics are optional and first-party only.",
    learnMore: { label: "Privacy policy", href: "/privacy" },
  },
  {
    category: "trust",
    question: "How do cookies and analytics work?",
    answer:
      "We set a session cookie for auth and an optional analytics consent cookie. If you decline analytics, no usage events are recorded on your device or accepted by our API.",
    learnMore: { label: "Privacy policy", href: "/privacy" },
  },
  {
    category: "trust",
    question: "How does billing and LLM usage work?",
    answer:
      "Free and Pro plans include a monthly managed LLM budget for letter generation and fills. You can optionally bring your own API keys (BYOK) in Settings — then your provider bills you directly and usage counts against your key, not our managed pool.",
    learnMore: { label: "Pricing", href: "/pricing" },
  },
  {
    category: "product",
    question: "Can I apply to jobs I did not choose?",
    answer:
      "No. Jober only works on jobs you add to your queue. Our acceptable use policy prohibits evasion, spam applications, or violating employer site terms.",
    learnMore: { label: "Acceptable use", href: "/acceptable-use" },
  },
];

export const FAQ_CATEGORIES: { id: FaqCategory; label: string }[] = [
  { id: "product", label: "Product" },
  { id: "trust", label: "Trust & billing" },
];

export const PRICING_FAQ: { question: string; answer: string }[] = [
  {
    question: "How do I upgrade to Pro?",
    answer:
      "When Stripe is enabled, use Upgrade to Pro on the pricing page or in Settings → Plan & billing, then complete checkout on Stripe. Free limits match Settings today; if self-serve is not live yet, join the waitlist on pricing.",
  },
  {
    question: "What counts as a run?",
    answer:
      "Each assisted application attempt against a queued job target counts toward your monthly runs. Failed runs that never reached submit still count — check the run console for status.",
  },
  {
    question: "What if I exceed my LLM budget?",
    answer:
      "Managed LLM spend is capped per plan. Add a BYOK key in Settings to continue generation with your own provider, or wait for the next billing period.",
  },
  {
    question: "Can I downgrade from Pro?",
    answer:
      "Yes. When billing is enabled, canceling returns you to Free limits at the end of the paid period. Your queue and vault data remain in your workspace.",
  },
];
