import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function MarketingPageHeader({
  eyebrow,
  title,
  lead,
  className,
}: {
  eyebrow?: string;
  title: string;
  lead?: string;
  className?: string;
}) {
  return (
    <header className={cn("mx-auto max-w-3xl text-center", motionFadeIn, className)}>
      {eyebrow ? (
        <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
          {eyebrow}
        </p>
      ) : null}
      <h1 className="mt-3 text-3xl font-semibold tracking-[-0.02em] md:text-4xl md:leading-tight">
        {title}
      </h1>
      {lead ? (
        <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground md:text-xl">{lead}</p>
      ) : null}
    </header>
  );
}
