import type { MetadataRoute } from "next";

import { blogSlugs } from "@/content/blog/posts";
import { MARKETING_SITEMAP_STATIC_ROUTES } from "@/lib/marketing/sitemap-routes";
import { getSiteUrl } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = getSiteUrl();
  const lastModified = new Date();

  const pages: MetadataRoute.Sitemap = MARKETING_SITEMAP_STATIC_ROUTES.map((path) => ({
    url: path === "/" ? base : `${base}${path}`,
    lastModified,
    changeFrequency: path === "/" || path === "/blog" ? "weekly" : "monthly",
    priority: path === "/" ? 1 : path === "/pricing" ? 0.9 : 0.7,
  }));

  const posts: MetadataRoute.Sitemap = blogSlugs().map((slug) => ({
    url: `${base}/blog/${slug}`,
    lastModified,
    changeFrequency: "monthly",
    priority: 0.5,
  }));

  return [...pages, ...posts];
}
