import { Activity, Clock3, FileCheck2, Radar } from "lucide-react";

import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const values = [
  {
    icon: Clock3,
    title: "Hours back, not hidden automation",
    body: "Batch prep, mapping, and uploads run while you focus on choosing the right roles — not retyping the same answers.",
  },
  {
    icon: FileCheck2,
    title: "ATS-quality materials",
    body: "Cover letters and attachments follow your voice presets and ATS-safe formatting. Claims stay grounded in your vault.",
  },
  {
    icon: Radar,
    title: "Tracking you can trust",
    body: "Every run, checkpoint, and submit is logged in your workspace. Know exactly what was sent and when.",
  },
  {
    icon: Activity,
    title: "Live watch, calm console",
    body: "Stream events and screenshots in the run console. When something needs you, the UI says so — plainly.",
  },
] as const;

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
          {values.map(({ icon: Icon, title, body }) => (
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
