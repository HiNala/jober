import { describe, expect, it } from "vitest";

import { exportJobsXlsxUrl } from "@/lib/api/jobs";

describe("jobs api helpers", () => {
  it("builds export URL from API base", () => {
    const url = exportJobsXlsxUrl();
    expect(url).toMatch(/\/api\/exports\/jobs-xlsx$/);
  });
});
