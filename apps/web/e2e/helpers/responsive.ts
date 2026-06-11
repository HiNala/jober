import { expect, type Page } from "@playwright/test";

/** Document must not scroll horizontally (1px tolerance for subpixel rounding). */
export async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const overflows = await page.evaluate(() => {
    const doc = document.documentElement;
    return doc.scrollWidth > doc.clientWidth + 1;
  });
  expect(overflows, "horizontal body overflow detected").toBe(false);
}

export const VIEWPORTS = {
  phone: { width: 375, height: 812 },
  tablet: { width: 768, height: 1024 },
} as const;
