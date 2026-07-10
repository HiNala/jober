import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function MarketingCtaBand({
  title = "Ready to apply with clarity?",
  lead = "Create a free account — review every submit before it leaves your workspace.",
  signupFeature,
  secondaryHref = "/pricing",
  secondaryFeature,
  secondaryLabel = "View pricing",
}: {
  title?: string;
  lead?: string;
  signupFeature: string;
  secondaryHref?: string;
  secondaryFeature?: string;
  secondaryLabel?: string;
}) {
  return (
    <section
      aria-labelledby="marketing-cta-band-heading"
      className={cn(
        "relative overflow-hidden border-y border-border/40 bg-primary px-6 py-24",
        motionFadeIn,
      )}
    >
      {/* Subtle background texture */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 20% 50%, oklch(1 0 0 / 0.12) 0%, transparent 60%), radial-gradient(ellipse 60% 80% at 80% 50%, oklch(0.2 0.08 260 / 0.35) 0%, transparent 60%)",
        }}
      />

      <div className="relative mx-auto max-w-3xl text-center">
        <p className="font-mono text-[0.65rem] font-medium uppercase tracking-[0.22em] text-primary-foreground/70">
          Get started
        </p>
        <h2
          id="marketing-cta-band-heading"
          className="mt-4 text-3xl font-bold tracking-[-0.02em] text-primary-foreground md:text-4xl"
        >
          {title}
        </h2>
        <p className="mx-auto mt-4 max-w-md text-lg text-primary-foreground/80">{lead}</p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <MarketingCtaLink
            href="/signup"
            feature={signupFeature}
            size="lg"
            className="rounded-full bg-background px-8 font-semibold text-foreground shadow-lg shadow-black/25 hover:bg-background/90"
          >
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
          {secondaryFeature ? (
            <Link
              href={secondaryHref}
              className="inline-flex h-11 items-center justify-center rounded-full border border-primary-foreground/25 bg-primary-foreground/10 px-8 text-sm font-medium text-primary-foreground backdrop-blur-sm transition-colors hover:bg-primary-foreground/20"
            >
              {secondaryLabel}
            </Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}
