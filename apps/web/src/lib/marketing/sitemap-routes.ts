import { blogSlugs } from "@/content/blog/posts";

/** Public marketing paths included in `app/sitemap.ts`. */
export const MARKETING_SITEMAP_STATIC_ROUTES = [
  "/",
  "/features",
  "/how-it-works",
  "/faq",
  "/pricing",
  "/blog",
  "/privacy",
  "/terms",
  "/acceptable-use",
  "/signup",
  "/login",
] as const;

export function marketingSitemapPaths(): string[] {
  const posts = blogSlugs().map((slug) => `/blog/${slug}`);
  return [...MARKETING_SITEMAP_STATIC_ROUTES, ...posts];
}
