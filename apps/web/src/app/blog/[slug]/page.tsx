import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { JsonLd } from "@/components/marketing/json-ld";
import { MarketingShell } from "@/components/marketing/marketing-shell";
import { BLOG_POSTS, postBySlug } from "@/content/blog/posts";
import { motionFadeIn } from "@/lib/design/motion";
import { marketingMetadata } from "@/lib/marketing/metadata";
import { getSiteUrl } from "@/lib/site";
import { cn } from "@/lib/utils";

type PageProps = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return BLOG_POSTS.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = postBySlug(slug);
  if (!post) return { title: "Post not found" };
  return marketingMetadata({
    title: post.title,
    description: post.summary,
    path: `/blog/${post.slug}`,
  });
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = postBySlug(slug);
  if (!post) notFound();

  const postUrl = `${getSiteUrl()}/blog/${post.slug}`;

  return (
    <MarketingShell signupFeature="blog_post_header_signup">
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "BlogPosting",
          headline: post.title,
          description: post.summary,
          datePublished: post.publishedAt,
          url: postUrl,
          author: { "@type": "Organization", name: "Jober" },
          publisher: { "@type": "Organization", name: "Jober" },
        }}
      />
      <article className={cn("mx-auto max-w-2xl px-6 py-16", motionFadeIn)}>
        <Link href="/blog" className="text-sm text-muted-foreground hover:text-foreground">
          ← Blog
        </Link>
        <time dateTime={post.publishedAt} className="mt-4 block text-xs text-muted-foreground">
          {post.publishedAt}
        </time>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">{post.title}</h1>
        <p className="mt-4 text-muted-foreground">{post.summary}</p>
        <div className="mt-8 space-y-4 text-sm leading-relaxed text-muted-foreground">
          {post.body.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>
      </article>
    </MarketingShell>
  );
}
