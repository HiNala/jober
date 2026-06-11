import { Eye, FileCheck2, Radar, Shield } from "lucide-react";

import { FillDiffMock } from "@/components/marketing/fill-diff-mock";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const SUPPORT_CELLS = [
  {
    icon: FileCheck2,
    title: "ATS-grounded letters",
    body: "Voice presets and claims tied to your vault — not invented employers.",
  },
  {
    icon: Radar,
    title: "Runs you can audit",
    body: "Every checkpoint and artifact logged in your workspace.",
  },
  {
    icon: Shield,
    title: "Honest handoffs",
    body: "CAPTCHA and login walls pause the run until you act.",
  },
] as const;

export function DifferentiatorBento() {
  return (
    <section
      id="differentiator"
      aria-labelledby="differentiator-heading"
      className="border-t border-border/50 px-6 py-20"
    >
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
            Differentiator
          </p>
          <h2
            id="differentiator-heading"
            className="mt-3 text-3xl font-semibold tracking-[-0.02em] md:text-4xl"
          >
            Review before submit — by default
          </h2>
          <p className="mt-3 text-muted-foreground">
            Auto-submit is never the default. See proposed fills beside what landed on the page.
          </p>
        </div>

        <ul className="mt-12 grid gap-4 md:grid-cols-3 md:grid-rows-2">
          <li
            className={cn(
              surface.card,
              "flex flex-col gap-4 rounded-xl p-6 md:col-span-2 md:row-span-2",
              motionFadeIn,
            )}
          >
            <div className="flex items-start gap-3">
              <Eye className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
              <div>
                <h3 className="text-lg font-semibold">You approve the final submit</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  The run console pauses at review checkpoints. Compare field diffs, edit the
                  letter, then click submit — or send the run back.
                </p>
              </div>
            </div>
            <FillDiffMock className="mt-auto" />
          </li>
          {SUPPORT_CELLS.map(({ icon: Icon, title, body }) => (
            <li
              key={title}
              className={cn(surface.card, "rounded-xl p-5", motionFadeIn)}
            >
              <Icon className="size-5 text-accent" aria-hidden />
              <h3 className="mt-3 text-sm font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{body}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
