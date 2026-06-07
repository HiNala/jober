import Link from "next/link";
import { ArrowRight, CheckCircle2, Shield, UserCheck } from "lucide-react";

import { AnimatedBackground } from "@/components/marketing/animated-background";
import { buttonVariants } from "@/components/ui/button";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const pillars = [
  {
    icon: UserCheck,
    title: "You choose every job",
    body: "Jober assists applications you select — never spray-and-pray volume.",
  },
  {
    icon: Shield,
    title: "Review before submit",
    body: "Forms fill with your consent; you approve the final submit.",
  },
  {
    icon: CheckCircle2,
    title: "Honest handoffs",
    body: "CAPTCHA, login, and sensitive fields pause for you — no bypass.",
  },
] as const;

export function MarketingHero() {
  return (
    <section className="relative overflow-hidden px-6 py-20 md:py-28">
      <AnimatedBackground />
      <div className={cn("relative mx-auto max-w-3xl text-center", motionFadeIn)}>
        <p className="text-sm font-medium uppercase tracking-widest text-accent">
          You-in-the-loop applications
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight md:text-5xl md:leading-tight">
          Tailored startup applications with clarity at every step
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
          Jober prepares materials, fills forms with your consent, and pauses for your
          review before anything submits. Quality and tracking — not automation in
          hiding.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className={cn(buttonVariants({ size: "lg" }), "inline-flex gap-2")}
          >
            Open dashboard
            <ArrowRight className="size-4" aria-hidden />
          </Link>
          <Link
            href="/vault"
            className={buttonVariants({ variant: "outline", size: "lg" })}
          >
            Set up profile vault
          </Link>
        </div>
      </div>

      <ul className="relative mx-auto mt-16 grid max-w-4xl gap-4 md:grid-cols-3">
        {pillars.map(({ icon: Icon, title, body }) => (
          <li
            key={title}
            className="rounded-lg border border-border/60 bg-card/60 p-4 text-left backdrop-blur-sm"
          >
            <Icon className="mb-2 size-5 text-accent" aria-hidden />
            <h2 className="text-sm font-semibold">{title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">{body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
