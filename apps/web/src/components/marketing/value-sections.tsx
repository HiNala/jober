import { VALUE_PROPS } from "@/lib/marketing/content";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function ValueSections() {
  return (
    <section aria-labelledby="value-heading" className="px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-accent">Why Jober</p>
          <h2 id="value-heading" className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
            Quality applications, visible process
          </h2>
        </div>

        <ul className="mt-12 grid gap-4 md:grid-cols-2">
          {VALUE_PROPS.map(({ icon: Icon, title, body }) => (
            <li
              key={title}
              className={cn(surface.card, "flex gap-4 rounded-lg p-5", motionFadeIn)}
            >
              <Icon className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
              <div>
                <h3 className="text-base font-semibold">{title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{body}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
