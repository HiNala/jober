import { LegalDraftBanner } from "@/components/marketing/legal-draft-banner";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function LegalDocument({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <MarketingShell>
      <article className={cn("mx-auto max-w-3xl px-6 py-16", motionFadeIn)}>
        <LegalDraftBanner />
        <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
        <div className="mt-8 max-w-none space-y-6 text-sm leading-relaxed text-muted-foreground">
          {children}
        </div>
      </article>
    </MarketingShell>
  );
}
