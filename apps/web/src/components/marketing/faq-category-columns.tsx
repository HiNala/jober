import { FAQ_CATEGORIES, FAQ_ITEMS } from "@/lib/marketing/content";
import { FaqList } from "@/components/marketing/faq-list";

export function FaqCategoryColumns() {
  return (
    <div className="mx-auto mt-10 grid max-w-6xl gap-10 md:grid-cols-2">
      {FAQ_CATEGORIES.map(({ id, label }) => (
        <section key={id} aria-labelledby={`faq-${id}-heading`}>
          <h2 id={`faq-${id}-heading`} className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            {label}
          </h2>
          <div className="mt-4">
            <FaqList items={FAQ_ITEMS.filter((item) => item.category === id)} />
          </div>
        </section>
      ))}
    </div>
  );
}
