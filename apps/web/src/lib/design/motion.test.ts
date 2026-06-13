import { describe, expect, it } from "vitest";

import {
  HERO_STAGGER_MS,
  MOTION_DISTANCE,
  MOTION_MS,
  brandBorderBeam,
  brandStepperConnector,
  motionHeroStagger,
  motionLivePulse,
  motionSkeleton,
  runStatusTone,
} from "@/lib/design/motion";

describe("motion tokens", () => {
  it("keeps micro interactions at or below 200ms", () => {
    expect(MOTION_MS.micro).toBeLessThanOrEqual(200);
    expect(MOTION_MS.fast).toBeLessThanOrEqual(200);
  });

  it("keeps view transitions at or below 500ms", () => {
    expect(MOTION_MS.view).toBeLessThanOrEqual(500);
    expect(MOTION_MS.layout).toBeLessThanOrEqual(500);
    expect(MOTION_MS.max).toBe(500);
  });

  it("uses small transform distances only", () => {
    expect(MOTION_DISTANCE.sm).toBeLessThanOrEqual(8);
    expect(MOTION_DISTANCE.md).toBeLessThanOrEqual(16);
  });

  it("exports brand and micro-interaction tokens", () => {
    expect(brandBorderBeam).toBe("brand-border-beam");
    expect(motionLivePulse).toContain("jober-live-pulse");
    expect(motionSkeleton).toContain("jober-skeleton-shimmer");
    expect(brandStepperConnector).toContain("brand-stepper-connector");
  });

  it("hero stagger uses 50ms steps", () => {
    expect(HERO_STAGGER_MS).toBe(50);
    expect(motionHeroStagger(2)).toContain("100ms");
  });
});

describe("runStatusTone", () => {
  it("maps queued statuses", () => {
    expect(runStatusTone("queued")).toBe("queued");
    expect(runStatusTone("new")).toBe("queued");
  });

  it("maps running statuses", () => {
    expect(runStatusTone("in_progress")).toBe("running");
    expect(runStatusTone("filling_form")).toBe("running");
  });

  it("maps review and submitted", () => {
    expect(runStatusTone("review_and_submit")).toBe("review");
    expect(runStatusTone("applied")).toBe("submitted");
  });
});
