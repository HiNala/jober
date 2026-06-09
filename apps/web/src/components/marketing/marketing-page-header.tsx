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
        <p className="text-sm font-medium uppercase tracking-widest text-accent">{eyebrow}</p>
      ) : null}
      <h1 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">{title}</h1>
      {lead ? <p className="mt-4 text-lg text-muted-foreground">{lead}</p> : null}
    </header>
  );
}
