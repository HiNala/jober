import type { MetadataRoute } from "next";

import { getSiteUrl } from "@/lib/site";

const routes = ["/", "/pricing", "/privacy", "/terms", "/signup", "/login"] as const;

export default function sitemap(): MetadataRoute.Sitemap {
  const base = getSiteUrl();
  const lastModified = new Date();

  return routes.map((path) => ({
    url: path === "/" ? base : `${base}${path}`,
    lastModified,
    changeFrequency: path === "/" ? "weekly" : "monthly",
    priority: path === "/" ? 1 : 0.6,
  }));
}
