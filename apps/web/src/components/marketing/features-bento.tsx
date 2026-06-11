import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { HeroRunPreview } from "@/components/marketing/hero-run-preview";
import { FEATURE_DEEP_DIVES } from "@/lib/marketing/content";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function FeaturesBento() {
  const hero = FEATURE_DEEP_DIVES.find((f) => f.hero);
  const cells = FEATURE_DEEP_DIVES.filter((f) => !f.hero);

  return (
    <ul className="mx-auto mt-12 grid max-w-6xl gap-4 md:grid-cols-3 md:auto-rows-[minmax(0,1fr)]">
      {hero ? (
        <li
          className={cn(
            surface.marketing,
            "relative col-span-1 row-span-2 flex flex-col overflow-hidden rounded-xl p-6 md:col-span-2",
            motionFadeIn,
          )}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-accent">
                {hero.specLabel}
              </p>
              <h2 className="mt-2 text-xl font-semibold tracking-[-0.02em]">{hero.title}</h2>
            </div>
            {hero.howItWorksHref ? (
              <Link
                href={hero.howItWorksHref}
                className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-primary"
              >
                See the loop
                <ArrowUpRight className="size-4" aria-hidden />
              </Link>
            ) : null}
          </div>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">{hero.body}</p>
          <div className="mt-6 flex-1">
            <HeroRunPreview className="max-w-none" />
          </div>
        </li>
      ) : null}
      {cells.map(({ icon: Icon, title, specLabel, body, bullets, howItWorksHref }) => (
        <li key={title} className={cn(surface.marketing, "flex flex-col rounded-xl p-5", motionFadeIn)}>
          <p className="font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-accent">
            {specLabel}
          </p>
          <Icon className="mt-3 size-5 text-accent" aria-hidden />
          <h2 className="mt-2 text-base font-semibold">{title}</h2>
          <p className="mt-2 flex-1 text-sm text-muted-foreground">{body}</p>
          <ul className="mt-4 space-y-1.5 text-sm text-muted-foreground">
            {bullets.slice(0, 2).map((item) => (
              <li key={item} className="flex gap-2">
                <span className="text-accent" aria-hidden>
                  ·
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
          {howItWorksHref ? (
            <Link
              href={howItWorksHref}
              className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary"
            >
              How it works
              <ArrowUpRight className="size-3.5" aria-hidden />
            </Link>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
