import { describe, expect, it } from "vitest";

import { MARKETING_SITEMAP_STATIC_ROUTES } from "@/lib/marketing/sitemap-routes";
import { ROBOTS_DISALLOW_PATHS } from "@/lib/marketing/seo";

describe("marketing SEO paths", () => {
  it("does not sitemap workspace routes blocked in robots", () => {
    for (const blocked of ROBOTS_DISALLOW_PATHS) {
      for (const listed of MARKETING_SITEMAP_STATIC_ROUTES) {
        expect(listed).not.toBe(blocked);
        expect(listed.startsWith(`${blocked}/`)).toBe(false);
      }
    }
  });
});
