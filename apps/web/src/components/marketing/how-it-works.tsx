import { HOW_IT_WORKS_STEPS } from "@/lib/marketing/content";
import { motionFadeIn } from "@/lib/design/motion";
import { spacing, surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function HowItWorks({
  compact = false,
  showIntro = true,
}: {
  compact?: boolean;
  showIntro?: boolean;
}) {
  return (
    <section
      id="how-it-works"
      aria-labelledby={showIntro ? "how-it-works-heading" : undefined}
      className={cn(
        "px-6 py-20",
        showIntro && "border-t border-border/50",
        spacing.section,
      )}
    >
      <div className="mx-auto max-w-6xl">
        {showIntro ? (
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-medium uppercase tracking-widest text-accent">
              How it works
            </p>
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
        ) : null}

        <ol className={cn("grid gap-4 md:grid-cols-2 lg:grid-cols-4", showIntro ? "mt-12" : "mt-0")}>
          {HOW_IT_WORKS_STEPS.map(({ icon: Icon, title, body, detail }, index) => (
            <li
              key={title}
              className={cn(surface.card, "relative rounded-lg p-5", motionFadeIn)}
            >
              <span className="text-xs font-medium text-muted-foreground">Step {index + 1}</span>
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
          ))}
        </ol>
      </div>
    </section>
  );
}
