import type { Metadata } from "next";
import Link from "next/link";

import { MarketingPageHeader } from "@/components/marketing/marketing-page-header";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { BLOG_POSTS } from "@/content/blog/posts";
import { BLOG_LEAD } from "@/lib/states/onboarding-copy";
import { motionFadeIn } from "@/lib/design/motion";
import { marketingMetadata } from "@/lib/marketing/metadata";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export const metadata: Metadata = marketingMetadata({
  title: "Blog & changelog",
  description: "Product updates, launch notes, and changelog entries from the Jober team.",
  path: "/blog",
});

export default function BlogIndexPage() {
  return (
    <MarketingShell signupFeature="blog_header_signup">
      <div className="px-6 py-16">
        <MarketingPageHeader
          eyebrow="Blog"
          title="Updates & changelog"
          lead={BLOG_LEAD}
        />
        <ul className="mx-auto mt-12 max-w-3xl space-y-4">
          {BLOG_POSTS.map((post) => (
            <li key={post.slug}>
              <article className={cn(surface.card, "rounded-xl p-6", motionFadeIn)}>
                <time dateTime={post.publishedAt} className="text-xs text-muted-foreground">
                  {post.publishedAt}
                </time>
                <h2 className="mt-2 text-lg font-semibold">
                  <Link href={`/blog/${post.slug}`} className="hover:text-primary">
                    {post.title}
                  </Link>
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">{post.summary}</p>
                <Link
                  href={`/blog/${post.slug}`}
                  className="mt-3 inline-block text-sm font-medium text-primary"
                >
                  Read more →
                </Link>
              </article>
            </li>
          ))}
        </ul>
      </div>
    </MarketingShell>
  );
}
