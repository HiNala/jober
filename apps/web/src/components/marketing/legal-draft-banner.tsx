import Link from "next/link";

import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function LegalDraftBanner() {
  return (
    <aside
      className={cn(
        surface.card,
        "mb-8 rounded-lg border-amber-500/30 bg-amber-500/5 px-4 py-3 text-sm text-amber-950 dark:text-amber-100",
      )}
      role="note"
    >
      <strong className="font-semibold">Draft — requires legal review before public launch.</strong>{" "}
      This text describes current product behavior but is not final counsel. Contact{" "}
      <Link href="mailto:legal@jober.app" className="underline underline-offset-2">
        legal@jober.app
      </Link>{" "}
      for sign-off.
    </aside>
  );
}
