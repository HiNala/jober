import Link from "next/link";
import { ChevronDown } from "lucide-react";

import type { FaqItem } from "@/lib/marketing/content";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function FaqList({
  items,
  id,
}: {
  items: FaqItem[] | { question: string; answer: string }[];
  id?: string;
}) {
  return (
    <div id={id} className="space-y-3">
      {items.map((item) => (
        <FaqAccordionItem key={item.question} item={item} />
      ))}
    </div>
  );
}

function FaqAccordionItem({
  item,
}: {
  item: FaqItem | { question: string; answer: string };
}) {
  const learnMore = "learnMore" in item ? item.learnMore : undefined;

  return (
    <details className={cn(surface.card, "group rounded-lg px-4 py-3 open:pb-4")}>
      <summary className="cursor-pointer list-none text-sm font-medium marker:content-none [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between gap-3">
          {item.question}
          <ChevronDown
            className="size-4 shrink-0 text-muted-foreground transition-transform duration-200 group-open:rotate-180 motion-reduce:transition-none"
            aria-hidden
          />
        </span>
      </summary>
      <div className="grid grid-rows-[0fr] transition-[grid-template-rows] duration-200 group-open:grid-rows-[1fr] motion-reduce:transition-none">
        <div className="overflow-hidden">
          <p className="pt-3 text-sm leading-relaxed text-muted-foreground">{item.answer}</p>
          {learnMore ? (
            <Link
              href={learnMore.href}
              className="mt-3 inline-block text-sm font-medium text-primary hover:underline"
            >
              {learnMore.label} →
            </Link>
          ) : null}
        </div>
      </div>
    </details>
  );
}
