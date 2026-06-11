import { describe, expect, it } from "vitest";

import { MARKETING_A11Y_ROUTES } from "../../../e2e/marketing-routes";
import {
  MARKETING_SITEMAP_STATIC_ROUTES,
  marketingSitemapPaths,
} from "@/lib/marketing/sitemap-routes";

describe("marketingSitemapPaths", () => {
  it("includes all M30 public marketing routes and blog slugs", () => {
    const paths = marketingSitemapPaths();
    expect(paths).toEqual(
      expect.arrayContaining([
        "/",
        "/features",
        "/how-it-works",
        "/faq",
        "/pricing",
        "/acceptable-use",
        "/blog/welcome-to-jober",
      ]),
    );
  });

  it("excludes dev-only kitchen sink from sitemap", () => {
    expect(marketingSitemapPaths()).not.toContain("/kitchen-sink");
  });

  it("includes every Playwright a11y marketing route", () => {
    const staticPaths = new Set<string>(MARKETING_SITEMAP_STATIC_ROUTES);
    for (const path of MARKETING_A11Y_ROUTES) {
      expect(staticPaths, `missing sitemap entry for ${path}`).toContain(path);
    }
  });
});
