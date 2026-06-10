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

export const HOW_IT_WORKS_STEPS: {
  icon: LucideIcon;
  title: string;
  body: string;
  detail: string;
}[] = [
  {
    icon: ListChecks,
    title: "Pick the roles you want",
    body: "Import or add jobs to your queue. Jober never applies on its own — you choose every target.",
    detail:
      "Discover boards, refresh saved searches, or import spreadsheets. Fit signals help you prioritize — you still decide what enters the queue.",
  },
  {
    icon: ClipboardList,
    title: "Vault + tailored materials",
    body: "Your profile vault powers cover letters and form fills. Sensitive fields stay masked until you need them.",
    detail:
      "Resume ingestion seeds skills and history. Cover letters follow your voice presets with claims grounded in vault data — not invented employers or titles.",
  },
  {
    icon: Eye,
    title: "Watch, then review",
    body: "Live run console shows each step. CAPTCHA, login, and checkpoints pause for you — no silent bypass.",
    detail:
      "Screenshots and an event stream show fills in progress. When a site needs a human — CAPTCHA, OAuth login, ambiguous fields — the run stops and asks.",
  },
  {
    icon: Send,
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
  body: string;
  bullets: string[];
}[] = [
  {
    icon: Compass,
    title: "Unified discovery",
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
    body: "Jober assists applications you select. No spray-and-pray volume, no hidden submits.",
    bullets: [
      "Queue ownership stays with you",
      "Checkpoints pause until you act",
      "Acceptable use: only roles you choose, respecting site terms",
    ],
  },
];

export const FAQ_ITEMS: { question: string; answer: string }[] = [
  {
    question: "Does Jober auto-submit applications?",
    answer:
      "No. Auto-submit is never the default. Every application pauses for your review; nothing is sent until you explicitly approve the final submit.",
  },
  {
    question: "What happens with CAPTCHAs, logins, or 2FA?",
    answer:
      "The run stops at a human checkpoint. Jober does not bypass CAPTCHAs, OAuth walls, or multi-factor prompts — you complete those steps, then the run can continue.",
  },
  {
    question: "Is my vault data private?",
    answer:
      "Your profile vault is tenant-scoped and encrypted for sensitive fields. We do not sell your data. Admin support views exclude raw vault secrets by design.",
  },
  {
    question: "What data does Jober store?",
    answer:
      "Account info, your job queue, run artifacts (screenshots, event logs), vault fields you provide, and documents you generate. Marketing analytics are optional and first-party only.",
  },
  {
    question: "How do cookies and analytics work?",
    answer:
      "We set a session cookie for auth and an optional analytics consent cookie. If you decline analytics, no usage events are recorded on your device or accepted by our API.",
  },
  {
    question: "How does billing and LLM usage work?",
    answer:
      "Free and Pro plans include a monthly managed LLM budget for letter generation and fills. You can optionally bring your own API keys (BYOK) in Settings — then your provider bills you directly and usage counts against your key, not our managed pool.",
  },
  {
    question: "Can I apply to jobs I did not choose?",
    answer:
      "No. Jober only works on jobs you add to your queue. Our acceptable use policy prohibits evasion, spam applications, or violating employer site terms.",
  },
];

export const PRICING_FAQ: { question: string; answer: string }[] = [
  {
    question: "When will Pro checkout be available?",
    answer:
      "Stripe subscription checkout is rolling out soon. Free tier limits are live today and match what you see in Settings → usage.",
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
