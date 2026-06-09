import type { Metadata } from "next";

import { MarketingShell } from "@/components/marketing/marketing-shell";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function legalStubMetadata(title: string, description: string): Metadata {
  return { title, description };
}

export function LegalStubPage({
  title,
  lead,
  body,
}: {
  title: string;
  lead: string;
  body: string;
}) {
  return (
    <MarketingShell>
      <article className={cn("mx-auto max-w-2xl px-6 py-16", motionFadeIn)}>
        <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-4 text-muted-foreground">{lead}</p>
        <p className="mt-6 text-sm leading-relaxed text-muted-foreground">{body}</p>
      </article>
    </MarketingShell>
  );
}
