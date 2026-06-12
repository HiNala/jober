import { describe, expect, it } from "vitest";

import {
  BLOG_LEAD,
  DASHBOARD_FIRST_RUN,
  DOCUMENTS_EMPTY_JOBS,
  DOCUMENTS_ERROR_JOBS,
  QUEUE_EMPTY,
  QUEUE_FILTER_EMPTY,
} from "@/lib/states/onboarding-copy";
import {
  PAGE_ERROR_ARIA,
  PAGE_LOADING_ARIA,
  PAGE_SUCCESS_ARIA,
} from "@/lib/states/page-state-contracts";

const EMPTY_STATES = [QUEUE_EMPTY, DASHBOARD_FIRST_RUN, DOCUMENTS_EMPTY_JOBS] as const;

describe("page state accessibility contracts", () => {
  it("loading states expose polite busy status", () => {
    expect(PAGE_LOADING_ARIA).toEqual({ role: "status", live: "polite", busy: true });
  });

  it("error states use alert role", () => {
    expect(PAGE_ERROR_ARIA.role).toBe("alert");
  });

  it("success states use status role", () => {
    expect(PAGE_SUCCESS_ARIA.role).toBe("status");
  });
});

describe("page state copy coverage", () => {
  it("empty states include title and actionable description", () => {
    for (const state of EMPTY_STATES) {
      expect(state.title.length).toBeGreaterThan(3);
      expect(state.description.length).toBeGreaterThan(20);
    }
  });

  it("filter-empty and error strings are user-facing", () => {
    expect(QUEUE_FILTER_EMPTY.toLowerCase()).toContain("filter");
    expect(DOCUMENTS_ERROR_JOBS.toLowerCase()).toContain("try again");
    expect(BLOG_LEAD.length).toBeGreaterThan(10);
  });
});
