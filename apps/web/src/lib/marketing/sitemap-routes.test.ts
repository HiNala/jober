import { describe, expect, it } from "vitest";

import { marketingSitemapPaths } from "@/lib/marketing/sitemap-routes";

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
});
