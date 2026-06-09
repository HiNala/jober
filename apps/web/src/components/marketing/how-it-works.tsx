import { ClipboardList, Eye, ListChecks, Send } from "lucide-react";

import { motionFadeIn } from "@/lib/design/motion";
import { spacing, surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const steps = [
  {
    icon: ListChecks,
    title: "Pick the roles you want",
    body: "Import or add jobs to your queue. Jober never applies on its own — you choose every target.",
  },
  {
    icon: ClipboardList,
    title: "Vault + tailored materials",
    body: "Your profile vault powers cover letters and form fills. Sensitive fields stay masked until you need them.",
  },
  {
    icon: Eye,
    title: "Watch, then review",
    body: "Live run console shows each step. CAPTCHA, login, and checkpoints pause for you — no silent bypass.",
  },
  {
    icon: Send,
    title: "You approve submit",
    body: "Review the filled application and diff. Nothing submits until you explicitly confirm.",
  },
] as const;

export function HowItWorks() {
  return (
    <section
      id="how-it-works"
      aria-labelledby="how-it-works-heading"
      className={cn("border-t border-border/50 px-6 py-20", spacing.section)}
    >
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-accent">How it works</p>
          <h2
            id="how-it-works-heading"
            className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl"
          >
            Human-in-the-loop by design
          </h2>
          <p className="mt-3 text-muted-foreground">
            Jober accelerates prep and form work — you keep authority over what gets sent.
          </p>
        </div>

        <ol className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {steps.map(({ icon: Icon, title, body }, index) => (
            <li
              key={title}
              className={cn(
                surface.card,
                "relative rounded-lg p-5",
                motionFadeIn,
              )}
            >
              <span className="text-xs font-medium text-muted-foreground">
                Step {index + 1}
              </span>
              <Icon className="mt-3 size-5 text-accent" aria-hidden />
              <h3 className="mt-2 text-base font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
