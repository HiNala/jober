import { describe, expect, it } from "vitest";

import {
  formatBatchExclusionReason,
  JOB_STATUS_LABEL,
  JOB_STATUS_OPTIONS,
} from "@/lib/jobs/status-vocabulary";

describe("status-vocabulary", () => {
  it("covers every job status with a human label", () => {
    for (const status of JOB_STATUS_OPTIONS) {
      expect(JOB_STATUS_LABEL[status].length).toBeGreaterThan(0);
    }
  });

  it("maps batch exclusion reasons to readable copy", () => {
    expect(formatBatchExclusionReason("already_applied")).toContain("applied");
    expect(formatBatchExclusionReason("custom_reason")).toBe("custom reason");
  });
});
