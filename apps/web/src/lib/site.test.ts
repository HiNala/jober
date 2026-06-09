import { afterEach, describe, expect, it } from "vitest";

import { getSiteUrl } from "@/lib/site";

describe("getSiteUrl", () => {
  const originalSite = process.env.NEXT_PUBLIC_SITE_URL;
  const originalVercel = process.env.VERCEL_URL;

  afterEach(() => {
    if (originalSite === undefined) delete process.env.NEXT_PUBLIC_SITE_URL;
    else process.env.NEXT_PUBLIC_SITE_URL = originalSite;
    if (originalVercel === undefined) delete process.env.VERCEL_URL;
    else process.env.VERCEL_URL = originalVercel;
  });

  it("prefers NEXT_PUBLIC_SITE_URL without trailing slash", () => {
    process.env.NEXT_PUBLIC_SITE_URL = "https://jober.app/";
    delete process.env.VERCEL_URL;
    expect(getSiteUrl()).toBe("https://jober.app");
  });

  it("falls back to VERCEL_URL when site URL unset", () => {
    delete process.env.NEXT_PUBLIC_SITE_URL;
    process.env.VERCEL_URL = "jober-preview.vercel.app";
    expect(getSiteUrl()).toBe("https://jober-preview.vercel.app");
  });

  it("defaults to localhost in dev", () => {
    delete process.env.NEXT_PUBLIC_SITE_URL;
    delete process.env.VERCEL_URL;
    expect(getSiteUrl()).toBe("http://localhost:3000");
  });
});
