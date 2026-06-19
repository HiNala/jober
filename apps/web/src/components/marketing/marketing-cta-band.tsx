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
        "relative overflow-hidden bg-blue-600 px-6 py-24",
        motionFadeIn,
      )}
    >
      {/* Subtle background texture */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 20% 50%, oklch(0.55 0.18 250 / 0.4) 0%, transparent 60%), radial-gradient(ellipse 60% 80% at 80% 50%, oklch(0.35 0.16 260 / 0.3) 0%, transparent 60%)",
        }}
      />

      <div className="relative mx-auto max-w-3xl text-center">
        <p className="font-mono text-[0.65rem] font-medium uppercase tracking-[0.22em] text-blue-200">
          Get started
        </p>
        <h2
          id="marketing-cta-band-heading"
          className="mt-4 text-3xl font-bold tracking-[-0.02em] text-white md:text-4xl"
        >
          {title}
        </h2>
        <p className="mx-auto mt-4 max-w-md text-lg text-blue-100/80">{lead}</p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <MarketingCtaLink
            href="/signup"
            feature={signupFeature}
            size="lg"
            className="rounded-full bg-white px-8 font-semibold text-blue-700 shadow-lg shadow-blue-900/20 hover:bg-blue-50"
          >
            Start free
            <ArrowRight className="size-4" aria-hidden />
          </MarketingCtaLink>
          {secondaryFeature ? (
            <Link
              href={secondaryHref}
              className="inline-flex h-11 items-center justify-center rounded-full border border-white/25 bg-white/10 px-8 text-sm font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/20"
            >
              {secondaryLabel}
            </Link>
          ) : null}
        </div>
      </div>
    </section>
  );
}
