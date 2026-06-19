import { FOUNDER_PROOF } from "@/lib/marketing/content";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function FounderProof() {
  return (
    <section
      aria-labelledby="founder-proof-heading"
      className="border-y border-border/20 bg-muted/8 px-6 py-20"
    >
      <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className={motionFadeIn}>
          <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
            {FOUNDER_PROOF.eyebrow}
          </p>
          <h2
            id="founder-proof-heading"
            className="mt-3 text-3xl font-semibold tracking-[-0.02em] md:text-4xl"
          >
            {FOUNDER_PROOF.title}
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground">
            {FOUNDER_PROOF.story}
          </p>
          <p className="mt-4 text-sm text-muted-foreground">
            Formal case studies and customer quotes will land when we have permission to share
            them — not placeholder testimonials.
          </p>
        </div>
        <ul className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
          {FOUNDER_PROOF.stats.map(({ label, value }) => (
            <li
              key={label}
              className={cn(surface.marketing, "rounded-xl p-5 text-center lg:text-left", motionFadeIn)}
            >
              <p className="text-2xl font-semibold tabular-nums tracking-tight text-foreground">
                {value}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{label}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
