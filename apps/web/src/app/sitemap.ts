import type { MetadataRoute } from "next";

import { blogSlugs } from "@/content/blog/posts";
import { getSiteUrl } from "@/lib/site";

const staticRoutes = [
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

export default function sitemap(): MetadataRoute.Sitemap {
  const base = getSiteUrl();
  const lastModified = new Date();

  const pages: MetadataRoute.Sitemap = staticRoutes.map((path) => ({
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
