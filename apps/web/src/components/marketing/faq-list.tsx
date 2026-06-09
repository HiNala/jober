import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function FaqList({
  items,
  id,
}: {
  items: { question: string; answer: string }[];
  id?: string;
}) {
  return (
    <div id={id} className="space-y-3">
      {items.map(({ question, answer }) => (
        <details
          key={question}
          className={cn(surface.card, "group rounded-lg px-4 py-3 open:pb-4")}
        >
          <summary className="cursor-pointer list-none text-sm font-medium marker:content-none [&::-webkit-details-marker]:hidden">
            <span className="flex items-center justify-between gap-3">
              {question}
              <span
                className="text-muted-foreground transition-transform group-open:rotate-45"
                aria-hidden
              >
                +
              </span>
            </span>
          </summary>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{answer}</p>
        </details>
      ))}
    </div>
  );
}
