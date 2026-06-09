import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const quotes = [
  {
    quote:
      "Finally a tool that stops before submit. I review every application — Jober just removes the grunt work.",
    attribution: "Early design partner",
    role: "Senior product manager",
  },
  {
    quote:
      "The run console made our team comfortable. We can see checkpoints instead of guessing what the agent did.",
    attribution: "Private beta user",
    role: "Engineering lead",
  },
] as const;

export function SocialProof() {
  return (
    <section aria-labelledby="social-proof-heading" className="border-y border-border/50 bg-muted/15 px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-accent">Social proof</p>
          <h2 id="social-proof-heading" className="mt-3 text-3xl font-semibold tracking-tight">
            Built with operators who care about trust
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Placeholder quotes from design partners — full case studies ship with Mission 30.
          </p>
        </div>

        <ul className="mt-10 grid gap-4 md:grid-cols-2">
          {quotes.map(({ quote, attribution, role }) => (
            <li key={attribution} className={cn(surface.card, "rounded-lg p-6", motionFadeIn)}>
              <blockquote className="text-base leading-relaxed">&ldquo;{quote}&rdquo;</blockquote>
              <footer className="mt-4 text-sm text-muted-foreground">
                <cite className="not-italic font-medium text-foreground">{attribution}</cite>
                <span className="block text-xs">{role}</span>
              </footer>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
