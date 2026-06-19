"use client";

import { Eye, FileCheck2, Radar, Shield } from "lucide-react";

import { FillDiffMock } from "@/components/marketing/fill-diff-mock";
import { useScrollReveal } from "@/lib/hooks/use-scroll-reveal";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const SUPPORT_CELLS = [
  {
    icon: FileCheck2,
    title: "ATS-grounded letters",
    body: "Voice presets and claims tied to your vault — not invented employers.",
    num: "02",
  },
  {
    icon: Radar,
    title: "Runs you can audit",
    body: "Every checkpoint and artifact logged in your workspace.",
    num: "03",
  },
  {
    icon: Shield,
    title: "Honest handoffs",
    body: "CAPTCHA and login walls pause the run until you act.",
    num: "04",
  },
] as const;

export function DifferentiatorBento() {
  const sectionRef = useScrollReveal<HTMLElement>();

  return (
    <section
      ref={sectionRef}
      id="differentiator"
      aria-labelledby="differentiator-heading"
      className="bg-white px-6 py-24"
    >
      <div className="mx-auto max-w-6xl">
        {/* Section header with display scale */}
        <div className="mx-auto max-w-2xl text-center">
          <p className="font-mono text-xs font-medium uppercase tracking-[0.22em] text-accent">
            01 — Differentiator
          </p>
          <h2
            id="differentiator-heading"
            className="mt-4 font-bold tracking-[-0.03em]"
            style={{ fontSize: "clamp(2rem, 4.5vw, 3.25rem)", lineHeight: 1.1 }}
          >
            <span className="block">Review before submit</span>
            <span className="block text-foreground/30">— by default.</span>
          </h2>
          <p className="mt-4 text-base text-muted-foreground">
            Auto-submit is never the default. See proposed fills beside what landed on the page.
          </p>
        </div>

        <ul className="mt-14 grid gap-4 md:grid-cols-3 md:grid-rows-2">
          {/* Hero card — spans 2 cols × 2 rows */}
          <li
            className={cn(
              surface.marketing,
              "relative flex flex-col gap-4 overflow-hidden rounded-2xl p-7 md:col-span-2 md:row-span-2",
              motionFadeIn,
            )}
          >
            <div className="flex items-start justify-between gap-3">
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
              <span
                className="shrink-0 font-mono text-4xl font-bold leading-none text-foreground/[0.06]"
                aria-hidden
              >
                01
              </span>
            </div>
            <FillDiffMock className="mt-auto" />
          </li>

          {/* Support cells */}
          {SUPPORT_CELLS.map(({ icon: Icon, title, body, num }) => (
            <li
              key={title}
              className={cn(surface.marketing, "relative overflow-hidden rounded-2xl p-5", motionFadeIn)}
            >
              <span
                className="absolute right-3 top-2 font-mono text-4xl font-bold leading-none text-foreground/[0.05]"
                aria-hidden
              >
                {num}
              </span>
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
