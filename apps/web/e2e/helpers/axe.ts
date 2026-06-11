import AxeBuilder from "@axe-core/playwright";
import type { Page } from "@playwright/test";

/**
 * Shared axe config for Jober e2e.
 * - color-contrast: validated at token level (see 13_a11y_waivers.md)
 * - region: closed dialog portals (command palette) fail best-practice landmark nesting
 */
export function createAxeBuilder(page: Page) {
  return new AxeBuilder({ page }).disableRules(["color-contrast", "region"]);
}
