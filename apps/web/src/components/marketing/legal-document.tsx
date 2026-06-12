import { LegalDraftBanner } from "@/components/marketing/legal-draft-banner";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LegalDocument({
  title,
  summary,
  children,
}: {
  title: string;
  /** Plain-language overview shown above the full policy text. */
  summary: string;
  children: React.ReactNode;
}) {
  return (
    <MarketingShell>
      <article className={cn("mx-auto max-w-3xl px-6 py-16", motionFadeIn)}>
        <LegalDraftBanner />
        <aside
          className={cn(
            surface.marketing,
            "mb-8 rounded-lg border border-border/60 bg-muted/20 px-4 py-3 text-sm leading-relaxed text-foreground",
          )}
          role="note"
        >
          <strong className="font-semibold">In short:</strong> {summary}
        </aside>
        <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
        <div className="mt-8 max-w-none space-y-6 text-sm leading-relaxed text-muted-foreground">
          {children}
        </div>
      </article>
    </MarketingShell>
  );
}
