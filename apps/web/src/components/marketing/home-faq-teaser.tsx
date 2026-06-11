import Link from "next/link";

import { FaqList } from "@/components/marketing/faq-list";
import { buttonVariants } from "@/components/ui/button";
import { HOME_FAQ_TEASER } from "@/lib/marketing/content";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function HomeFaqTeaser() {
  return (
    <section aria-labelledby="home-faq-heading" className="px-6 py-20">
      <div className={cn("mx-auto max-w-3xl", motionFadeIn)}>
        <div className="text-center">
          <p className="font-mono text-xs font-medium uppercase tracking-[0.2em] text-accent">
            FAQ
          </p>
          <h2
            id="home-faq-heading"
            className="mt-3 text-3xl font-semibold tracking-[-0.02em] md:text-4xl"
          >
            Common questions
          </h2>
        </div>
        <div className="mt-10">
          <FaqList items={[...HOME_FAQ_TEASER]} />
        </div>
        <p className="mt-8 text-center">
          <Link href="/faq" className={buttonVariants({ variant: "outline", size: "sm" })}>
            Read all FAQ
          </Link>
        </p>
      </div>
    </section>
  );
}
