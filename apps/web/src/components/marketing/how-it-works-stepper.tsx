"use client";

import { useEffect, useRef, useState } from "react";

import { HOW_IT_WORKS_STEPS } from "@/lib/marketing/content";
import { motionFadeIn, brandStepperConnector } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function HowItWorksStepper({ showIntro = true }: { showIntro?: boolean }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [reduceMotion, setReduceMotion] = useState(false);
  const stepRefs = useRef<(HTMLLIElement | null)[]>([]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduceMotion(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    const nodes = stepRefs.current.filter(Boolean) as HTMLLIElement[];
    if (nodes.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]?.target instanceof HTMLElement) {
          const idx = Number(visible[0].target.dataset.stepIndex);
          if (!Number.isNaN(idx)) setActiveIndex(idx);
        }
      },
      { rootMargin: "-20% 0px -35% 0px", threshold: [0.25, 0.5, 0.75] },
    );

    for (const node of nodes) observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="how-it-works"
      aria-labelledby={showIntro ? "how-it-works-heading" : undefined}
      className={cn("px-6 py-12 md:py-16", showIntro && "border-t border-border/50")}
    >
      <div className="mx-auto max-w-6xl">
        {showIntro ? (
          <div className="mx-auto max-w-2xl text-center">
            <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
              How it works
            </p>
            <h2
              id="how-it-works-heading"
              className="mt-3 text-3xl font-semibold tracking-[-0.02em] md:text-4xl"
            >
              Human-in-the-loop by design
            </h2>
          </div>
        ) : null}

        <ol className={cn("relative mt-10 grid gap-4 md:grid-cols-4", showIntro && "mt-12")}>
          <div
            className={cn(
              "pointer-events-none absolute left-[12.5%] right-[12.5%] top-8 hidden md:block",
              brandStepperConnector,
            )}
            aria-hidden
          />
          {HOW_IT_WORKS_STEPS.map(({ icon: Icon, slug, title, body, detail }, index) => {
            const isDominant = index === 2;
            const isActive = activeIndex === index;
            return (
              <li
                key={slug}
                id={`step-${slug}`}
                ref={(el) => {
                  stepRefs.current[index] = el;
                }}
                data-step-index={index}
                className={cn(
                  surface.marketing,
                  "scroll-mt-24 rounded-xl p-5 transition-[box-shadow,border-color,transform]",
                  motionFadeIn,
                  !reduceMotion && isActive && "border-primary/50 shadow-md shadow-primary/5",
                  isDominant && "border-primary/40 ring-1 ring-primary/25 md:scale-[1.02]",
                )}
              >
                <span
                  className={cn(
                    "inline-flex size-7 items-center justify-center rounded-full border text-xs font-mono font-medium",
                    isDominant || isActive
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
                <h2 className="mt-2 text-base font-semibold">{title}</h2>
                <p className="mt-2 text-sm text-muted-foreground">{body}</p>
                <p className="mt-3 text-xs leading-relaxed text-muted-foreground/90">{detail}</p>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
