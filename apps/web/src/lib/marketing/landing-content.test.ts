import { describe, expect, it } from "vitest";

import {
  FOUNDER_PROOF,
  HOME_FAQ_TEASER,
  LANDING_TRUST_ITEMS,
  POSITIONING_ONE_LINER,
} from "@/lib/marketing/content";

describe("landing content", () => {
  it("implements positioning audit §17 one-liner", () => {
    expect(POSITIONING_ONE_LINER).toContain("You review and submit");
    expect(POSITIONING_ONE_LINER).toContain("quality bar");
  });

  it("trust strip matches §18 commitments", () => {
    expect(LANDING_TRUST_ITEMS).toContain("Review before submit");
    expect(LANDING_TRUST_ITEMS).toContain("BYOK supported");
  });

  it("has no placeholder testimonial quotes on home", () => {
    expect(FOUNDER_PROOF.story).not.toMatch(/early design partner|private beta user/i);
    expect(FOUNDER_PROOF.stats.length).toBeGreaterThanOrEqual(3);
  });

  it("faq teaser leads with bot/objection questions", () => {
    expect(HOME_FAQ_TEASER[0]?.question.toLowerCase()).toContain("bot");
  });
});
