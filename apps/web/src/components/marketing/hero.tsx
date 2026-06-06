import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { AnimatedBackground } from "@/components/marketing/animated-background";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function MarketingHero() {
  return (
    <section className="relative overflow-hidden px-6 py-24 md:py-32">
      <AnimatedBackground />
      <div className="relative mx-auto max-w-3xl text-center">
        <p className="text-sm font-medium uppercase tracking-widest text-accent">
          Assisted applications
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight md:text-5xl">
          High-volume startup applications, without the busywork
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Jober prepares tailored materials, fills forms with your consent, and
          stops for human review before anything submits.
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
            href="/queue"
            className={buttonVariants({ variant: "outline", size: "lg" })}
          >
            View queue
          </Link>
        </div>
      </div>
    </section>
  );
}
