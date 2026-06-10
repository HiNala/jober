import { describe, expect, it } from "vitest";

import { marketingMetadata } from "@/lib/marketing/metadata";

describe("marketingMetadata", () => {
  it("sets canonical path and openGraph url", () => {
    const meta = marketingMetadata({
      title: "FAQ",
      description: "Answers about Jober.",
      path: "/faq",
    });
    expect(meta.alternates?.canonical).toBe("/faq");
    expect(meta.openGraph?.url).toContain("/faq");
    expect(meta.twitter?.title).toBe("FAQ");
  });
});
