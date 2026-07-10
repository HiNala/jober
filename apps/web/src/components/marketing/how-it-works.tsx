"use client";

import { HOW_IT_WORKS_STEPS } from "@/lib/marketing/content";
import { motionFadeIn, brandStepperConnector } from "@/lib/design/motion";
import { useScrollReveal } from "@/lib/hooks/use-scroll-reveal";
import { spacing, surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const DISPLAY_NUMS = ["01", "02", "03", "04"];

export function HowItWorks({
  compact = false,
  showIntro = true,
  variant = "cards",
}: {
  compact?: boolean;
  showIntro?: boolean;
  variant?: "cards" | "stepper";
}) {
  const isStepper = variant === "stepper";
  const sectionRef = useScrollReveal<HTMLElement>();

  return (
    <section
      ref={sectionRef}
      id="how-it-works"
      aria-labelledby={showIntro ? "how-it-works-heading" : undefined}
      className={cn(
        "bg-muted/30 px-6 py-24",
        showIntro && "border-t border-border/40",
        spacing.section,
      )}
    >
      <div className="mx-auto max-w-6xl">
        {showIntro ? (
          <div className="mx-auto max-w-2xl text-center">
            <p className="font-mono text-xs font-medium uppercase tracking-[0.22em] text-accent">
              How it works
            </p>
            <h2
              id="how-it-works-heading"
              className="mt-4 font-bold tracking-[-0.03em]"
              style={{ fontSize: "clamp(2rem, 4.5vw, 3.25rem)", lineHeight: 1.1 }}
            >
              <span className="block">Human-in-the-loop</span>
              <span className="block text-foreground/30">by design.</span>
            </h2>
            <p className="mt-4 text-base text-muted-foreground">
              Jober accelerates prep and form work — you keep authority over what gets sent.
            </p>
          </div>
        ) : null}

        <ol
          className={cn(
            "relative grid gap-4",
            isStepper ? "mt-14 md:grid-cols-4" : "md:grid-cols-2 lg:grid-cols-4",
            showIntro ? "mt-14" : "mt-0",
          )}
        >
          {isStepper ? (
            <div
              className={cn(
                "pointer-events-none absolute left-[12.5%] right-[12.5%] top-8 hidden md:block",
                brandStepperConnector,
              )}
              aria-hidden
            />
          ) : null}

          {HOW_IT_WORKS_STEPS.map(({ icon: Icon, slug, title, body, detail }, index) => {
            const isDominant = isStepper && index === 2;
            return (
              <li
                key={slug}
                id={isStepper ? `step-${slug}` : undefined}
                className={cn(
                  surface.marketing,
                  "relative overflow-hidden rounded-2xl p-6",
                  motionFadeIn,
                  isDominant && "border-primary/60 ring-2 ring-primary/30 md:scale-105",
                )}
              >
                {/* Large display number in background */}
                <span
                  className="pointer-events-none absolute -right-1 -top-3 font-mono text-6xl font-bold leading-none select-none"
                  style={{ color: "oklch(0.7 0.14 250 / 0.12)" }}
                  aria-hidden
                >
                  {DISPLAY_NUMS[index]}
                </span>

                <span
                  className={cn(
                    "relative inline-flex size-7 items-center justify-center rounded-full border text-xs font-mono font-medium",
                    isDominant
                      ? "border-primary/50 bg-primary/10 text-primary"
                      : "border-border text-muted-foreground",
                  )}
                >
                  {index + 1}
                </span>

                {isDominant ? (
                  <div
                    className="mt-3 rounded-md border border-border/50 bg-muted/30 px-2 py-1.5 text-[10px] text-muted-foreground"
                    aria-hidden
                  >
                    <span className="inline-block size-1.5 rounded-full bg-destructive/80" />
                    <span className="mx-1 inline-block size-1.5 rounded-full bg-amber-400/80" />
                    <span className="inline-block size-1.5 rounded-full bg-emerald-500/80" />
                    <span className="ml-2 font-mono">run console · live</span>
                  </div>
                ) : null}

                <Icon className="mt-3 size-5 text-accent" aria-hidden />
                {showIntro ? (
                  <h3 className="mt-2 text-base font-semibold">{title}</h3>
                ) : (
                  <h2 className="mt-2 text-base font-semibold">{title}</h2>
                )}
                <p className="mt-2 text-sm text-muted-foreground">{body}</p>
                {!compact ? (
                  <p className="mt-3 text-xs leading-relaxed text-muted-foreground/90">{detail}</p>
                ) : null}
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
