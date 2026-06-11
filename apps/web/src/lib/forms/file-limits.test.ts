import { describe, expect, it } from "vitest";

import { validateUploadFile } from "@/lib/forms/file-limits";

function file(name: string, size: number): File {
  return new File([new Uint8Array(size)], name);
}

describe("validateUploadFile", () => {
  it("rejects unsupported spreadsheet types", () => {
    expect(validateUploadFile(file("jobs.csv", 100), "spreadsheet")).toContain(".xlsx");
  });

  it("accepts pdf resumes", () => {
    expect(validateUploadFile(file("resume.pdf", 100), "resume")).toBeNull();
  });

  it("rejects oversized resumes", () => {
    expect(validateUploadFile(file("resume.pdf", 11 * 1024 * 1024), "resume")).toContain("under");
  });
});
