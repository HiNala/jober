import { describe, expect, it } from "vitest";

import {
  FIRST_APPLY_STEPS,
  stepIsDone,
  walkthroughStats,
  type WalkthroughProgress,
} from "@/lib/onboarding/first-apply-walkthrough";

const empty: WalkthroughProgress = {
  hasJobs: false,
  hasResume: false,
  hasDocuments: false,
  hasRuns: false,
  hasReviewOrSuccess: false,
};

describe("first-apply walkthrough", () => {
  it("has five steps with one optional", () => {
    expect(FIRST_APPLY_STEPS).toHaveLength(5);
    expect(FIRST_APPLY_STEPS.filter((s) => s.optional)).toHaveLength(1);
  });

  it("marks steps from progress flags", () => {
    expect(stepIsDone("add_jobs", empty)).toBe(false);
    expect(stepIsDone("add_jobs", { ...empty, hasJobs: true })).toBe(true);
    expect(stepIsDone("tailor_docs", { ...empty, hasDocuments: true })).toBe(true);
  });

  it("computes required completion", () => {
    const mid = walkthroughStats({
      ...empty,
      hasJobs: true,
      hasResume: true,
    });
    expect(mid.requiredDone).toBe(2);
    expect(mid.allRequiredDone).toBe(false);

    const done = walkthroughStats({
      hasJobs: true,
      hasResume: true,
      hasDocuments: false,
      hasRuns: true,
      hasReviewOrSuccess: true,
    });
    expect(done.allRequiredDone).toBe(true);
  });
});
