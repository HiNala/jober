import { describe, expect, it } from "vitest";

import {
  BLOG_LEAD,
  DASHBOARD_FIRST_RUN,
  DOCUMENTS_EMPTY_JOBS,
  DOCUMENTS_ERROR_JOBS,
  QUEUE_EMPTY,
  QUEUE_FILTER_EMPTY,
} from "@/lib/states/onboarding-copy";

const DEV_COPY_PATTERN = /\bmake\s+(seed|up)\b/i;

const USER_FACING_COPY = [
  QUEUE_EMPTY.title,
  QUEUE_EMPTY.description,
  QUEUE_FILTER_EMPTY,
  DASHBOARD_FIRST_RUN.title,
  DASHBOARD_FIRST_RUN.description,
  DOCUMENTS_EMPTY_JOBS.title,
  DOCUMENTS_EMPTY_JOBS.description,
  DOCUMENTS_ERROR_JOBS,
  BLOG_LEAD,
];

describe("onboarding copy", () => {
  it("contains no dev-only commands", () => {
    for (const text of USER_FACING_COPY) {
      expect(text).not.toMatch(DEV_COPY_PATTERN);
    }
  });

  it("names a real next action for queue empty state", () => {
    expect(QUEUE_EMPTY.description.toLowerCase()).toContain("upload");
    expect(QUEUE_EMPTY.title.toLowerCase()).toContain("import");
  });
});
