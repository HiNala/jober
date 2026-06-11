import type { Metadata } from "next";
import Link from "next/link";

import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { BLOG_POSTS } from "@/content/blog/posts";
import { BLOG_LEAD } from "@/lib/states/onboarding-copy";
import { motionFadeIn } from "@/lib/design/motion";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { marketingMetadata } from "@/lib/marketing/metadata";

export const metadata: Metadata = marketingMetadata({
  title: "Blog & changelog",
  description: "Product updates, launch notes, and changelog entries from the Jober team.",
  path: "/blog",
});

export default function BlogIndexPage() {
  return (
    <MarketingShell signupFeature="blog_header_signup">
      <div className="px-6 py-16 md:py-20">
        <MarketingPageHeader
          eyebrow="Blog"
          title="Updates & changelog"
          lead={BLOG_LEAD}
        />
        <ul className="mx-auto mt-12 max-w-3xl space-y-6">
          {BLOG_POSTS.map((post) => (
            <li key={post.slug}>
              <article
                className={cn(
                  surface.card,
                  "overflow-hidden rounded-xl",
                  motionFadeIn,
                )}
              >
                <div
                  className="h-2 bg-gradient-to-r from-primary/40 via-accent/50 to-primary/20"
                  aria-hidden
                />
                <div className="p-6 md:p-8">
                  <time
                    dateTime={post.publishedAt}
                    className="font-mono text-xs uppercase tracking-wider text-muted-foreground"
                  >
                    {post.publishedAt}
                  </time>
                  <h2 className="mt-3 text-2xl font-semibold tracking-[-0.02em]">
                    <Link href={`/blog/${post.slug}`} className="hover:text-primary">
                      {post.title}
                    </Link>
                  </h2>
                  <p className="mt-3 text-base leading-relaxed text-muted-foreground">
                    {post.summary}
                  </p>
                  <Link
                    href={`/blog/${post.slug}`}
                    className="mt-5 inline-block text-sm font-medium text-primary"
                  >
                    Read more →
                  </Link>
                </div>
              </article>
            </li>
          ))}
        </ul>
      </div>
    </MarketingShell>
  );
}
